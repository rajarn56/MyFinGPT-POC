#!/usr/bin/env python3
"""
LiteLLM Google Gemini Connectivity Test Script

Tests connectivity to Google Gemini via LiteLLM.
Requires GEMINI_API_KEY environment variable in .env file.

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
    from datetime import datetime
    print("✓ litellm library imported successfully")
except ImportError as e:
    print(f"✗ Failed to import litellm: {e}")
    print("  Install with: pip install litellm>=1.30.0")
    sys.exit(1)


def test_gemini_connectivity():
    """Test Google Gemini connectivity via LiteLLM"""
    print("\n" + "="*60)
    print("LiteLLM Google Gemini Connectivity Test")
    print("="*60)
    
    # Get API key from .env file
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n✗ GEMINI_API_KEY not found")
        print(f"  Please set GEMINI_API_KEY in your .env file at: {project_root / '.env'}")
        print("  Get an API key from: https://makersuite.google.com/app/apikey")
        return False
    
    print(f"\n✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Set API key for LiteLLM
    os.environ["GEMINI_API_KEY"] = api_key
    
    print("\n1. Testing Gemini chat completion...")
    try:
        response = litellm.completion(
            model="gemini-pro",
            messages=[
                {"role": "user", "content": "Say 'Hello, Gemini connectivity test successful!' and nothing else."}
            ],
            max_tokens=20,
            timeout=10
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"  ✓ Success: Received response from Gemini")
            print(f"    Response: {content[:100]}...")
            return True
        else:
            print(f"  ✗ Failed: No response received")
            return False
            
    except litellm.exceptions.RateLimitError as e:
        print(f"  ✗ Failed: Rate limit exceeded - {e}")
        print("    Please wait a moment and try again")
        return False
    except litellm.exceptions.AuthenticationError as e:
        print(f"  ✗ Failed: Authentication error - {e}")
        print("    Please check your GEMINI_API_KEY")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Main test function"""
    print("\nStarting LiteLLM Google Gemini connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_gemini_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ LiteLLM Google Gemini connectivity test PASSED")
        print("\nGoogle Gemini is accessible via LiteLLM and working correctly.")
    else:
        print("✗ LiteLLM Google Gemini connectivity test FAILED")
        print("\nPlease check:")
        print(f"  - GEMINI_API_KEY is set correctly in .env file at: {project_root / '.env'}")
        print("  - Internet connection")
        print("  - API rate limits and billing status")
        print("  - Get API key from: https://makersuite.google.com/app/apikey")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

