#!/usr/bin/env python3
"""
Chroma Vector Database Connectivity Test Script

Tests connectivity and basic operations with Chroma vector database.

Uses the same Python virtual environment and .env configuration as the POC.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file (same as POC)
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env")

try:
    import chromadb
    from chromadb.config import Settings
    from datetime import datetime
    print("✓ chromadb library imported successfully")
except ImportError as e:
    print(f"✗ Failed to import chromadb: {e}")
    print("  Install with: pip install chromadb>=0.4.22")
    sys.exit(1)


def test_chroma_connectivity():
    """Test Chroma vector database connectivity"""
    print("\n" + "="*60)
    print("Chroma Vector Database Connectivity Test")
    print("="*60)
    
    # Get database path from .env file
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    test_db_path = os.path.join(db_path, "test_connectivity")
    print(f"  (CHROMA_DB_PATH from .env: {db_path})")
    
    print(f"\n1. Testing Chroma client initialization...")
    try:
        # Create directory if it doesn't exist
        Path(test_db_path).mkdir(parents=True, exist_ok=True)
        
        client = chromadb.PersistentClient(
            path=test_db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print(f"  ✓ Success: Chroma client initialized")
        print(f"    Database path: {test_db_path}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n2. Testing collection creation...")
    try:
        collection_name = "test_collection"
        collection = client.get_or_create_collection(name=collection_name)
        print(f"  ✓ Success: Collection '{collection_name}' created/retrieved")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n3. Testing document addition...")
    try:
        test_documents = [
            "This is a test document for Chroma connectivity testing.",
            "Financial data analysis requires vector search capabilities.",
            "Chroma provides efficient semantic search for embeddings."
        ]
        test_metadatas = [
            {"source": "test", "type": "connectivity"},
            {"source": "test", "type": "connectivity"},
            {"source": "test", "type": "connectivity"}
        ]
        test_ids = ["test_doc_1", "test_doc_2", "test_doc_3"]
        
        collection.add(
            documents=test_documents,
            metadatas=test_metadatas,
            ids=test_ids
        )
        print(f"  ✓ Success: Added {len(test_documents)} test documents")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n4. Testing document query...")
    try:
        results = collection.query(
            query_texts=["test document"],
            n_results=2
        )
        
        if results and results.get("ids") and len(results["ids"][0]) > 0:
            print(f"  ✓ Success: Retrieved {len(results['ids'][0])} documents")
            print(f"    First result ID: {results['ids'][0][0]}")
        else:
            print(f"  ⚠ Warning: Query returned no results")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n5. Testing collection count...")
    try:
        count = collection.count()
        print(f"  ✓ Success: Collection contains {count} documents")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n6. Testing collection deletion...")
    try:
        client.delete_collection(name=collection_name)
        print(f"  ✓ Success: Test collection deleted")
    except Exception as e:
        print(f"  ⚠ Warning: Could not delete collection: {e}")
        # Not critical, continue
    
    # Clean up test database directory
    try:
        import shutil
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
            print(f"  ✓ Success: Test database directory cleaned up")
    except Exception as e:
        print(f"  ⚠ Warning: Could not clean up test directory: {e}")
    
    return True


def main():
    """Main test function"""
    print("\nStarting Chroma vector database connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_chroma_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ Chroma vector database connectivity test PASSED")
        print("\nChroma is accessible and working correctly.")
        print("Note: Database will be created at CHROMA_DB_PATH (default: ./chroma_db)")
    else:
        print("✗ Chroma vector database connectivity test FAILED")
        print("\nPlease check:")
        print("  - chromadb library installation: pip install chromadb>=0.4.22")
        print(f"  - CHROMA_DB_PATH is set correctly in .env file at: {project_root / '.env'}")
        print("  - Write permissions for database directory")
        print("  - Disk space availability")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

