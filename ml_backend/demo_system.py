#!/usr/bin/env python3
"""
Demo script to showcase the ML Backend Data Sync System functionality
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n[Step {step}] {description}")
    print("-" * 40)

def test_api_health():
    """Test the API health endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ API is healthy!")
            print(f"  Status: {data.get('status')}")
            print(f"  Service: {data.get('service')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API health check error: {e}")
        return False

def test_data_sync():
    """Test the data sync functionality"""
    try:
        response = requests.post("http://localhost:8000/api/sync-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Data sync successful!")
            print(f"  Message: {data.get('message')}")
            print(f"  Backup: {data.get('backup_path', 'N/A')}")
            return True
        else:
            print(f"✗ Data sync failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Data sync error: {e}")
        return False

def test_feature_extraction():
    """Test feature extraction"""
    try:
        response = requests.post("http://localhost:8000/api/extract-features", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✓ Feature extraction successful!")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"✗ Feature extraction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Feature extraction error: {e}")
        return False

def test_sync_status():
    """Test sync status endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/sync-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Sync status retrieved!")
            
            file_stats = data.get('file_statistics', {})
            for file_type, stats in file_stats.items():
                records = stats.get('records', 0)
                print(f"  {file_type}: {records} records")
            
            return True
        else:
            print(f"✗ Sync status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Sync status error: {e}")
        return False

def show_csv_data():
    """Show sample CSV data"""
    try:
        import pandas as pd
        
        files = ['customers.csv', 'transactions.csv', 'products.csv', 'shops.csv']
        
        for file in files:
            if os.path.exists(file):
                df = pd.read_csv(file)
                print(f"\n{file.upper()} (showing first 3 rows):")
                print(df.head(3).to_string(index=False))
            else:
                print(f"\n{file}: Not found")
                
    except Exception as e:
        print(f"Error reading CSV files: {e}")

def show_extracted_features():
    """Show extracted features"""
    try:
        import pandas as pd
        
        if os.path.exists('extracted_features.csv'):
            df = pd.read_csv('extracted_features.csv')
            print(f"\nEXTRACTED FEATURES ({len(df)} records):")
            print("Columns:", list(df.columns))
            print("\nSample features (first 2 rows):")
            print(df.head(2).to_string(index=False))
        else:
            print("\nExtracted features file not found")
            
    except Exception as e:
        print(f"Error reading features file: {e}")

def demo_add_transaction():
    """Demo adding a new transaction via the API"""
    try:
        # This would be the data from Flutter app
        new_transaction = {
            "transaction_id": f"T{int(time.time())}",
            "customer_id": "1",
            "product_id": "2", 
            "shop_id": "3",
            "quantity": 2,
            "actual_price": 450.0,
            "transaction_date": datetime.now().isoformat(),
            "payment_method": "Card"
        }
        
        print(f"Adding new transaction: {new_transaction['transaction_id']}")
        print(f"  Customer: {new_transaction['customer_id']}")
        print(f"  Product: {new_transaction['product_id']}")
        print(f"  Amount: {new_transaction['actual_price']} x {new_transaction['quantity']}")
        
        # In real implementation, this would come from Flutter app
        # For demo, we'll just simulate the sync
        response = requests.post("http://localhost:8000/api/sync-data", timeout=10)
        
        if response.status_code == 200:
            print("✓ Transaction sync simulated successfully!")
            return True
        else:
            print(f"✗ Transaction sync failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Transaction demo error: {e}")
        return False

def main():
    """Main demo function"""
    print_header("ML Backend Data Sync System - LIVE DEMO")
    
    print("\nThis demo showcases the key features of the system:")
    print("• Automatic CSV data management")
    print("• Feature extraction from joined datasets")
    print("• Real-time synchronization with ML backend")
    print("• Data preservation and backup")
    print("• RESTful API for Flutter integration")
    
    print("\nStarting demo in 3 seconds...")
    time.sleep(3)
    
    # Step 1: Show current data
    print_step(1, "Current Data State")
    show_csv_data()
    
    # Step 2: Test API health
    print_step(2, "API Health Check")
    if not test_api_health():
        print("\n❌ API is not running. Please start it with: python start_api.py")
        return 1
    
    # Step 3: Test data sync
    print_step(3, "Data Synchronization")
    test_data_sync()
    
    # Step 4: Test feature extraction
    print_step(4, "Feature Extraction")
    test_feature_extraction()
    
    # Step 5: Show extracted features
    print_step(5, "Extracted Features")
    show_extracted_features()
    
    # Step 6: Demo transaction addition
    print_step(6, "Transaction Addition Demo")
    demo_add_transaction()
    
    # Step 7: Check sync status
    print_step(7, "Final Sync Status")
    test_sync_status()
    
    # Summary
    print_header("DEMO COMPLETED")
    print("\n✨ Key Features Demonstrated:")
    print("  ✓ CSV data management and persistence")
    print("  ✓ Automatic feature extraction from joined datasets")
    print("  ✓ Real-time API communication")
    print("  ✓ Data backup and preservation")
    print("  ✓ Transaction processing pipeline")
    
    print("\n🚀 Integration with Flutter App:")
    print("  • Flutter app calls LocalDataService for local storage")
    print("  • MLBackendSyncService handles automatic synchronization")
    print("  • TransactionController manages the data flow")
    print("  • Features are automatically extracted and sent to ML models")
    print("  • Old data is preserved while new data is continuously added")
    
    print("\n📱 Next Steps:")
    print("  1. Run Flutter app: cd ../meropasalapp && flutter run")
    print("  2. Use DataManagementPage to add transactions")
    print("  3. Enable auto-sync for real-time updates")
    print("  4. Monitor analytics dashboard for insights")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
