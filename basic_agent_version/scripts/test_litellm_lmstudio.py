#!/usr/bin/env python3
"""
LiteLLM LM Studio Connectivity Test Script

Tests connectivity to LM Studio (local LLM) via LiteLLM.
Requires LM Studio to be running locally (default: http://localhost:1234).
LM_STUDIO_API_BASE can be set in .env file.

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


def test_lmstudio_connectivity():
    """Test LM Studio connectivity via LiteLLM"""
    print("\n" + "="*60)
    print("LiteLLM LM Studio Connectivity Test")
    print("="*60)
    
    # Get API base URL from .env file (default includes /v1 for OpenAI-compatible API)
    api_base = os.getenv("LM_STUDIO_API_BASE", "http://localhost:1234/v1")
    print(f"\n✓ Using LM Studio API base: {api_base}")
    print(f"  (Set LM_STUDIO_API_BASE in .env file at: {project_root / '.env'})")
    print(f"  (default: http://localhost:1234/v1)")
    
    print("\n1. Testing LM Studio server availability...")
    try:
        # LM Studio uses OpenAI-compatible API at /v1/models
        response = requests.get(f"{api_base}/models", timeout=5)
        response.raise_for_status()
        models_data = response.json()
        models = models_data.get("data", [])
        print(f"  ✓ Success: LM Studio server is running")
        if models:
            model_names = [m.get("id", "unknown") for m in models]
            print(f"    Available models: {', '.join(model_names[:5])}")
            if len(models) > 5:
                print(f"    ... and {len(models) - 5} more")
        else:
            print(f"    ⚠ Warning: No models found. Load a model in LM Studio.")
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Failed: Cannot connect to LM Studio server at {api_base}")
        print("    Please ensure LM Studio is running:")
        print("    1. Install LM Studio from: https://lmstudio.ai/")
        print("    2. Start LM Studio application")
        print("    3. Load a model in LM Studio")
        print("    4. Start the local server (usually on port 1234)")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Set API base for LiteLLM
    os.environ["LM_STUDIO_API_BASE"] = api_base
    
    print("\n2. Testing LM Studio chat completion...")
    try:
        # Get available models from the server
        try:
            response = requests.get(f"{api_base}/models", timeout=5)
            response.raise_for_status()
            models_data = response.json()
            available_models = [m.get("id", "") for m in models_data.get("data", [])]
        except:
            available_models = []
        
        # Try to use an available model, or fall back to common model names
        test_models = available_models[:3] if available_models else ["local-model", "gpt-3.5-turbo"]
        model_used = None
        
        for model_name in test_models:
            try:
                # LM Studio uses OpenAI-compatible API, so we use openai/ prefix
                # The model name should match what's loaded in LM Studio
                response = litellm.completion(
                    model=f"openai/{model_name}",
                    messages=[
                        {"role": "user", "content": "Say 'Hello, LM Studio connectivity test successful!' and nothing else."}
                    ],
                    max_tokens=20,
                    timeout=10,
                    api_base=api_base
                )
                
                if response and response.choices:
                    content = response.choices[0].message.content
                    print(f"  ✓ Success: Received response from LM Studio")
                    print(f"    Model used: {model_name}")
                    print(f"    Response: {content[:100]}...")
                    model_used = model_name
                    return True
            except Exception as e:
                # Try next model
                continue
        
        if not model_used:
            print(f"  ✗ Failed: Could not connect with any model")
            if available_models:
                print(f"    Available models: {', '.join(available_models[:5])}")
            else:
                print("    No models found. Please load a model in LM Studio.")
            print("    Please ensure:")
            print("    1. LM Studio is running")
            print("    2. A model is loaded in LM Studio")
            print("    3. The local server is started (usually on port 1234)")
            return False
            
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        print("    Please ensure:")
        print("    1. LM Studio is running")
        print("    2. A model is loaded in LM Studio")
        print("    3. The local server is started (usually on port 1234)")
        return False


def main():
    """Main test function"""
    print("\nStarting LiteLLM LM Studio connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_lmstudio_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ LiteLLM LM Studio connectivity test PASSED")
        print("\nLM Studio is accessible via LiteLLM and working correctly.")
    else:
        print("✗ LiteLLM LM Studio connectivity test FAILED")
        print("\nPlease check:")
        print("  - LM Studio is installed and running")
        print(f"  - LM_STUDIO_API_BASE is set correctly in .env file at: {project_root / '.env'}")
        print("    (default: http://localhost:1234/v1)")
        print("  - A model is loaded in LM Studio")
        print("  - The local server is started in LM Studio")
        print("  - Install LM Studio from: https://lmstudio.ai/")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

