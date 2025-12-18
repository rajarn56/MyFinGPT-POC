#!/usr/bin/env python3
"""
LiteLLM Anthropic Claude Connectivity Test Script

Tests connectivity to Anthropic Claude via LiteLLM.
Requires ANTHROPIC_API_KEY environment variable in .env file.

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


def test_anthropic_connectivity():
    """Test Anthropic Claude connectivity via LiteLLM"""
    print("\n" + "="*60)
    print("LiteLLM Anthropic Claude Connectivity Test")
    print("="*60)
    
    # Get API key from .env file
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n✗ ANTHROPIC_API_KEY not found")
        print(f"  Please set ANTHROPIC_API_KEY in your .env file at: {project_root / '.env'}")
        print("  Get an API key from: https://console.anthropic.com/")
        return False
    
    print(f"\n✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Set API key for LiteLLM
    os.environ["ANTHROPIC_API_KEY"] = api_key
    
    print("\n1. Testing Claude chat completion...")
    try:
        response = litellm.completion(
            model="claude-3-haiku-20240307",  # Using haiku for faster/cheaper test
            messages=[
                {"role": "user", "content": "Say 'Hello, Claude connectivity test successful!' and nothing else."}
            ],
            max_tokens=20,
            timeout=10
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"  ✓ Success: Received response from Claude")
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
        print("    Please check your ANTHROPIC_API_KEY")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Main test function"""
    print("\nStarting LiteLLM Anthropic Claude connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_anthropic_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ LiteLLM Anthropic Claude connectivity test PASSED")
        print("\nAnthropic Claude is accessible via LiteLLM and working correctly.")
    else:
        print("✗ LiteLLM Anthropic Claude connectivity test FAILED")
        print("\nPlease check:")
        print(f"  - ANTHROPIC_API_KEY is set correctly in .env file at: {project_root / '.env'}")
        print("  - Internet connection")
        print("  - API rate limits and billing status")
        print("  - Get API key from: https://console.anthropic.com/")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

