#!/usr/bin/env python3
"""
Yahoo Finance Connectivity Test Script

Tests connectivity to Yahoo Finance using the yfinance library.
This script verifies that the yfinance library can successfully fetch stock data.

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
    import yfinance as yf
    from datetime import datetime
    print("✓ yfinance library imported successfully")
except ImportError as e:
    print(f"✗ Failed to import yfinance: {e}")
    print("  Install with: pip install yfinance>=0.2.28")
    sys.exit(1)


def test_yahoo_finance_connectivity():
    """Test Yahoo Finance connectivity"""
    print("\n" + "="*60)
    print("Yahoo Finance Connectivity Test")
    print("="*60)
    
    # Test symbol
    test_symbol = "AAPL"
    all_tests_passed = True
    
    print(f"\n1. Testing stock price fetch for {test_symbol}...")
    try:
        ticker = yf.Ticker(test_symbol)
        info = ticker.info
        
        if not info:
            print(f"  ✗ Failed: No data returned for {test_symbol}")
            all_tests_passed = False
        else:
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            if current_price:
                print(f"  ✓ Success: Current price = ${current_price:.2f}")
            else:
                print(f"  ⚠ Warning: Price data not available, but connection successful")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        all_tests_passed = False
    
    print("\n2. Testing company info fetch...")
    try:
        ticker = yf.Ticker(test_symbol)
        info = ticker.info
        
        company_name = info.get("longName") or info.get("shortName")
        if company_name:
            print(f"  ✓ Success: Company name = {company_name}")
        else:
            print(f"  ⚠ Warning: Company name not available")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        all_tests_passed = False
    
    print("\n3. Testing historical data fetch...")
    try:
        ticker = yf.Ticker(test_symbol)
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            print(f"  ✓ Success: Retrieved {len(hist)} days of historical data")
            print(f"    Latest date: {hist.index[-1].strftime('%Y-%m-%d')}")
        else:
            print(f"  ⚠ Warning: No historical data returned")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        all_tests_passed = False
    
    return all_tests_passed


def main():
    """Main test function"""
    print("\nStarting Yahoo Finance connectivity test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = test_yahoo_finance_connectivity()
    
    print("\n" + "="*60)
    if success:
        print("✓ Yahoo Finance connectivity test PASSED")
        print("\nYahoo Finance is accessible and working correctly.")
    else:
        print("✗ Yahoo Finance connectivity test FAILED")
        print("\nPlease check:")
        print("  - Internet connection")
        print("  - yfinance library installation: pip install yfinance>=0.2.28")
        print("  - Yahoo Finance service availability")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

