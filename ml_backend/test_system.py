#!/usr/bin/env python3
"""
Test script to verify the ML Backend setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
        
        import flask
        print("✓ flask imported successfully")
        
        import data_sync_manager
        print("✓ data_sync_manager imported successfully")
        
        import sync_api
        print("✓ sync_api imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_csv_files():
    """Test if CSV files exist and can be read"""
    try:
        import pandas as pd
        
        files = ['customers.csv', 'products.csv', 'shops.csv', 'transactions.csv']
        
        for file in files:
            if os.path.exists(file):
                df = pd.read_csv(file)
                print(f"✓ {file} exists with {len(df)} records")
            else:
                print(f"✗ {file} not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ CSV test error: {e}")
        return False

def test_feature_extraction():
    """Test feature extraction functionality"""
    try:
        from data_sync_manager import DataSyncManager
        
        ml_backend_path = os.path.dirname(os.path.abspath(__file__))
        flutter_data_path = os.path.join(os.path.dirname(ml_backend_path), 'meropasalapp')
        
        sync_manager = DataSyncManager(ml_backend_path, flutter_data_path)
        success = sync_manager.extract_features_from_transactions()
        
        if success:
            print("✓ Feature extraction test passed")
            return True
        else:
            print("✗ Feature extraction test failed")
            return False
            
    except Exception as e:
        print(f"✗ Feature extraction error: {e}")
        return False

def test_api_creation():
    """Test if API can be created"""
    try:
        from sync_api import app
        print("✓ API app created successfully")
        return True
    except Exception as e:
        print(f"✗ API creation error: {e}")
        return False

def main():
    """Main test function"""
    print("Testing ML Backend Data Sync System")
    print("=" * 40)
    
    tests = [
        ("Module imports", test_imports),
        ("CSV files", test_csv_files),
        ("Feature extraction", test_feature_extraction),
        ("API creation", test_api_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"Test failed: {test_name}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nTo start the system:")
        print("1. Run: python start_api.py")
        print("2. API will be available at: http://localhost:8000")
        print("3. Test with: http://localhost:8000/api/health")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
