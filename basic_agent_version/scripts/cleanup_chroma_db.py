#!/usr/bin/env python3
"""
ChromaDB Cleanup Script

Cleans up all data stored in ChromaDB by the MyFinGPT application.
After running this script, the database will be empty (no collections or documents).

Usage:
    python scripts/cleanup_chroma_db.py [--delete-dir]

Options:
    --delete-dir    Also delete the entire database directory (default: only clears collections)
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file (same as POC)
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env")

try:
    import chromadb
    from chromadb.config import Settings
    print("✓ chromadb library imported successfully")
except ImportError as e:
    print(f"✗ Failed to import chromadb: {e}")
    print("  Install with: pip install chromadb>=0.4.22")
    sys.exit(1)


def get_collection_stats(client):
    """Get statistics for all collections"""
    stats = []
    try:
        collections = client.list_collections()
        for collection in collections:
            count = collection.count()
            stats.append({
                "name": collection.name,
                "count": count
            })
    except Exception as e:
        print(f"  ⚠ Warning: Could not list collections: {e}")
    return stats


def cleanup_chroma_db(delete_directory=False):
    """Clean up ChromaDB data"""
    print("\n" + "="*60)
    print("ChromaDB Cleanup Script")
    print("="*60)
    
    # Get database path from .env file
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    # Resolve relative paths
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
    db_path = os.path.abspath(db_path)
    
    print(f"\nDatabase path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"\n✓ Database directory does not exist: {db_path}")
        print("  Nothing to clean up.")
        return True
    
    print(f"\n1. Connecting to ChromaDB...")
    try:
        client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print(f"  ✓ Successfully connected to ChromaDB")
    except Exception as e:
        print(f"  ✗ Failed to connect: {e}")
        return False
    
    print(f"\n2. Listing existing collections...")
    try:
        collections = client.list_collections()
        if not collections:
            print(f"  ✓ No collections found. Database is already empty.")
        else:
            print(f"  ✓ Found {len(collections)} collection(s):")
            for collection in collections:
                count = collection.count()
                print(f"    - {collection.name}: {count} document(s)")
    except Exception as e:
        print(f"  ✗ Failed to list collections: {e}")
        return False
    
    if not collections:
        # If no collections, optionally delete directory
        if delete_directory:
            print(f"\n3. Deleting database directory...")
            try:
                shutil.rmtree(db_path)
                print(f"  ✓ Successfully deleted database directory: {db_path}")
            except Exception as e:
                print(f"  ✗ Failed to delete directory: {e}")
                return False
        return True
    
    print(f"\n3. Deleting collections...")
    deleted_count = 0
    failed_collections = []
    
    for collection in collections:
        try:
            collection_name = collection.name
            doc_count = collection.count()
            client.delete_collection(name=collection_name)
            print(f"  ✓ Deleted collection '{collection_name}' ({doc_count} document(s))")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗ Failed to delete collection '{collection.name}': {e}")
            failed_collections.append(collection.name)
    
    if failed_collections:
        print(f"\n  ⚠ Warning: Failed to delete {len(failed_collections)} collection(s): {failed_collections}")
        return False
    
    print(f"\n  ✓ Successfully deleted {deleted_count} collection(s)")
    
    # Verify cleanup
    print(f"\n4. Verifying cleanup...")
    try:
        remaining_collections = client.list_collections()
        if remaining_collections:
            print(f"  ⚠ Warning: {len(remaining_collections)} collection(s) still exist:")
            for coll in remaining_collections:
                print(f"    - {coll.name}")
            return False
        else:
            print(f"  ✓ Verification passed: No collections remaining")
    except Exception as e:
        print(f"  ⚠ Warning: Could not verify cleanup: {e}")
    
    # Optionally delete the entire directory
    if delete_directory:
        print(f"\n5. Deleting database directory...")
        try:
            # Close client before deleting directory
            del client
            shutil.rmtree(db_path)
            print(f"  ✓ Successfully deleted database directory: {db_path}")
        except Exception as e:
            print(f"  ✗ Failed to delete directory: {e}")
            print(f"  Note: Collections are deleted, but directory remains.")
            return False
    
    return True


def main():
    """Main cleanup function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up ChromaDB data stored by MyFinGPT application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear all collections (keeps directory)
  python scripts/cleanup_chroma_db.py
  
  # Clear collections and delete directory
  python scripts/cleanup_chroma_db.py --delete-dir
        """
    )
    parser.add_argument(
        "--delete-dir",
        action="store_true",
        help="Also delete the entire database directory (default: only clears collections)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("ChromaDB Cleanup Script")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    if args.delete_dir:
        print("\n⚠ WARNING: This will delete ALL data including the database directory.")
        print("   The database will be completely removed and recreated on next use.")
    else:
        print("\n⚠ WARNING: This will delete ALL collections and documents.")
        print("   The database directory will remain but will be empty.")
    
    response = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\nCleanup cancelled.")
        return 0
    
    success = cleanup_chroma_db(delete_directory=args.delete_dir)
    
    print("\n" + "="*60)
    if success:
        print("✓ ChromaDB cleanup completed successfully")
        if args.delete_dir:
            print("\nDatabase directory has been deleted.")
            print("A new empty database will be created when the application runs next.")
        else:
            print("\nAll collections have been deleted.")
            print("The database directory remains but is empty.")
            print("Collections will be recreated when the application runs next.")
    else:
        print("✗ ChromaDB cleanup failed")
        print("\nPlease check the error messages above and try again.")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

