#!/usr/bin/env python3
"""
Alpha Vantage API Connectivity Test Script

Tests connectivity to Alpha Vantage API.
Requires ALPHA_VANTAGE_API_KEY environment variable in .env file.

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
    import requests
    from datetime import datetime
    print("✓ requests library imported successfully")
except ImportError as e:
    print(f"✗ Failed to import requests: {e}")
    print("  Install with: pip install requests>=2.31.0")
    sys.exit(1)


def test_alpha_vantage_connectivity():
    """Test Alpha Vantage API connectivity"""
    print("\n" + "="*60)
    print("Alpha Vantage API Connectivity Test")
    print("="*60)
    
    # Get API key from .env file
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("\n✗ ALPHA_VANTAGE_API_KEY not found")
        print(f"  Please set ALPHA_VANTAGE_API_KEY in your .env file at: {project_root / '.env'}")
        print("  Get a free API key from: https://www.alphavantage.co/support/#api-key")
        return False
    
    print(f"\n✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    base_url = "https://www.alphavantage.co/query"
    test_symbol = "AAPL"
    
    print(f"\n1. Testing GLOBAL_QUOTE endpoint for {test_symbol}...")
    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": test_symbol,
            "apikey": api_key
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "Error Message" in data:
            print(f"  ✗ API Error: {data['Error Message']}")
            return False
        
        if "Note" in data:
            print(f"  ⚠ API Note: {data['Note']}")
            print("    (This usually means rate limit exceeded. Free tier: 5 calls/minute)")
            return False
        
        quote = data.get("Global Quote", {})
        if quote:
            price = quote.get("05. price")
            if price:
                print(f"  ✓ Success: Current price = ${float(price):.2f}")
                return True
            else:
                print(f"  ⚠ Warning: Quote received but price not available")
                return True
        else:
            print(f"  ✗ Failed: No quote data in response")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  ✗ Failed: Request timeout (check internet connection)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed: Request error - {e}")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n2. Testing OVERVIEW endpoint...")
    try:
        params = {
            "function": "OVERVIEW",
            "symbol": test_symbol,
            "apikey": api_key
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "Error Message" in data:
            print(f"  ✗ API Error: {data['Error Message']}")
            return False
        
        if "Note" in data:
            print(f"  ⚠ API Note: {data['Note']}")
            return False
        
        company_name = data.get("Name")
        if company_name:
            print(f"  ✓ Success: Company name = {company_name}")
            return True
        else:
            print(f"  ⚠ Warning: Overview received but name not available")
            return True
            
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Main test function"""
    print("\nStarting Alpha Vantage API connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_alpha_vantage_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ Alpha Vantage API connectivity test PASSED")
        print("\nAlpha Vantage API is accessible and working correctly.")
        print("Note: Free tier has rate limits (5 calls/minute, 500 calls/day)")
    else:
        print("✗ Alpha Vantage API connectivity test FAILED")
        print("\nPlease check:")
        print(f"  - ALPHA_VANTAGE_API_KEY is set correctly in .env file at: {project_root / '.env'}")
        print("  - Internet connection")
        print("  - API rate limits (free tier: 5 calls/minute)")
        print("  - Get API key from: https://www.alphavantage.co/support/#api-key")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

