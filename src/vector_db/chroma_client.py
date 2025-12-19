"""Chroma vector database client for MyFinGPT"""

import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import time
import hashlib
import json
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


class ChromaClient:
    """Chroma vector database client with collections for financial data"""
    
    def __init__(self, db_path: Optional[str] = None, persist_directory: Optional[str] = None, 
                 embedding_dimension: Optional[int] = None):
        """
        Initialize Chroma client
        
        Args:
            db_path: Path to database (defaults to ./chroma_db)
            persist_directory: Persistence directory (same as db_path if not specified)
            embedding_dimension: Expected embedding dimension. If provided, collections will be
                                recreated if they have a different dimension.
        """
        if db_path is None:
            db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        
        if persist_directory is None:
            persist_directory = db_path
        
        logger.info(f"[VectorDB] Initializing Chroma client | Path: {persist_directory}")
        
        # Create directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"[VectorDB] Database directory ensured: {persist_directory}")
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        logger.debug("[VectorDB] Chroma PersistentClient created")
        
        # Store expected embedding dimension
        self.expected_dimension = embedding_dimension
        
        # Initialize collections
        logger.debug("[VectorDB] Initializing collections...")
        self.collections = {
            "financial_news": self._get_or_create_collection("financial_news"),
            "company_analysis": self._get_or_create_collection("company_analysis"),
            "market_trends": self._get_or_create_collection("market_trends"),
        }
        
        # Initialize query cache
        self.query_cache: Dict[str, tuple] = {}  # {query_hash: (results, timestamp)}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
        logger.info(f"[VectorDB] Chroma client initialized | Collections: {list(self.collections.keys())}")
    
    def _get_or_create_collection(self, name: str):
        """
        Get or create a collection, handling dimension mismatches.
        
        If a collection exists with a different dimension than expected, it will be recreated.
        """
        try:
            collection = self.client.get_collection(name=name)
            
            # Check if we need to validate dimension
            if self.expected_dimension is not None:
                # Try to detect collection dimension by checking metadata or peeking at data
                # ChromaDB doesn't expose dimension directly, so we check on first add/query
                # For now, we'll let it fail on mismatch and handle it in add_document/query
                pass
            
            return collection
        except Exception:
            # Collection doesn't exist, create it
            # Note: ChromaDB will infer dimension from first embedding if not specified
            return self.client.create_collection(name=name)
    
    def _recreate_collection_if_dimension_mismatch(self, collection_name: str, embedding: List[float]):
        """
        Recreate collection if dimension mismatch is detected.
        
        Args:
            collection_name: Name of the collection
            embedding: Embedding vector to check dimension
            
        Returns:
            Collection (possibly recreated)
        """
        if not embedding or len(embedding) == 0:
            return self.get_collection(collection_name)
        
        actual_dimension = len(embedding)
        
        # Check if collection exists and has wrong dimension
        try:
            collection = self.client.get_collection(name=collection_name)
            
            # If collection is empty, we can safely recreate it
            if collection.count() == 0:
                logger.debug(f"[VectorDB] Collection {collection_name} is empty, recreating with dimension {actual_dimension}")
                try:
                    self.client.delete_collection(name=collection_name)
                except:
                    pass
                collection = self.client.create_collection(name=collection_name)
                self.collections[collection_name] = collection
                return collection
            
            # Collection has documents - try to detect dimension mismatch by attempting to add
            # We'll catch dimension errors and recreate if needed
            try:
                # This will fail if dimension mismatch
                collection.add(
                    ids=["_dimension_test"],
                    documents=["test"],
                    metadatas=[{}],
                    embeddings=[embedding]
                )
                # If successful, delete test document
                collection.delete(ids=["_dimension_test"])
                return collection
            except Exception as e:
                error_msg = str(e).lower()
                if "dimension" in error_msg or "embedding" in error_msg or "expected" in error_msg:
                    logger.warning(f"[VectorDB] Dimension mismatch detected for {collection_name}: "
                                 f"collection expects different dimension. Recreating collection...")
                    # Delete old collection (this will lose existing data, but dimension mismatch makes it unusable)
                    try:
                        self.client.delete_collection(name=collection_name)
                    except:
                        pass
                    # Create new collection (dimension will be set by first embedding)
                    collection = self.client.create_collection(name=collection_name)
                    logger.info(f"[VectorDB] Recreated collection {collection_name} with dimension {actual_dimension}")
                    # Update cached collection
                    self.collections[collection_name] = collection
                    return collection
                else:
                    # Some other error, re-raise
                    raise
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(name=collection_name)
            self.collections[collection_name] = collection
            return collection
    
    def get_collection(self, collection_name: str):
        """Get a collection by name"""
        if collection_name not in self.collections:
            self.collections[collection_name] = self._get_or_create_collection(collection_name)
        return self.collections[collection_name]
    
    def add_document(self, collection_name: str, document: str, metadata: Dict[str, Any],
                    document_id: Optional[str] = None, embedding: Optional[List[float]] = None):
        """
        Add a document to a collection
        
        Args:
            collection_name: Name of the collection
            document: Document text
            metadata: Metadata dictionary
            document_id: Optional document ID (auto-generated if None)
            embedding: Optional embedding vector (will be generated if None)
        """
        doc_length = len(document)
        symbol = metadata.get("symbol", "unknown")
        logger.debug(f"[VectorDB] Adding document to {collection_name} | "
                   f"Symbol: {symbol} | "
                   f"Length: {doc_length} chars | "
                   f"Has embedding: {embedding is not None}")
        
        collection = self.get_collection(collection_name)
        
        # Add timestamp if not present
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()

        # Chroma metadata must not contain None values and must be simple types.
        # Clean and normalize metadata before sending to Chroma to avoid
        # TypeError: 'NoneType' object cannot be converted to 'Py*' errors.
        clean_metadata: Dict[str, Any] = {}
        for key, value in metadata.items():
            if value is None:
                # Drop keys with None values
                continue
            # Allow basic JSON-serializable scalar types directly
            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            else:
                # Fallback: store string representation
                clean_metadata[key] = str(value)
        
        # Generate ID if not provided
        if document_id is None:
            document_id = f"{collection_name}_{datetime.now().timestamp()}"
        
        # Add document
        try:
            if embedding:
                # Ensure collection has correct dimension (recreate if mismatch)
                collection = self._recreate_collection_if_dimension_mismatch(collection_name, embedding)
                
                collection.add(
                    ids=[document_id],
                    documents=[document],
                    metadatas=[clean_metadata],
                    embeddings=[embedding]
                )
            else:
                collection.add(
                    ids=[document_id],
                    documents=[document],
                    metadatas=[clean_metadata]
                )
            
            logger.info(f"[VectorDB] Document added successfully | "
                       f"Collection: {collection_name} | "
                       f"ID: {document_id} | "
                       f"Symbol: {symbol}")
            return document_id
        except Exception as e:
            logger.error(f"[VectorDB] Error adding document to {collection_name}: {e}", exc_info=True)
            raise
    
    def _hash_query(self, collection_name: str, query_text: str = "",
                   query_embeddings: Optional[List[float]] = None,
                   n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate hash for query caching
        
        Args:
            collection_name: Collection name
            query_text: Query text
            query_embeddings: Query embeddings
            n_results: Number of results
            where: Metadata filter
        
        Returns:
            Query hash string
        """
        query_data = {
            "collection": collection_name,
            "query_text": query_text,
            "query_embeddings": str(query_embeddings) if query_embeddings else None,
            "n_results": n_results,
            "where": json.dumps(where, sort_keys=True) if where else None
        }
        query_str = json.dumps(query_data, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def query(self, collection_name: str, query_text: str = "", n_results: int = 5,
             query_embeddings: Optional[List[float]] = None,
             where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query a collection with caching
        
        Args:
            collection_name: Name of the collection
            query_text: Query text
            n_results: Number of results to return
            query_embeddings: Optional query embedding
            where: Optional metadata filter
        
        Returns:
            Query results dictionary
        """
        start_time = time.time()
        query_preview = query_text[:50] if query_text else "embedding-based"
        
        # Generate query hash
        query_hash = self._hash_query(collection_name, query_text, query_embeddings, n_results, where)
        
        # Check cache
        if query_hash in self.query_cache:
            results, timestamp = self.query_cache[query_hash]
            if time.time() - timestamp < self.cache_ttl:
                elapsed = time.time() - start_time
                result_count = len(results.get("ids", [[]])[0]) if results.get("ids") else 0
                logger.debug(f"[VectorDB] Using cached query result | "
                           f"Collection: {collection_name} | "
                           f"Results: {result_count} | "
                           f"Time: {elapsed:.4f}s")
                return results
            else:
                # Expired - remove from cache
                del self.query_cache[query_hash]
        
        logger.debug(f"[VectorDB] Querying {collection_name} | "
                   f"Query: {query_preview}... | "
                   f"n_results: {n_results} | "
                   f"Has embedding: {query_embeddings is not None}")
        
        collection = self.get_collection(collection_name)
        
        try:
            if query_embeddings:
                # Ensure collection has correct dimension (recreate if mismatch)
                collection = self._recreate_collection_if_dimension_mismatch(collection_name, query_embeddings)
                
                results = collection.query(
                    query_embeddings=[query_embeddings],
                    n_results=n_results,
                    where=where
                )
            else:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where
                )
            
            # Cache results
            self.query_cache[query_hash] = (results, time.time())
            
            elapsed = time.time() - start_time
            result_count = len(results.get("ids", [[]])[0]) if results.get("ids") else 0
            logger.info(f"[VectorDB] Query completed | "
                       f"Collection: {collection_name} | "
                       f"Results: {result_count} | "
                       f"Time: {elapsed:.2f}s")
            return results
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[VectorDB] Query failed after {elapsed:.2f}s: {e}", exc_info=True)
            raise
    
    def search_similar(self, collection_name: str, query_embedding: List[float],
                      n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using embedding
        
        Args:
            collection_name: Name of the collection
            query_embedding: Query embedding vector
            n_results: Number of results
            where: Optional metadata filter
        
        Returns:
            List of similar documents with metadata
        """
        results = self.query(
            collection_name=collection_name,
            query_text="",
            n_results=n_results,
            query_embeddings=query_embedding,  # Pass directly, query() will wrap it
            where=where
        )
        
        # Format results
        formatted_results = []
        if results.get("ids") and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })
        
        return formatted_results
    
    def delete_document(self, collection_name: str, document_id: str):
        """Delete a document from a collection"""
        collection = self.get_collection(collection_name)
        collection.delete(ids=[document_id])
    
    def update_document(self, collection_name: str, document_id: str, document: str = None,
                       metadata: Dict[str, Any] = None):
        """Update a document in a collection"""
        collection = self.get_collection(collection_name)
        
        # Chroma doesn't have direct update, so we delete and re-add
        collection.delete(ids=[document_id])
        
        # Get existing document if needed
        existing = collection.get(ids=[document_id])
        if existing.get("documents"):
            doc_text = document or existing["documents"][0]
            doc_metadata = metadata or existing.get("metadatas", [{}])[0]
        else:
            doc_text = document
            doc_metadata = metadata or {}
        
        self.add_document(collection_name, doc_text, doc_metadata, document_id)
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics about a collection"""
        collection = self.get_collection(collection_name)
        count = collection.count()
        return {
            "name": collection_name,
            "count": count
        }
    
    def reset_collection(self, collection_name: str):
        """Reset (clear) a collection"""
        try:
            self.client.delete_collection(name=collection_name)
            self.collections[collection_name] = self._get_or_create_collection(collection_name)
        except Exception as e:
            print(f"Error resetting collection {collection_name}: {e}")

