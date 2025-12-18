#!/usr/bin/env python3
"""
LiteLLM Ollama Connectivity Test Script

Tests connectivity to Ollama (local LLM) via LiteLLM.
Requires Ollama to be running locally (default: http://localhost:11434).
OLLAMA_API_BASE can be set in .env file.

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
    import litellm
    import requests
    from datetime import datetime
    print("✓ litellm and requests libraries imported successfully")
except ImportError as e:
    print(f"✗ Failed to import required libraries: {e}")
    print("  Install with: pip install litellm>=1.30.0 requests>=2.31.0")
    sys.exit(1)


def test_ollama_connectivity():
    """Test Ollama connectivity via LiteLLM"""
    print("\n" + "="*60)
    print("LiteLLM Ollama Connectivity Test")
    print("="*60)
    
    # Get API base URL from .env file
    api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    print(f"\n✓ Using Ollama API base: {api_base}")
    print(f"  (Set OLLAMA_API_BASE in .env file at: {project_root / '.env'})")
    
    print("\n1. Testing Ollama server availability...")
    try:
        response = requests.get(f"{api_base}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        print(f"  ✓ Success: Ollama server is running")
        if models:
            model_names = [m.get("name", "unknown") for m in models]
            print(f"    Available models: {', '.join(model_names[:5])}")
        else:
            print(f"    ⚠ Warning: No models found. Pull a model with: ollama pull llama2")
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Failed: Cannot connect to Ollama server at {api_base}")
        print("    Please ensure Ollama is running:")
        print("    1. Install Ollama from: https://ollama.ai/")
        print("    2. Start Ollama service")
        print("    3. Pull a model: ollama pull llama2")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Set API base for LiteLLM
    os.environ["OLLAMA_API_BASE"] = api_base
    
    print("\n2. Testing Ollama chat completion...")
    try:
        # Try common model names
        test_models = ["llama2", "mistral", "codellama", "llama3"]
        model_used = None
        
        for model_name in test_models:
            try:
                response = litellm.completion(
                    model=f"ollama/{model_name}",
                    messages=[
                        {"role": "user", "content": "Say 'Hello, Ollama connectivity test successful!' and nothing else."}
                    ],
                    max_tokens=20,
                    timeout=10,
                    api_base=api_base
                )
                
                if response and response.choices:
                    content = response.choices[0].message.content
                    print(f"  ✓ Success: Received response from Ollama")
                    print(f"    Model used: {model_name}")
                    print(f"    Response: {content[:100]}...")
                    model_used = model_name
                    return True
            except Exception as e:
                continue
        
        if not model_used:
            print(f"  ✗ Failed: Could not connect with any model")
            print("    Available models: " + ", ".join(test_models))
            print("    Please pull a model: ollama pull llama2")
            return False
            
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        print("    Please ensure:")
        print("    1. Ollama is running")
        print("    2. At least one model is pulled (e.g., ollama pull llama2)")
        return False


def main():
    """Main test function"""
    print("\nStarting LiteLLM Ollama connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_ollama_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ LiteLLM Ollama connectivity test PASSED")
        print("\nOllama is accessible via LiteLLM and working correctly.")
    else:
        print("✗ LiteLLM Ollama connectivity test FAILED")
        print("\nPlease check:")
        print("  - Ollama is installed and running")
        print(f"  - OLLAMA_API_BASE is set correctly in .env file at: {project_root / '.env'}")
        print("    (default: http://localhost:11434)")
        print("  - At least one model is pulled: ollama pull llama2")
        print("  - Install Ollama from: https://ollama.ai/")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

