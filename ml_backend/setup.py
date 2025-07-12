#!/usr/bin/env python3
"""
Setup script for the ML Backend Data Sync System
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def create_directories():
    """Create necessary directories"""
    directories = [
        'backups',
        'logs',
        'data',
    ]
    
    try:
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
        return True
    except Exception as e:
        print(f"Error creating directories: {e}")
        return False

def copy_sample_data():
    """Copy sample data from the app directory"""
    print("📋 Setting up sample data...")
    
    # Import after dependencies are installed
    try:
        from data_sync_manager import DataSyncManager
        
        # Initialize sync manager
        ml_backend_path = os.path.dirname(os.path.abspath(__file__))
        flutter_data_path = os.path.join(os.path.dirname(ml_backend_path), 'meropasalapp')
        
        sync_manager = DataSyncManager(ml_backend_path, flutter_data_path)
        
        # Create initial CSV files if they don't exist
        _create_initial_csv_files()
        
        # Extract features
        sync_manager.extract_features_from_transactions()
        
        print("✅ Sample data setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Sample data setup failed: {e}")
        return False

def _create_initial_csv_files():
    """Create initial CSV files with sample data"""
    
    # Create customers.csv
    customers_data = """customer_id,customer_name,gender,age,city,preferred_categories,avg_monthly_spending,visits_per_month
1,Customer 1,Other,29,Pokhara,"Snacks, Personal Care",1406.82,12
2,Customer 2,Female,32,Bhaktapur,"Household, Personal Care",4250.83,3
3,Customer 3,Male,53,Biratnagar,Beverage,4588.2,12
4,Customer 4,Other,31,Lalitpur,Beverage,1007.41,11
5,Customer 5,Other,22,Kathmandu,Snacks,1150.9,7"""
    
    # Create products.csv
    products_data = """product_id,product_name,category,brand,standard_price
1,Pepsi Bev1,Beverage,Pepsi,98.67
2,Wai Wai Sna2,Snacks,Wai Wai,442.06
3,Nestle Bev3,Beverage,Nestle,253.9
4,Nestle Bev4,Beverage,Nestle,373.24
5,Pepsi Bev5,Beverage,Pepsi,70.13"""
    
    # Create shops.csv
    shops_data = """shop_id,city,district
1,Lalitpur,Bhaktapur
2,Biratnagar,Kathmandu
3,Bhaktapur,Lalitpur
4,Pokhara,Lalitpur
5,Pokhara,Kathmandu"""
    
    # Create transactions.csv
    transactions_data = """transaction_id,customer_id,product_id,shop_id,quantity,actual_price,transaction_date,payment_method
T1001,1,1,1,2,100.0,2024-07-12T10:30:00,Cash
T1002,2,2,2,1,450.0,2024-07-11T14:15:00,Card
T1003,3,3,3,3,260.0,2024-07-10T09:45:00,Digital
T1004,4,4,4,1,380.0,2024-07-09T16:20:00,Cash
T1005,5,5,5,2,75.0,2024-07-08T11:10:00,Card"""
    
    # Write files
    files = {
        'customers.csv': customers_data,
        'products.csv': products_data,
        'shops.csv': shops_data,
        'transactions.csv': transactions_data,
    }
    
    for filename, data in files.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"Created {filename}")

def test_system():
    """Test the system functionality"""
    print("🧪 Testing system functionality...")
    
    try:
        from data_sync_manager import DataSyncManager
        
        # Initialize sync manager
        ml_backend_path = os.path.dirname(os.path.abspath(__file__))
        flutter_data_path = os.path.join(os.path.dirname(ml_backend_path), 'meropasalapp')
        
        sync_manager = DataSyncManager(ml_backend_path, flutter_data_path)
        
        # Test feature extraction
        success = sync_manager.extract_features_from_transactions()
        
        if success:
            print("✅ System test passed")
            return True
        else:
            print("❌ System test failed")
            return False
            
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def create_startup_scripts():
    """Create startup scripts for the system"""
    
    try:
        # API server startup script
        api_script = """#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_api import app

if __name__ == '__main__':
    print("Starting ML Backend Sync API...")
    app.run(host='0.0.0.0', port=8000, debug=False)
"""
        
        with open('start_api.py', 'w', encoding='utf-8') as f:
            f.write(api_script)
        
        # Data sync script
        sync_script = """#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_sync_manager import main

if __name__ == '__main__':
    print("Starting data sync...")
    main()
"""
        
        with open('sync_data.py', 'w', encoding='utf-8') as f:
            f.write(sync_script)
        
        print("Created startup scripts")
        return True
        
    except Exception as e:
        print(f"Error creating startup scripts: {e}")
        return False
    
    print("📜 Created startup scripts")

def create_config_file():
    """Create configuration file"""
    try:
        config = {
            "ml_backend_path": os.path.dirname(os.path.abspath(__file__)),
            "flutter_data_path": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'meropasalapp'),
            "api_port": 8000,
            "sync_interval_minutes": 5,
            "auto_backup": True,
            "max_backups": 10,
            "log_level": "INFO"
        }
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print("Created configuration file")
        return True
        
    except Exception as e:
        print(f"Error creating configuration file: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up ML Backend Data Sync System")
    print("=" * 50)
    
    success_count = 0
    total_steps = 6
    
    steps = [
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Setting up sample data", copy_sample_data),
        ("Testing system", test_system),
        ("Creating startup scripts", create_startup_scripts),
        ("Creating configuration", create_config_file),
    ]
    
    for step_name, step_function in steps:
        print(f"\nStep: {step_name}")
        if step_function():
            success_count += 1
        else:
            print(f"Warning: {step_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Setup completed: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("\nML Backend Data Sync System is ready!")
        print("\nNext steps:")
        print("1. Start the API server: python start_api.py")
        print("2. Test data sync: python sync_data.py")
        print("3. Enable auto-sync: python sync_data.py --auto")
        print("\nAPI will be available at: http://localhost:8000")
    else:
        print(f"\nSetup completed with warnings. {total_steps - success_count} steps failed.")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
