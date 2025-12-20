#!/usr/bin/env python3
"""
Financial Modeling Prep (FMP) API Connectivity Test Script

Tests connectivity to Financial Modeling Prep API.
Requires FMP_API_KEY environment variable in .env file.

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


def test_fmp_connectivity():
    """Test Financial Modeling Prep API connectivity"""
    print("\n" + "="*60)
    print("Financial Modeling Prep API Connectivity Test")
    print("="*60)
    
    # Get API key from .env file
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("\n✗ FMP_API_KEY not found")
        print(f"  Please set FMP_API_KEY in your .env file at: {project_root / '.env'}")
        print("  Get a free API key from: https://site.financialmodelingprep.com/developer/docs/")
        return False
    
    print(f"\n✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    base_url = "https://financialmodelingprep.com/stable"
    test_symbol = "AAPL"
    
    print(f"\n1. Testing quote endpoint for {test_symbol}...")
    try:
        params = {
            "symbol": test_symbol,
            "apikey": api_key
        }
        
        response = requests.get(f"{base_url}/quote", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and "Error Message" in data:
            print(f"  ✗ API Error: {data['Error Message']}")
            return False
        
        if not data or len(data) == 0:
            print(f"  ✗ Failed: No data returned")
            return False
        
        quote = data[0] if isinstance(data, list) else data
        price = quote.get("price")
        if price:
            print(f"  ✓ Success: Current price = ${float(price):.2f}")
            return True
        else:
            print(f"  ⚠ Warning: Quote received but price not available")
            return True
            
    except requests.exceptions.Timeout:
        print(f"  ✗ Failed: Request timeout (check internet connection)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed: Request error - {e}")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n2. Testing profile endpoint...")
    try:
        params = {
            "symbol": test_symbol,
            "apikey": api_key
        }
        
        response = requests.get(f"{base_url}/profile", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and "Error Message" in data:
            print(f"  ✗ API Error: {data['Error Message']}")
            return False
        
        if not data or len(data) == 0:
            print(f"  ✗ Failed: No profile data returned")
            return False
        
        profile = data[0] if isinstance(data, list) else data
        company_name = profile.get("companyName")
        if company_name:
            print(f"  ✓ Success: Company name = {company_name}")
            return True
        else:
            print(f"  ⚠ Warning: Profile received but name not available")
            return True
            
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Main test function"""
    print("\nStarting Financial Modeling Prep API connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_fmp_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ Financial Modeling Prep API connectivity test PASSED")
        print("\nFMP API is accessible and working correctly.")
    else:
        print("✗ Financial Modeling Prep API connectivity test FAILED")
        print("\nPlease check:")
        print(f"  - FMP_API_KEY is set correctly in .env file at: {project_root / '.env'}")
        print("  - Internet connection")
        print("  - API rate limits")
        print("  - Get API key from: https://site.financialmodelingprep.com/developer/docs/")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

