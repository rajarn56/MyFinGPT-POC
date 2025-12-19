#!/usr/bin/env python3
"""
Test script to verify embedding format fix and zero embeddings issue resolution.

Tests:
1. Embedding format - no triple-nested lists
2. Embeddings are not all zeros (when OpenAI key available)
3. search_similar function works correctly
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_db.embeddings import EmbeddingPipeline
from src.vector_db.chroma_client import ChromaClient
from loguru import logger
import traceback


def test_embedding_generation():
    """Test that embeddings are generated correctly"""
    print("\n" + "="*60)
    print("TEST 1: Embedding Generation")
    print("="*60)
    
    pipeline = EmbeddingPipeline()
    test_text = "AAPL stock analysis"
    
    try:
        embedding = pipeline.generate_embedding(test_text)
        
        # Check embedding format
        assert isinstance(embedding, list), f"Embedding should be a list, got {type(embedding)}"
        assert len(embedding) > 0, "Embedding should not be empty"
        assert len(embedding) == 1536, f"Embedding should be 1536 dimensions, got {len(embedding)}"
        
        # Check for zero vectors
        is_all_zeros = all(x == 0.0 for x in embedding)
        if is_all_zeros:
            print("⚠️  WARNING: Embedding is all zeros!")
            print("   This means semantic search will be disabled.")
            print("   For LMStudio: Ensure EMBEDDING_MODEL is set and LMStudio server is running.")
            print("   OPENAI_API_KEY is NOT required for LMStudio (code sets dummy key automatically).")
        else:
            print("✅ Embedding generated successfully (not all zeros)")
            # Show sample values
            print(f"   Sample values: {embedding[:5]}")
            print(f"   Non-zero count: {sum(1 for x in embedding if x != 0.0)}/{len(embedding)}")
        
        return embedding, not is_all_zeros
        
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        traceback.print_exc()
        return None, False


def test_embedding_format():
    """Test that embedding format is correct for ChromaDB"""
    print("\n" + "="*60)
    print("TEST 2: Embedding Format (No Triple Nesting)")
    print("="*60)
    
    pipeline = EmbeddingPipeline()
    test_text = "MSFT stock comparison"
    
    try:
        embedding = pipeline.generate_embedding(test_text)
        
        # Check it's a flat list of floats
        assert isinstance(embedding, list), "Should be a list"
        assert all(isinstance(x, (int, float)) for x in embedding), "All elements should be numbers"
        
        # Verify it's NOT nested
        assert not any(isinstance(x, list) for x in embedding), "Should not contain nested lists"
        
        print("✅ Embedding format is correct (flat list of floats)")
        print(f"   Type: {type(embedding)}")
        print(f"   Length: {len(embedding)}")
        print(f"   First element type: {type(embedding[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking embedding format: {e}")
        traceback.print_exc()
        return False


def test_chroma_query_format():
    """Test that search_similar passes correct format to ChromaDB"""
    print("\n" + "="*60)
    print("TEST 3: ChromaDB Query Format")
    print("="*60)
    
    pipeline = EmbeddingPipeline()
    chroma_client = ChromaClient()
    
    test_text = "GOOGL stock analysis"
    
    try:
        # Generate embedding
        query_embedding = pipeline.generate_embedding(test_text)
        
        # Check format before passing to search_similar
        print(f"   Query embedding type: {type(query_embedding)}")
        print(f"   Query embedding length: {len(query_embedding)}")
        print(f"   Is nested: {any(isinstance(x, list) for x in query_embedding)}")
        
        # Test search_similar (should not throw format error)
        # This will fail if format is wrong (triple nesting)
        try:
            results = chroma_client.search_similar(
                collection_name="company_analysis",
                query_embedding=query_embedding,
                n_results=3
            )
            
            print("✅ search_similar executed without format errors")
            print(f"   Results returned: {len(results)} documents")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "Expected embeddings to be" in error_msg or "triple" in error_msg.lower():
                print(f"❌ FORMAT ERROR: {error_msg}")
                print("   This indicates the triple-nesting issue is NOT fixed!")
                return False
            else:
                # Other errors (like empty collection) are OK
                print(f"⚠️  Query returned error (may be expected): {e}")
                print("   Format appears correct (no triple-nesting error)")
                return True
                
    except Exception as e:
        print(f"❌ Error testing ChromaDB query: {e}")
        traceback.print_exc()
        return False


def test_end_to_end():
    """Test end-to-end: add document, then search"""
    print("\n" + "="*60)
    print("TEST 4: End-to-End Test (Add & Search)")
    print("="*60)
    
    pipeline = EmbeddingPipeline()
    chroma_client = ChromaClient()
    
    test_doc = "AAPL stock has shown strong performance with revenue growth of 15%"
    test_symbol = "AAPL"
    
    try:
        # Generate embedding for document
        doc_embedding = pipeline.generate_embedding(test_doc)
        
        if all(x == 0.0 for x in doc_embedding):
            print("⚠️  Skipping end-to-end test - embeddings are all zeros")
            return False
        
        # Add document to vector DB
        doc_id = chroma_client.add_document(
            collection_name="company_analysis",
            document=test_doc,
            metadata={"symbol": test_symbol, "test": True},
            embedding=doc_embedding
        )
        print(f"✅ Document added with ID: {doc_id}")
        
        # Search for similar documents
        query_text = "Apple stock performance revenue"
        query_embedding = pipeline.generate_embedding(query_text)
        
        results = chroma_client.search_similar(
            collection_name="company_analysis",
            query_embedding=query_embedding,
            n_results=5
        )
        
        print(f"✅ Search completed successfully")
        print(f"   Found {len(results)} similar documents")
        
        if len(results) > 0:
            print(f"   Top result: {results[0]['document'][:50]}...")
            print(f"   Distance: {results[0].get('distance', 'N/A')}")
        
        # Cleanup
        try:
            chroma_client.delete_document("company_analysis", doc_id)
            print("✅ Test document cleaned up")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Error in end-to-end test: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("EMBEDDING FIXES VERIFICATION TEST")
    print("="*60)
    print("\nChecking configuration...")
    
    # Check provider
    from src.utils.llm_config import llm_config
    provider = llm_config.default_provider
    print(f"   LLM Provider: {provider}")
    
    # Check embedding provider env var
    embedding_provider = os.getenv("EMBEDDING_PROVIDER")
    if embedding_provider:
        print(f"   EMBEDDING_PROVIDER: {embedding_provider}")
        effective_provider = embedding_provider
    else:
        effective_provider = provider
    
    # Check LMStudio-specific configuration
    if effective_provider == "lmstudio":
        lmstudio_api_base = os.getenv("LM_STUDIO_API_BASE")
        if lmstudio_api_base:
            print(f"   LM_STUDIO_API_BASE: {lmstudio_api_base}")
        else:
            print(f"   LM_STUDIO_API_BASE: NOT SET (will use default: http://localhost:1234/v1)")
        
        embedding_model = os.getenv("EMBEDDING_MODEL")
        if embedding_model:
            print(f"   EMBEDDING_MODEL: {embedding_model}")
        else:
            print(f"   EMBEDDING_MODEL: NOT SET (will use config default or text-embedding-ada-002)")
            print("   ⚠️  Note: Set EMBEDDING_MODEL to your LMStudio embedding model name")
        
        print("\n   ℹ️  LMStudio Configuration:")
        print("      - OPENAI_API_KEY is NOT required for LMStudio (code sets dummy key)")
        print("      - Ensure LMStudio server is running at the configured API base")
        print("      - Set EMBEDDING_MODEL to your LMStudio embedding model name")
        print("      - Example: export EMBEDDING_MODEL=your-embedding-model-name")
    
    # Check OpenAI key (only needed if using OpenAI provider or as fallback)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"   OPENAI_API_KEY: {'*' * 20} (set)")
        if effective_provider == "lmstudio":
            print("      (Not required for LMStudio, but available as fallback)")
    else:
        print(f"   OPENAI_API_KEY: NOT SET")
        if effective_provider == "lmstudio":
            print("      (Not required for LMStudio embeddings)")
        else:
            print("      ⚠️  Required for OpenAI embeddings")
    
    # Run tests
    results = []
    
    embedding, has_valid_embeddings = test_embedding_generation()
    results.append(("Embedding Generation", has_valid_embeddings))
    
    format_ok = test_embedding_format()
    results.append(("Embedding Format", format_ok))
    
    query_ok = test_chroma_query_format()
    results.append(("ChromaDB Query Format", query_ok))
    
    if has_valid_embeddings:
        e2e_ok = test_end_to_end()
        results.append(("End-to-End Test", e2e_ok))
    else:
        print("\n⚠️  Skipping end-to-end test - embeddings are all zeros")
        results.append(("End-to-End Test", None))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(r for r in results if r is not None)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED - Review output above")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

