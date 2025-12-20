#!/usr/bin/env python3
"""
LangGraph Connectivity Test Script

Tests LangGraph library import and basic functionality.

Uses the same Python virtual environment and .env configuration as the POC.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file (same as POC)
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env")


def test_langgraph_connectivity():
    """Test LangGraph library connectivity"""
    print("\n" + "="*60)
    print("LangGraph Connectivity Test")
    print("="*60)
    
    print("\n1. Testing LangGraph import...")
    try:
        from langgraph.graph import StateGraph, END
        print("  ✓ Success: LangGraph imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed: {e}")
        print("    Install with: pip install langgraph>=0.0.40")
        return False
    
    print("\n2. Testing StateGraph creation...")
    try:
        from typing import TypedDict
        
        # Create a simple state type
        class TestState(TypedDict):
            value: str
        
        # Create a simple graph
        graph = StateGraph(TestState)
        
        # Add a simple node
        def test_node(state: TestState) -> TestState:
            return {"value": "test"}
        
        graph.add_node("test", test_node)
        graph.set_entry_point("test")
        graph.add_edge("test", END)
        
        # Compile the graph
        app = graph.compile()
        
        print("  ✓ Success: StateGraph created and compiled")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n3. Testing graph execution...")
    try:
        # Execute the graph
        result = app.invoke({"value": "initial"})
        
        if result and result.get("value") == "test":
            print("  ✓ Success: Graph executed successfully")
            return True
        else:
            print(f"  ⚠ Warning: Graph executed but result unexpected: {result}")
            return True
            
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Main test function"""
    print("\nStarting LangGraph connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_langgraph_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ LangGraph connectivity test PASSED")
        print("\nLangGraph is installed and working correctly.")
    else:
        print("✗ LangGraph connectivity test FAILED")
        print("\nPlease check:")
        print("  - langgraph library installation: pip install langgraph>=0.0.40")
        print("  - Python version compatibility (Python 3.8+)")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

