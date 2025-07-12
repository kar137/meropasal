import sys
import os
sys.path.insert(0, r'C:\Users\suraj\OneDrive\Desktop\getx file\meropasal\ml_backend')

from data_sync_manager import DataSyncManager

# Initialize paths
ml_backend_path = r'C:\Users\suraj\OneDrive\Desktop\getx file\meropasal\ml_backend'
flutter_data_path = r'C:\Users\suraj\OneDrive\Desktop\getx file\meropasal\meropasalapp'

print(f"ML Backend Path: {ml_backend_path}")
print(f"Flutter Data Path: {flutter_data_path}")

# Check if source files exist
import os
csv_files = ['customers.csv', 'products.csv', 'shops.csv', 'transactions.csv']
for file in csv_files:
    flutter_file = os.path.join(flutter_data_path, file)
    ml_file = os.path.join(ml_backend_path, file)
    print(f"{file}: Flutter={os.path.exists(flutter_file)}, ML={os.path.exists(ml_file)}")

# Initialize sync manager
sync_manager = DataSyncManager(ml_backend_path, flutter_data_path)

print("\nStarting sync...")
success = sync_manager.sync_all_data()
print(f"Sync result: {success}")

print("\nExtracting features...")
features_success = sync_manager.extract_features_from_transactions()
print(f"Feature extraction result: {features_success}")
