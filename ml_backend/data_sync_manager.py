import os
import pandas as pd
import shutil
from datetime import datetime
import json
import logging

class DataSyncManager:
    def __init__(self, ml_backend_path, flutter_data_path):
        """
        Initialize the DataSyncManager
        
        Args:
            ml_backend_path (str): Path to the ML backend directory
            flutter_data_path (str): Path to the Flutter app data directory
        """
        self.ml_backend_path = ml_backend_path
        self.flutter_data_path = flutter_data_path
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(ml_backend_path, 'sync.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # CSV file mappings
        self.csv_files = {
            'customers': 'customers.csv',
            'transactions': 'transactions.csv',
            'products': 'products.csv',
            'shops': 'shops.csv',
            'features': 'extracted_features.csv'
        }
        
    def sync_all_data(self):
        """Sync all CSV files from Flutter app to ML backend"""
        try:
            self.logger.info("Starting data synchronization...")
            
            sync_results = {}
            
            for data_type, filename in self.csv_files.items():
                result = self.sync_csv_file(data_type, filename)
                sync_results[data_type] = result
                
            # Update pipeline data
            self.update_pipeline_data()
            
            # Generate sync report
            self.generate_sync_report(sync_results)
            
            self.logger.info("Data synchronization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Data synchronization failed: {str(e)}")
            return False
    
    def sync_csv_file(self, data_type, filename):
        """Sync a specific CSV file"""
        try:
            source_path = os.path.join(self.flutter_data_path, filename)
            target_path = os.path.join(self.ml_backend_path, filename)
            
            if not os.path.exists(source_path):
                self.logger.warning(f"Source file not found: {source_path}")
                return {'success': False, 'message': 'Source file not found'}
            
            # Read source data
            source_df = pd.read_csv(source_path)
            
            # If target exists, merge data
            if os.path.exists(target_path):
                target_df = pd.read_csv(target_path)
                merged_df = self.merge_dataframes(source_df, target_df, data_type)
            else:
                merged_df = source_df
            
            # Save merged data
            merged_df.to_csv(target_path, index=False)
            
            self.logger.info(f"Synced {data_type}: {len(merged_df)} records")
            
            return {
                'success': True,
                'records': len(merged_df),
                'message': f'Successfully synced {len(merged_df)} records'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to sync {data_type}: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def merge_dataframes(self, source_df, target_df, data_type):
        """Merge source and target dataframes while preserving old data"""
        try:
            # Define primary keys for each data type
            primary_keys = {
                'customers': 'customer_id',
                'transactions': 'transaction_id',
                'products': 'product_id',
                'shops': 'shop_id',
                'features': 'transaction_id'  # Assuming features are per transaction
            }
            
            primary_key = primary_keys.get(data_type)
            
            if primary_key and primary_key in source_df.columns and primary_key in target_df.columns:
                # Remove duplicates from source based on primary key
                source_df = source_df.drop_duplicates(subset=[primary_key])
                target_df = target_df.drop_duplicates(subset=[primary_key])
                
                # Merge dataframes, updating existing records and adding new ones
                merged_df = pd.concat([target_df, source_df]).drop_duplicates(
                    subset=[primary_key], keep='last'
                )
            else:
                # If no primary key, simply concatenate and remove duplicates
                merged_df = pd.concat([target_df, source_df]).drop_duplicates()
            
            return merged_df
            
        except Exception as e:
            self.logger.error(f"Error merging dataframes for {data_type}: {str(e)}")
            # Return source data as fallback
            return source_df
    
    def update_pipeline_data(self):
        """Update the retail analytics pipeline with new data"""
        try:
            from retail_analytics_pipeline import RetailAnalyticsPipeline
            
            # Initialize pipeline with updated data
            pipeline = RetailAnalyticsPipeline(
                transactions_path=os.path.join(self.ml_backend_path, 'transactions.csv'),
                products_path=os.path.join(self.ml_backend_path, 'products.csv'),
                shops_path=os.path.join(self.ml_backend_path, 'shops.csv'),
                customers_path=os.path.join(self.ml_backend_path, 'customers.csv')
            )
            
            # Load and process data
            pipeline.load_data()
            pipeline.preprocess_data()
            
            # Retrain models if needed
            pipeline.train_demand_model()
            
            self.logger.info("Updated ML pipeline with new data")
            
        except Exception as e:
            self.logger.error(f"Failed to update pipeline: {str(e)}")
    
    def generate_sync_report(self, sync_results):
        """Generate a sync report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'sync_results': sync_results,
                'total_files_synced': sum(1 for r in sync_results.values() if r.get('success', False)),
                'total_files': len(sync_results)
            }
            
            report_path = os.path.join(self.ml_backend_path, 'sync_report.json')
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info(f"Sync report generated: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate sync report: {str(e)}")
    
    def extract_features_from_transactions(self):
        """Extract features from transactions and save to features.csv"""
        try:
            # Load all data
            customers_path = os.path.join(self.ml_backend_path, 'customers.csv')
            transactions_path = os.path.join(self.ml_backend_path, 'transactions.csv')
            products_path = os.path.join(self.ml_backend_path, 'products.csv')
            shops_path = os.path.join(self.ml_backend_path, 'shops.csv')
            
            if not all(os.path.exists(path) for path in [customers_path, transactions_path, products_path, shops_path]):
                self.logger.error("One or more required CSV files are missing")
                return False
            
            customers_df = pd.read_csv(customers_path)
            transactions_df = pd.read_csv(transactions_path)
            products_df = pd.read_csv(products_path)
            shops_df = pd.read_csv(shops_path)
            
            # Join all data
            features_df = transactions_df.merge(customers_df, on='customer_id', how='left', suffixes=('', '_customer'))
            features_df = features_df.merge(products_df, on='product_id', how='left', suffixes=('', '_product'))
            features_df = features_df.merge(shops_df, on='shop_id', how='left', suffixes=('', '_shop'))
            
            # Add calculated features
            features_df['price_difference'] = features_df['actual_price'] - features_df['standard_price']
            features_df['price_ratio'] = features_df['actual_price'] / features_df['standard_price'].replace(0, 1)
            features_df['total_amount'] = features_df['quantity'] * features_df['actual_price']
            
            # Add time-based features
            features_df['transaction_date'] = pd.to_datetime(features_df['transaction_date'])
            features_df['month'] = features_df['transaction_date'].dt.month
            features_df['day_of_week'] = features_df['transaction_date'].dt.dayofweek
            features_df['is_weekend'] = (features_df['day_of_week'] >= 5).astype(int)
            
            # Save features
            features_path = os.path.join(self.ml_backend_path, 'extracted_features.csv')
            features_df.to_csv(features_path, index=False)
            
            self.logger.info(f"Extracted {len(features_df)} feature records")
            return True
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}")
            return False
    
    def setup_automatic_sync(self, interval_minutes=5):
        """Setup automatic synchronization"""
        import schedule
        import time
        import threading
        
        def sync_job():
            self.logger.info("Starting scheduled sync...")
            self.sync_all_data()
            
        # Schedule the sync job
        schedule.every(interval_minutes).minutes.do(sync_job)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        # Run scheduler in a separate thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        self.logger.info(f"Automatic sync scheduled every {interval_minutes} minutes")
    
    def backup_data(self):
        """Create a backup of current data"""
        try:
            backup_dir = os.path.join(self.ml_backend_path, 'backups', datetime.now().strftime('%Y%m%d_%H%M%S'))
            os.makedirs(backup_dir, exist_ok=True)
            
            for filename in self.csv_files.values():
                source_path = os.path.join(self.ml_backend_path, filename)
                if os.path.exists(source_path):
                    target_path = os.path.join(backup_dir, filename)
                    shutil.copy2(source_path, target_path)
            
            self.logger.info(f"Data backup created: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            return None


def main():
    """Main function to run the data sync"""
    import sys
    
    # Configure paths
    ml_backend_path = os.path.dirname(os.path.abspath(__file__))
    flutter_data_path = os.path.join(os.path.dirname(ml_backend_path), 'meropasalapp')
    
    # Initialize sync manager
    sync_manager = DataSyncManager(ml_backend_path, flutter_data_path)
    
    # Create backup before sync
    backup_path = sync_manager.backup_data()
    
    # Extract features
    sync_manager.extract_features_from_transactions()
    
    # Sync all data
    success = sync_manager.sync_all_data()
    
    if success:
        print("Data synchronization completed successfully!")
        
        # Setup automatic sync if requested
        if len(sys.argv) > 1 and sys.argv[1] == '--auto':
            sync_manager.setup_automatic_sync()
            print("Automatic sync enabled. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nAutomatic sync stopped.")
    else:
        print("Data synchronization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
