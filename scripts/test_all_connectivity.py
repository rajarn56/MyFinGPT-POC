#!/usr/bin/env python3
"""
Master Connectivity Test Script

Runs all connectivity tests for MyFinGPT integrations.
This script executes all individual connectivity test scripts.

Uses the same Python virtual environment and .env configuration as the POC.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Get project root and scripts directory
project_root = Path(__file__).parent.parent
scripts_dir = Path(__file__).parent

# Load environment variables from .env file (same as POC)
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env")

# List of all test scripts
TEST_SCRIPTS = [
    ("Yahoo Finance", "test_yahoo_finance.py"),
    ("Alpha Vantage API", "test_alpha_vantage.py"),
    ("Financial Modeling Prep API", "test_fmp.py"),
    ("Chroma Vector Database", "test_chroma.py"),
    ("LiteLLM OpenAI", "test_litellm_openai.py"),
    ("LiteLLM Google Gemini", "test_litellm_gemini.py"),
    ("LiteLLM Anthropic Claude", "test_litellm_anthropic.py"),
    ("LiteLLM Ollama", "test_litellm_ollama.py"),
    ("LangGraph", "test_langgraph.py"),
]


def run_test(script_name, script_path):
    """Run a single test script"""
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=scripts_dir,
            capture_output=False,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ✗ Test timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"  ✗ Error running test: {e}")
        return False


def main():
    """Main function to run all tests"""
    print("\n" + "="*70)
    print("MyFinGPT - All Connectivity Tests")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.executable}")
    print(f"Project root: {project_root}")
    print(f"Scripts directory: {scripts_dir}")
    print(f"Using .env from: {project_root / '.env'}")
    
    # Verify .env file exists
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"✓ Found .env file")
    else:
        print(f"⚠ Warning: .env file not found at {env_file}")
        print("  Some tests may fail without API keys")
    
    results = {}
    
    for test_name, script_file in TEST_SCRIPTS:
        script_path = scripts_dir / script_file
        
        if not script_path.exists():
            print(f"\n⚠ Warning: {script_file} not found, skipping...")
            results[test_name] = None
            continue
        
        success = run_test(test_name, script_path)
        results[test_name] = success
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results.items():
        if result is None:
            status = "SKIPPED"
            skipped += 1
        elif result:
            status = "✓ PASSED"
            passed += 1
        else:
            status = "✗ FAILED"
            failed += 1
        
        print(f"  {status:12} - {test_name}")
    
    print("\n" + "-"*70)
    print(f"Total: {len(results)} tests")
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    print("="*70 + "\n")
    
    # Return exit code (0 if all passed, 1 if any failed)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

