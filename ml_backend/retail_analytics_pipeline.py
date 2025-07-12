import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error  # Added mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from mlxtend.frequent_patterns import apriori, association_rules
import joblib
import os
from datetime import datetime
import json

class RetailAnalyticsPipeline:
    def __init__(self, transactions_path, products_path, shops_path, customers_path):
        """Initialize pipeline with data paths"""
        self.transactions_path = transactions_path
        self.products_path = products_path 
        self.shops_path = shops_path
        self.customers_path = customers_path
        
        # Initialize attributes
        self.data = None
        self.products = None
        self.shops = None
        self.customers = None
        self.monthly_data = None
        self.customer_profiles = None
        self.model = None
        self.is_trained = False  # Make sure this is here
        self.subscription = 'free'
        self.feature_columns = [
            'last_month_qty', 'last_2_months_qty', 'last_3_months_qty',
            'avg_last_3_months', 'trend', 'price_difference',
            'is_holiday_month', 'is_summer', 'category_code', 'shop_city_code'
        ]
        
        # Subscription plans configuration
        self.subscription_plans = {
            'free': {
                'product_owner_features': ['basic_trends', 'seasonality_charts', 'basic_plots'],
                'shopkeeper_features': ['full_recommendations'],
                'customer_features': ['full_recommendations'],
                'price': 0
            },
            'premium': {
                'product_owner_features': ['advanced_analytics', 'geographic_distribution', 
                                         'competitor_analysis', 'custom_reports', 'export_data'],
                'shopkeeper_features': ['full_recommendations', 'export_data'],
                'customer_features': ['full_recommendations'],
                'price': 99.99  # Monthly price
            }
        }
        self.current_subscription = 'free'  # Default to free
    
    def load_and_prepare_data(self):
        """Load all data sources and prepare for analysis"""
        print("Loading and preparing data...")
        
        # Validate files exist
        for path in [self.transactions_path, self.products_path, 
                    self.shops_path, self.customers_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Data file not found: {path}")
        
        try:
            # Load transactions first to check columns
            print("Loading transactions...")
            transactions = pd.read_csv(self.transactions_path)
            print(f"Transactions columns: {list(transactions.columns)}")
            
            # Check if customer_id exists in transactions
            if 'customer_id' not in transactions.columns:
                print("WARNING: customer_id not found in transactions. Adding sequential customer_id...")
                transactions['customer_id'] = ['CUST_' + str(i).zfill(6) for i in range(1, len(transactions) + 1)]
            
            # Apply data types after ensuring columns exist
            transactions = transactions.astype({
                'transaction_id': str,
                'product_id': str,
                'shop_id': str,
                'customer_id': str,
                'quantity': int,
                'unit_price': float,
                'total_amount': float
            })
            
            if 'transaction_time' in transactions.columns:
                transactions['transaction_time'] = pd.to_datetime(transactions['transaction_time'])
            else:
                raise ValueError("transaction_time column is required in transactions.csv")
            
            print("Loading products...")
            self.products = pd.read_csv(self.products_path)
            print(f"Products columns: {list(self.products.columns)}")
            
            # Ensure required columns exist
            required_product_cols = ['product_id', 'product_name', 'category', 'standard_price']
            missing_cols = [col for col in required_product_cols if col not in self.products.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in products.csv: {missing_cols}")
            
            self.products = self.products.astype({
                'product_id': str,
                'product_name': str,
                'category': str,
                'standard_price': float
            })
            
            print("Loading shops...")
            self.shops = pd.read_csv(self.shops_path)
            print(f"Shops columns: {list(self.shops.columns)}")
            
            # Create shop_name if missing
            if 'shop_name' not in self.shops.columns:
                print("WARNING: shop_name not found in shops.csv. Creating shop_name column...")
                # Check if there are alternative name columns
                if 'name' in self.shops.columns:
                    self.shops['shop_name'] = self.shops['name']
                    print("  Used 'name' column for shop_name")
                elif 'store_name' in self.shops.columns:
                    self.shops['shop_name'] = self.shops['store_name']
                    print("  Used 'store_name' column for shop_name")
                else:
                    # Create generic shop names based on shop_id or index
                    if 'shop_id' in self.shops.columns:
                        self.shops['shop_name'] = 'Shop_' + self.shops['shop_id'].astype(str)
                    else:
                        self.shops['shop_name'] = ['Shop_' + str(i) for i in range(1, len(self.shops) + 1)]
                    print("  Created generic shop names")
            
            # Create shop_id if missing
            if 'shop_id' not in self.shops.columns:
                print("WARNING: shop_id not found in shops.csv. Creating shop_id column...")
                self.shops['shop_id'] = ['SHOP_' + str(i).zfill(6) for i in range(1, len(self.shops) + 1)]
            
            # Create city if missing
            if 'city' not in self.shops.columns:
                print("WARNING: city not found in shops.csv. Creating city column...")
                # Check for alternative location columns
                if 'location' in self.shops.columns:
                    self.shops['city'] = self.shops['location']
                    print("  Used 'location' column for city")
                elif 'area' in self.shops.columns:
                    self.shops['city'] = self.shops['area']
                    print("  Used 'area' column for city")
                else:
                    self.shops['city'] = 'Default City'
                    print("  Created default city")
            
            # Apply data types for existing columns
            shop_dtypes = {
                'shop_id': str,
                'shop_name': str,
                'city': str
            }
            
            for col, dtype in shop_dtypes.items():
                if col in self.shops.columns:
                    try:
                        self.shops[col] = self.shops[col].astype(dtype)
                    except Exception as e:
                        print(f"Warning: Could not convert {col} to {dtype}: {e}")
            
            # Add latitude/longitude if missing
            if 'latitude' not in self.shops.columns:
                self.shops['latitude'] = 27.7172  # Default to Kathmandu coordinates
            if 'longitude' not in self.shops.columns:
                self.shops['longitude'] = 85.3240  # Default to Kathmandu coordinates
            
            # Apply float types to coordinates
            coordinate_dtypes = {
                'latitude': float,
                'longitude': float
            }
            
            for col, dtype in coordinate_dtypes.items():
                if col in self.shops.columns:
                    try:
                        self.shops[col] = self.shops[col].astype(dtype)
                    except Exception as e:
                        print(f"Warning: Could not convert {col} to {dtype}: {e}")
            
            print(f"✅ Shops data loaded with columns: {list(self.shops.columns)}")
            
            print("Loading customers...")
            # Check if customers file exists and has data
            if os.path.exists(self.customers_path):
                self.customers = pd.read_csv(self.customers_path)
                print(f"Customers columns: {list(self.customers.columns)}")
                
                # If customers file doesn't have customer_id, create from transactions
                if 'customer_id' not in self.customers.columns:
                    print("Creating customer profiles from transaction data...")
                    unique_customers = transactions['customer_id'].unique()
                    if self.customers['customer_id'].dtype != object or not self.customers['customer_id'].iloc[0].startswith('CUST_'):
                        self.customers['customer_id'] = self.customers['customer_id'].apply(lambda x: f"CUST_{int(x):06d}")
                    # ...existing code...
                    self.customers = pd.DataFrame({
                        'customer_id': unique_customers,
                        'gender': 'Unknown',
                        'age': 30,  # Default age
                        'city': 'Unknown',
                        'preferred_categories': '[]',
                        'avg_monthly_spending': 0.0,
                        'visits_per_month': 1.0
                    })
                
                self.customers = self.customers.astype({
                    'customer_id': str,
                    'gender': str,
                    'age': int,
                    'city': str,
                    'preferred_categories': str,
                    'avg_monthly_spending': float,
                    'visits_per_month': float
                })
            else:
                # Create customers from transactions if file doesn't exist
                print("Customer file not found. Creating customer profiles from transaction data...")
                unique_customers = transactions['customer_id'].unique()
                if 'preferred_categories' in self.customers.columns:
                    self.customers['preferred_categories'] = self.customers['preferred_categories'].apply(
                        lambda x: [cat.strip() for cat in str(x).split(',')] if pd.notnull(x) else []
                    )
                self.customers = pd.DataFrame({
                    'customer_id': unique_customers,
                    'gender': 'Unknown',
                    'age': 30,
                    'city': 'Unknown',
                    'preferred_categories': '[]',
                    'avg_monthly_spending': 0.0,
                    'visits_per_month': 1.0
                })
            
            # Clean all ID columns to ensure consistency
            print("Cleaning ID columns...")
            for df, id_cols in [
                (transactions, ['customer_id', 'product_id', 'shop_id', 'transaction_id']),
                (self.customers, ['customer_id']),
                (self.products, ['product_id']),
                (self.shops, ['shop_id'])
            ]:
                for col in id_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.strip()
            
            print("Merging datasets...")
            # Merge transaction data with error handling
            merged_data = transactions.copy()
            
            # Merge with products
            before_merge = len(merged_data)
            merged_data = merged_data.merge(self.products, on='product_id', how='left')
            print(f"After products merge: {len(merged_data)} rows (was {before_merge})")
            
            # Merge with shops - rename city column first to avoid conflicts
            shops_renamed = self.shops.copy()
            shops_renamed.rename(columns={'city': 'shop_city'}, inplace=True)
            
            before_merge = len(merged_data)
            merged_data = merged_data.merge(shops_renamed, on='shop_id', how='left')
            print(f"After shops merge: {len(merged_data)} rows (was {before_merge})")
            
            # Merge with customers - rename city column first to avoid conflicts
            customers_renamed = self.customers.copy()
            customers_renamed.rename(columns={'city': 'customer_city'}, inplace=True)
            
            before_merge = len(merged_data)
            merged_data = merged_data.merge(customers_renamed, on='customer_id', how='left')
            print(f"After customers merge: {len(merged_data)} rows (was {before_merge})")
            
            # Handle missing values after merge
            missing_products = merged_data['product_name'].isnull().sum()
            missing_shops = merged_data['shop_name'].isnull().sum()
            missing_customers = merged_data['gender'].isnull().sum()
            
            if missing_products > 0:
                print(f"WARNING: {missing_products} transactions have missing product info")
            if missing_shops > 0:
                print(f"WARNING: {missing_shops} transactions have missing shop info")
            if missing_customers > 0:
                print(f"WARNING: {missing_customers} transactions have missing customer info")
            
            # Drop rows with critical missing data
            merged_data = merged_data.dropna(subset=['transaction_time'])
            
            self.data = merged_data
            print(f"✅ Loaded {len(self.data)} merged records")
            
            # Prepare monthly data and features
            self.prepare_monthly_data()
            self.create_features()
            self.create_customer_profiles()
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print("Full traceback:")
            print(traceback.format_exc())
            raise ValueError(f"Error loading data: {str(e)}")
    
    def prepare_monthly_data(self):
        """Convert daily transactions to monthly aggregated sales data"""
        if self.data is None:
            raise ValueError("Data not loaded. Call load_and_prepare_data() first.")
            
        print("Preparing monthly sales data...")
        
        # Create year-month period
        self.data['year_month'] = self.data['transaction_time'].dt.to_period('M')
        
        # Product-shop level aggregation
        product_shop_monthly = self.data.groupby(
            ['product_id', 'shop_id', 'year_month']
        ).agg({
            'quantity': 'sum',
            'total_amount': 'sum',
            'unit_price': 'mean',
            'product_name': 'first',
            'category': 'first',
            'shop_city': 'first',  # Changed from 'city' to 'shop_city'
            'standard_price': 'first'
        }).reset_index()
        
        # Check if customer_id exists in the data before using it
        if 'customer_id' in self.data.columns:
            # Customer level aggregation
            customer_monthly = self.data.groupby(
                ['customer_id', 'year_month']
            ).agg({
                'quantity': 'sum',
                'total_amount': 'sum',
                'product_id': pd.Series.nunique
            }).reset_index()
            
            # Rename columns
            customer_monthly.rename(columns={
                'quantity': 'customer_monthly_quantity',
                'total_amount': 'customer_monthly_spend',
                'product_id': 'unique_products_purchased'
            }, inplace=True)
            
            # Add customer_id to product_shop_monthly for merging
            # First, we need to get customer_id for each product-shop-month combination
            customer_product_shop = self.data.groupby(
                ['product_id', 'shop_id', 'year_month']
            )['customer_id'].first().reset_index()
            
            # Merge customer_id into product_shop_monthly
            product_shop_monthly = product_shop_monthly.merge(
                customer_product_shop,
                on=['product_id', 'shop_id', 'year_month'],
                how='left'
            )
            
            # Merge customer metrics
            self.monthly_data = product_shop_monthly.merge(
                customer_monthly,
                on=['customer_id', 'year_month'],
                how='left'
            )
        else:
            print("WARNING: customer_id not found in data. Creating monthly data without customer metrics...")
            # Create dummy customer columns
            product_shop_monthly['customer_id'] = 'UNKNOWN'
            product_shop_monthly['customer_monthly_quantity'] = product_shop_monthly['quantity']
            product_shop_monthly['customer_monthly_spend'] = product_shop_monthly['total_amount']
            product_shop_monthly['unique_products_purchased'] = 1
            
            self.monthly_data = product_shop_monthly
        
        # Rename columns for consistency
        self.monthly_data.rename(columns={
            'quantity': 'monthly_quantity',
            'total_amount': 'monthly_revenue',
            'unit_price': 'avg_price'
        }, inplace=True)
        
        print(f"✅ Created {len(self.monthly_data)} monthly records")
        print(f"Monthly data columns: {list(self.monthly_data.columns)}")
        return self.monthly_data
    
    def create_features(self):
        """Create features for sales prediction and recommendations"""
        if self.monthly_data is None:
            raise ValueError("Monthly data not prepared. Call prepare_monthly_data() first.")
            
        print("Creating features...")
        
        # Convert period to timestamp
        self.monthly_data['month_date'] = self.monthly_data['year_month'].dt.to_timestamp()
        self.monthly_data['month'] = self.monthly_data['month_date'].dt.month
        self.monthly_data['year'] = self.monthly_data['month_date'].dt.year
        
        # Sales prediction features
        self.monthly_data['last_month_qty'] = self.monthly_data.groupby(
            ['product_id', 'shop_id']
        )['monthly_quantity'].shift(1)
        
        self.monthly_data['last_2_months_qty'] = self.monthly_data.groupby(
            ['product_id', 'shop_id']
        )['monthly_quantity'].shift(2)
        
        self.monthly_data['last_3_months_qty'] = self.monthly_data.groupby(
            ['product_id', 'shop_id']
        )['monthly_quantity'].shift(3)
        
        self.monthly_data['avg_last_3_months'] = self.monthly_data[
            ['last_month_qty', 'last_2_months_qty', 'last_3_months_qty']
        ].mean(axis=1)
        
        self.monthly_data['trend'] = self.monthly_data['last_month_qty'] - self.monthly_data['last_2_months_qty']
        self.monthly_data['price_difference'] = self.monthly_data['avg_price'] - self.monthly_data['standard_price']
        
        # Seasonal features
        self.monthly_data['is_holiday_month'] = self.monthly_data['month'].isin([1, 4, 10, 11, 12]).astype(int)
        self.monthly_data['is_summer'] = self.monthly_data['month'].isin([3, 4, 5, 6]).astype(int)
        
        # Customer behavior features
        self.monthly_data['purchase_frequency'] = self.monthly_data.groupby(
            'customer_id'
        )['year_month'].transform('count')
        
        self.monthly_data['avg_basket_size'] = (
            self.monthly_data['customer_monthly_quantity'] / 
            self.monthly_data['purchase_frequency']
        )
        
        # Encoding
        self.monthly_data['category_code'] = pd.Categorical(self.monthly_data['category']).codes
        self.monthly_data['shop_city_code'] = pd.Categorical(self.monthly_data['shop_city']).codes  # Changed from 'city_code'
        
        # Drop NA from lags
        self.monthly_data = self.monthly_data.dropna(
            subset=['last_month_qty', 'last_2_months_qty', 'last_3_months_qty']
        )
        
        print(f"✅ Created feature set with {len(self.monthly_data)} rows")
        return self.monthly_data
    
    def create_customer_profiles(self):
        """Create detailed customer profiles for recommendations"""
        if self.data is None:
            raise ValueError("Data not loaded. Call load_and_prepare_data() first.")
            
        print("Creating customer profiles...")
        
        # Handle preferred_categories which might be stored as JSON string
        if 'preferred_categories' in self.data.columns:
            try:
                # Try to parse as JSON if it's stringified
                self.data['preferred_categories'] = self.data['preferred_categories'].apply(
                    lambda x: json.loads(x) if isinstance(x, str) else x
                )
            except:
                # If parsing fails, keep as is
                pass
    
        self.customer_profiles = self.data.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'quantity': 'sum',
            'product_id': pd.Series.nunique,
            'shop_id': pd.Series.nunique,
            'transaction_time': ['min', 'max'],
            'gender': 'first',
            'age': 'first',
            'customer_city': 'first',  # Changed from 'city' to 'customer_city'
            'preferred_categories': 'first',
            'avg_monthly_spending': 'first',
            'visits_per_month': 'first'
        })
        
        # Flatten multi-index columns
        self.customer_profiles.columns = ['_'.join(col).strip() for col in self.customer_profiles.columns.values]
        
        # Calculate additional metrics
        self.customer_profiles['tenure_days'] = (
            pd.to_datetime(self.customer_profiles['transaction_time_max']) - 
            pd.to_datetime(self.customer_profiles['transaction_time_min'])
        ).dt.days
        
        self.customer_profiles['avg_basket_size'] = (
            self.customer_profiles['quantity_sum'] / 
            self.customer_profiles['total_amount_count']
        )
        
        # Automatically perform customer segmentation
        print("Performing customer segmentation...")
        self.perform_customer_segmentation()
        
        print(f"✅ Created profiles for {len(self.customer_profiles)} customers")
        return self.customer_profiles
    
    def set_subscription(self, plan='free'):
        """Set the subscription plan"""
        if plan.lower() not in self.subscription_plans:
            raise ValueError(f"Invalid subscription plan. Available: {list(self.subscription_plans.keys())}")
        self.current_subscription = plan.lower()
        print(f"Subscription set to: {self.current_subscription}")
        return True
    
    def get_subscription_info(self):
        """Get current subscription details"""
        return {
            'current_plan': self.current_subscription,
            'features': self.subscription_plans[self.current_subscription],
            'price': self.subscription_plans[self.current_subscription]['price']
        }
    
    def get_available_combinations(self):
        """Get all available product-shop combinations with historical data"""
        if self.monthly_data is None:
            return pd.DataFrame()
        
        try:
            combinations = self.monthly_data.groupby(['product_id', 'shop_id']).agg({
                'monthly_quantity': ['count', 'mean', 'sum'],
                'product_name': 'first',
                'shop_city': 'first'
            }).reset_index()
            
            # Flatten column names
            combinations.columns = ['product_id', 'shop_id', 'data_points', 'avg_monthly_qty', 
                                  'total_qty', 'product_name', 'shop_city'
            ]
            
            return combinations.sort_values('data_points', ascending=False)
        except Exception as e:
            print(f"Error getting available combinations: {e}")
            return pd.DataFrame()
    
    def is_ready_for_training(self):
        """Check if pipeline is ready for model training"""
        if self.monthly_data is None:
            return False, "Monthly data not prepared"
        
        if len(self.monthly_data) == 0:
            return False, "Monthly data is empty"
        
        # Check if required columns exist
        missing_features = [col for col in self.feature_columns if col not in self.monthly_data.columns]
        if missing_features:
            return False, f"Missing feature columns: {missing_features}"
        
        # Check if we have enough data points
        if len(self.monthly_data) < 10:
            return False, f"Not enough data points for training: {len(self.monthly_data)}"
        
        return True, "Ready for training"
    
    def train_model(self, target_col='monthly_quantity'):
        """Train sales prediction model"""
        # Check if ready for training
        ready, message = self.is_ready_for_training()
        if not ready:
            raise ValueError(f"Cannot train model: {message}")
        
        print("Training sales prediction model...")
        
        try:
            X = self.monthly_data[self.feature_columns]
            y = self.monthly_data[target_col]
            
            # Remove any infinite or NaN values
            mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
            X = X[mask]
            y = y[mask]
            
            if len(X) == 0:
                raise ValueError("No valid data points after removing NaN/infinite values")
            
            # Check if we have enough data for train/test split
            if len(X) < 4:
                # If very little data, train on all data
                print("Warning: Very little data. Training on all available data.")
                X_train, X_test, y_train, y_test = X, X, y, y
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
            
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            print(f"✅ Model trained. RMSE: {rmse:.2f}, R²: {r2:.2f}")
            
            return {
                'model': self.model,
                'rmse': rmse,
                'r2': r2,
                'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_)),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            print(f"Error training model: {e}")
            self.is_trained = False
            raise ValueError(f"Model training failed: {str(e)}")
    
    def get_model_metrics(self):
        """Get model evaluation metrics"""
        if not self.is_trained or self.model is None:
            # Try to train the model if data is available
            if self.monthly_data is not None and len(self.monthly_data) > 0:
                print("Model not trained. Training now...")
                try:
                    self.train_model()
                except Exception as e:
                    print(f"Error training model: {e}")
                    return {
                        'mae': 0.0,
                        'rmse': 0.0,
                        'r2': 0.0,
                        'mape': 0.0,
                        'error': f"Cannot train model: {str(e)}"
                    }
            else:
                return {
                    'mae': 0.0,
                    'rmse': 0.0,
                    'r2': 0.0,
                    'mape': 0.0,
                    'error': "No data available for training"
                }
        
        try:
            X = self.monthly_data[self.feature_columns]
            y = self.monthly_data['monthly_quantity']
            
            # Remove any NaN or infinite values
            mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
            X_clean = X[mask]
            y_clean = y[mask]
            
            if len(y_clean) == 0:
                return {
                    'mae': 0.0,
                    'rmse': 0.0,
                    'r2': 0.0,
                    'mape': 0.0,
                    'error': "No valid data for metrics calculation"
                }
            
            y_pred = self.model.predict(X_clean)
            
            mae = mean_absolute_error(y_clean, y_pred)
            rmse = np.sqrt(mean_squared_error(y_clean, y_pred))
            r2 = r2_score(y_clean, y_pred)
            
            # Handle division by zero in MAPE calculation
            mape = np.mean(np.abs((y_clean - y_pred) / np.where(y_clean == 0, 1, y_clean))) * 100
            
            return {'mae': mae, 'rmse': rmse, 'r2': r2, 'mape': mape}
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                'mae': 0.0,
                'rmse': 0.0,
                'r2': 0.0,
                'mape': 0.0,
                'error': f"Error calculating metrics: {str(e)}"
            }
    
    def predict_for_product_shop(self, product_id, shop_id):
        """Predict sales for a specific product-shop combination"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_model() first.")
    
        # Convert inputs to strings to match data types
        product_id = str(product_id)
        shop_id = str(shop_id)
    
        # Get historical data for this product-shop combination
        historical_data = self.monthly_data[
            (self.monthly_data['product_id'] == product_id) & 
            (self.monthly_data['shop_id'] == shop_id)
        ].sort_values('year_month')
    
        if len(historical_data) == 0:
            # No historical data - try to predict based on similar products/shops
            return self._predict_for_new_combination(product_id, shop_id)
    
        # Get the most recent record for prediction
        latest_record = historical_data.iloc[-1:].copy()
    
        # Create features for prediction
        try:
            features = latest_record[self.feature_columns]
            prediction = self.model.predict(features)[0]
        
            return {
                'predicted_quantity': max(0, prediction),  # Ensure non-negative
                'last_actual': latest_record['monthly_quantity'].iloc[0],
                'last_date': str(latest_record['year_month'].iloc[0]),
                'confidence': 'high',
                'historical_points': len(historical_data)
            }
        except Exception as e:
            print(f"Error predicting with historical data: {e}")
            return self._predict_for_new_combination(product_id, shop_id)

    def _predict_for_new_combination(self, product_id, shop_id):
        """Predict for product-shop combinations with no historical data"""
        product_id = str(product_id)
        shop_id = str(shop_id)
    
        # Get product info
        product_info = self.products[self.products['product_id'] == product_id]
        if len(product_info) == 0:
            return {
                'predicted_quantity': 10,  # Default fallback
                'last_actual': 0,
                'last_date': 'No data',
                'confidence': 'very_low',
                'historical_points': 0,
                'note': 'Product not found in catalog - using default estimate'
            }
    
        product_category = product_info['category'].iloc[0]
    
        # Get average sales for this product across all shops
        product_avg = self.monthly_data[
            self.monthly_data['product_id'] == product_id
        ]['monthly_quantity'].mean()
    
        # Get average sales for this shop across all products
        shop_avg = self.monthly_data[
            self.monthly_data['shop_id'] == shop_id
        ]['monthly_quantity'].mean()
    
        # Get average sales for this category at this shop
        category_shop_avg = self.monthly_data[
            (self.monthly_data['category'] == product_category) &
            (self.monthly_data['shop_id'] == shop_id)
        ]['monthly_quantity'].mean()
    
        # Get overall category average
        category_avg = self.monthly_data[
            self.monthly_data['category'] == product_category
        ]['monthly_quantity'].mean()
    
        # Get overall average
        overall_avg = self.monthly_data['monthly_quantity'].mean()
    
        # Use weighted average as prediction (priority order)
        prediction = None
        confidence = 'very_low'
        note = 'No historical data'
    
        if not pd.isna(product_avg):
            prediction = product_avg
            confidence = 'medium'
            note = f'Based on average sales of this product: {prediction:.1f} units/month'
        elif not pd.isna(category_shop_avg):
            prediction = category_shop_avg
            confidence = 'low'
            note = f'Based on {product_category} sales at this shop: {prediction:.1f} units/month'
        elif not pd.isna(shop_avg):
            prediction = shop_avg
            confidence = 'low'
            note = f'Based on average sales at this shop: {prediction:.1f} units/month'
        elif not pd.isna(category_avg):
            prediction = category_avg
            confidence = 'very_low'
            note = f'Based on {product_category} category average: {prediction:.1f} units/month'
        else:
            prediction = overall_avg if not pd.isna(overall_avg) else 10  # Default fallback
            confidence = 'very_low'
            note = f'Based on overall average: {prediction:.1f} units/month'
    
        return {
            'predicted_quantity': max(0, prediction),
            'last_actual': 0,
            'last_date': 'No historical data',
            'confidence': confidence,
            'historical_points': 0,
            'note': note
        }

    def get_product_shop_history(self, product_id, shop_id):
        """Get historical sales data for a product-shop combination"""
        product_id = str(product_id)
        shop_id = str(shop_id)
    
        historical_data = self.monthly_data[
            (self.monthly_data['product_id'] == product_id) & 
            (self.monthly_data['shop_id'] == shop_id)
        ].sort_values('year_month')
    
        if len(historical_data) == 0:
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=['year_month', 'monthly_quantity'])
    
        return historical_data[['year_month', 'monthly_quantity']].copy()

    def run_scenario(self, product_id, shop_id, price_change, marketing_boost, season):
        """Run what-if scenario analysis"""
        try:
            # Get base prediction
            base_prediction = self.predict_for_product_shop(product_id, shop_id)
            base_qty = base_prediction['predicted_quantity']
        
            # Apply scenario adjustments
            adjusted_qty = base_qty
        
            # Price elasticity (simplified model)
            # Negative elasticity: higher prices = lower demand
            price_elasticity = -0.5  # Assume -0.5 elasticity
            adjusted_qty *= (1 + price_change * price_elasticity)
        
            # Marketing boost effect
            # Scale around baseline of 3 (1-5 scale)
            marketing_effect = (marketing_boost - 3) * 0.1  # 10% impact per level
            adjusted_qty *= (1 + marketing_effect)
        
            # Seasonal adjustment
            seasonal_multipliers = {
                'normal': 1.0,
                'holiday': 1.3,    # 30% boost during holidays
                'summer': 0.8      # 20% drop in summer (depends on product)
            }
            adjusted_qty *= seasonal_multipliers.get(season, 1.0)
        
            # Ensure non-negative
            adjusted_qty = max(0, adjusted_qty)
        
            # Calculate changes
            change = adjusted_qty - base_qty
            change_pct = (change / base_qty * 100) if base_qty > 0 else 0
        
            return {
                'original': base_qty,
                'predicted': adjusted_qty,
                'change': change,
                'change_pct': change_pct,
                'confidence': base_prediction.get('confidence', 'unknown'),
                'note': base_prediction.get('note', '')
            }
        
        except Exception as e:
            print(f"Error in scenario analysis: {e}")
            return {
                'original': 0,
                'predicted': 0,
                'change': 0,
                'change_pct': 0,
                'error': str(e)
            }

    def _generate_shopkeeper_recommendations(self):
        """Generate recommendations for shopkeepers"""
        recommendations = []
    
        if self.monthly_data is None or not self.is_trained:
            return recommendations
    
        try:
            # Get recent performance for each shop
            recent_data = self.monthly_data.groupby(['shop_id', 'product_id']).agg({
                'monthly_quantity': 'mean',
                'product_name': 'first',
                'category': 'first'
            }).reset_index()
        
            for shop_id in recent_data['shop_id'].unique()[:5]:  # Limit to first 5 shops
                shop_data = recent_data[recent_data['shop_id'] == shop_id]
            
                if len(shop_data) == 0:
                    continue
            
                # Find underperforming products (bottom 30%)
                threshold = shop_data['monthly_quantity'].quantile(0.3)
                underperforming = shop_data[shop_data['monthly_quantity'] <= threshold]
            
                # Generate recommendations for underperforming products
                for _, product in underperforming.head(3).iterrows():
                    recommendations.append({
                        'shop_id': shop_id,
                        'product_id': product['product_id'],
                        'product_name': product['product_name'],
                        'type': 'increase_marketing',
                        'reason': f'Low sales: {product["monthly_quantity"]:.1f} units/month',
                        'current_avg': product['monthly_quantity'],
                        'predicted': product['monthly_quantity'] * 1.3,
                        'priority': 'high' if product['monthly_quantity'] < threshold * 0.5 else 'medium'
                    })
    
        except Exception as e:
            print(f"Error generating shopkeeper recommendations: {e}")
    
        return recommendations

    def _generate_customer_recommendations(self):
        """Generate customer recommendations based on purchase history and shop interactions"""
        recommendations = []

        # First, ensure we have transaction data
        if self.data is None or len(self.data) == 0:
            print("DEBUG: No transaction data available")
            return recommendations

        # Check if customer_id exists in data
        if 'customer_id' not in self.data.columns:
            print("DEBUG: No customer_id column in transaction data")
            return recommendations

        print(f"DEBUG: Transaction data has {len(self.data)} records with {self.data['customer_id'].nunique()} unique customers")

        try:
            # Get customer purchase behavior directly from transaction data
            customer_behavior = self.data.groupby('customer_id').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'quantity': 'sum',
                'product_id': ['nunique', list],
                'shop_id': ['nunique', list],
                'category': [list, lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown']
            }).reset_index()
            
            # Flatten column names
            customer_behavior.columns = [
                'customer_id', 'total_spending', 'avg_spending', 'transaction_count', 
                'total_quantity', 'unique_products', 'product_list', 
                'unique_shops', 'shop_list', 'category_list', 'top_category'
            ]
            
            # Sort by total spending to get top customers
            customer_behavior = customer_behavior.sort_values('total_spending', ascending=False)
            
            print(f"DEBUG: Processed {len(customer_behavior)} customers for recommendations")
            if len(customer_behavior) > 0:
                print(f"DEBUG: Top customer spent: {customer_behavior['total_spending'].iloc[0]:.2f}")
            
            # INCREASED: Generate recommendations for more customers (top 25 instead of 10)
            for idx, customer in customer_behavior.head(25).iterrows():
                customer_id = customer['customer_id']
                purchased_products = set(customer['product_list'])
                visited_shops = set(customer['shop_list'])
                top_category = customer['top_category']
                
                print(f"DEBUG: Processing customer {customer_id} - purchased {len(purchased_products)} products, top category: {top_category}")
                
                # Strategy 1: Recommend MORE products from favorite category (increased from 2 to 5)
                category_products = self.products[self.products['category'] == top_category]
                category_recs = 0
                
                for _, product in category_products.iterrows():
                    if product['product_id'] not in purchased_products and category_recs < 5:  # INCREASED
                        # Find which shops sell this product
                        product_shops = self.data[self.data['product_id'] == product['product_id']]['shop_id'].unique()
                        
                        # Prefer shops the customer has visited
                        preferred_shop = None
                        for shop in product_shops:
                            if shop in visited_shops:
                                preferred_shop = shop
                                break
                        
                        if preferred_shop is None and len(product_shops) > 0:
                            preferred_shop = product_shops[0]  # Any shop that sells it
                        
                        if preferred_shop:
                            recommendations.append({
                                'customer_id': customer_id,
                                'product_id': product['product_id'],
                                'product_name': product['product_name'],
                                'category': product['category'],
                                'recommended_shop': preferred_shop,
                                'reason': f'You frequently buy {top_category} products. Try this new item!',
                                'confidence': 'high',
                                'recommendation_type': 'category_preference'
                            })
                            category_recs += 1

                # Strategy 2: Recommend MORE popular products from visited shops (increased from 1 to 3)
                shop_recs = 0
                for shop_id in list(visited_shops)[:5]:  # Check more shops
                    # Get popular products in this shop that customer hasn't bought
                    shop_products = self.data[self.data['shop_id'] == shop_id].groupby('product_id').agg({
                        'quantity': 'sum',
                        'product_name': 'first',
                        'category': 'first'
                    }).sort_values('quantity', ascending=False)
                    
                    for product_id, product_data in shop_products.head(10).iterrows():  # Check more products
                        if product_id not in purchased_products and shop_recs < 3:  # INCREASED
                            recommendations.append({
                                'customer_id': customer_id,
                                'product_id': product_id,
                                'product_name': product_data['product_name'],
                                'category': product_data['category'],
                                'recommended_shop': shop_id,
                                'reason': f'Popular item at a shop you visit frequently',
                                'confidence': 'medium',
                                'recommendation_type': 'shop_popularity'
                            })
                            shop_recs += 1
                            if shop_recs >= 3:  # Break when we have enough from this strategy
                                break

                # Strategy 3: ENHANCED Cross-category recommendations
                # Get customer's secondary categories
                if len(customer['category_list']) > 1:
                    customer_categories = pd.Series(customer['category_list']).value_counts()
                    cross_recs = 0
                    
                    # Recommend from secondary categories the customer hasn't explored much
                    for category in customer_categories.index[1:4]:  # Skip top category, get next 3
                        if cross_recs >= 3:  # INCREASED
                            break
                        
                        category_products = self.products[self.products['category'] == category]
                        for _, product in category_products.head(5).iterrows():
                            if product['product_id'] not in purchased_products and cross_recs < 3:
                                # Find a shop they've visited that sells this
                                product_shops = self.data[self.data['product_id'] == product['product_id']]['shop_id'].unique()
                                preferred_shop = None
                                
                                for shop in product_shops:
                                    if shop in visited_shops:
                                        preferred_shop = shop
                                        break
                                
                                if preferred_shop is None and len(product_shops) > 0:
                                    preferred_shop = product_shops[0]
                                
                                if preferred_shop:
                                    recommendations.append({
                                        'customer_id': customer_id,
                                        'product_id': product['product_id'],
                                        'product_name': product['product_name'],
                                        'category': product['category'],
                                        'recommended_shop': preferred_shop,
                                        'reason': f'Explore {category} products - you\'ve shown some interest in this category',
                                        'confidence': 'medium',
                                        'recommendation_type': 'category_expansion'
                                    })
                                    cross_recs += 1
                                    break  # One per category

                # Strategy 4: NEW - Collaborative filtering based recommendations
                similar_customers = customer_behavior[
                    (customer_behavior['top_category'] == top_category) & 
                    (customer_behavior['customer_id'] != customer_id)
                ].head(5)  # Get more similar customers
                
                collab_recs = 0
                for _, similar_customer in similar_customers.iterrows():
                    if collab_recs >= 2:  # INCREASED
                        break
                    
                    similar_products = set(similar_customer['product_list'])
                    # Find products they bought that current customer hasn't
                    new_products = similar_products - purchased_products
                    
                    for product_id in list(new_products)[:3]:  # Check more products
                        if collab_recs < 2:
                            product_info = self.products[self.products['product_id'] == product_id]
                            if len(product_info) > 0:
                                product_shops = self.data[self.data['product_id'] == product_id]['shop_id'].unique()
                                preferred_shop = product_shops[0] if len(product_shops) > 0 else 'Any'
                                
                                recommendations.append({
                                    'customer_id': customer_id,
                                    'product_id': product_id,
                                    'product_name': product_info['product_name'].iloc[0],
                                    'category': product_info['category'].iloc[0],
                                    'recommended_shop': preferred_shop,
                                    'reason': 'Customers with similar preferences also bought this',
                                    'confidence': 'medium',
                                    'recommendation_type': 'collaborative_filtering'
                                })
                                collab_recs += 1
                                break

                # Strategy 5: NEW - Trending products recommendations
                # Get trending products (high sales in recent periods)
                if self.monthly_data is not None:
                    trending_products = self.monthly_data.groupby('product_id').agg({
                        'monthly_quantity': 'sum',
                        'product_name': 'first',
                        'category': 'first'
                    }).sort_values('monthly_quantity', ascending=False).head(20)
                    
                    trend_recs = 0
                    for product_id, product_data in trending_products.iterrows():
                        if product_id not in purchased_products and trend_recs < 2:  # NEW strategy
                            product_shops = self.data[self.data['product_id'] == product_id]['shop_id'].unique()
                            preferred_shop = product_shops[0] if len(product_shops) > 0 else 'Any'
                            
                            recommendations.append({
                                'customer_id': customer_id,
                                'product_id': product_id,
                                'product_name': product_data['product_name'],
                                'category': product_data['category'],
                                'recommended_shop': preferred_shop,
                                'reason': 'Trending product - popular among all customers',
                                'confidence': 'low',
                                'recommendation_type': 'trending'
                            })
                            trend_recs += 1

            print(f"DEBUG: Generated {len(recommendations)} total recommendations")
            
            # If still no recommendations, create MORE basic ones
            if len(recommendations) == 0:
                print("DEBUG: No personalized recommendations generated, creating MORE basic ones")
                recommendations = self._create_enhanced_basic_recommendations()
            
            return recommendations
        
        except Exception as e:
            print(f"ERROR in customer recommendations: {e}")
            import traceback
            print(traceback.format_exc())
            return self._create_enhanced_basic_recommendations()

    def _create_enhanced_basic_recommendations(self):
        """Create MORE basic recommendations when personalized ones fail"""
        recommendations = []
        
        try:
            if self.data is None or len(self.data) == 0:
                return recommendations
            
            print(f"DEBUG: Creating enhanced basic recommendations from {len(self.data)} transactions")
            
            # Get top 15 products by sales volume (INCREASED from 5)
            top_products = self.data.groupby('product_id').agg({
                'quantity': 'sum',
                'product_name': 'first',
                'category': 'first',
                'shop_id': lambda x: x.value_counts().index[0]  # Most popular shop for this product
            }).sort_values('quantity', ascending=False).head(15)  # INCREASED
            
            print(f"DEBUG: Found {len(top_products)} top products")
            
            # Get top 10 customers by transaction count (INCREASED from 3)
            top_customers = self.data['customer_id'].value_counts().head(10)  # INCREASED
            
            print(f"DEBUG: Found {len(top_customers)} top customers")
            
            # Create MORE combinations
            for i, (customer_id, _) in enumerate(top_customers.items()):
                # Recommend multiple products per customer (INCREASED from 1 to 3)
                for j in range(min(3, len(top_products))):  # Up to 3 products per customer
                    if j < len(top_products):
                        product_id = top_products.index[j]
                        product_data = top_products.iloc[j]
                        
                        recommendations.append({
                            'customer_id': customer_id,
                            'product_id': product_id,
                            'product_name': product_data['product_name'],
                            'category': product_data['category'],
                            'recommended_shop': product_data['shop_id'],
                            'reason': f'Top selling {product_data["category"]} product',
                            'confidence': 'low',
                            'recommendation_type': 'popularity_based'
                        })
        
            # Add category-based recommendations for diversity
            categories = self.products['category'].unique()
            for customer_id in top_customers.index[:5]:  # Top 5 customers
                for category in categories[:3]:  # Top 3 categories
                    category_products = self.products[self.products['category'] == category]
                    if len(category_products) > 0:
                        product = category_products.iloc[0]  # Get first product from category
                        
                        recommendations.append({
                            'customer_id': customer_id,
                            'product_id': product['product_id'],
                            'product_name': product['product_name'],
                            'category': product['category'],
                            'recommended_shop': 'Any',
                            'reason': f'Discover {category} products',
                            'confidence': 'low',
                            'recommendation_type': 'category_discovery'
                        })
        
            print(f"DEBUG: Created {len(recommendations)} enhanced basic recommendations")
            return recommendations
        
        except Exception as e:
            print(f"ERROR in enhanced basic recommendations: {e}")
            return []

    def perform_customer_segmentation(self, n_clusters=4):
        """Perform customer segmentation using K-means clustering"""
        if self.customer_profiles is None or len(self.customer_profiles) == 0:
            print("No customer profiles available for segmentation")
            return False
        
        try:
            # Select features for clustering
            features_for_clustering = []
            
            # Check which columns exist and use them
            potential_features = [
                'total_amount_sum', 'total_amount_mean', 'total_amount_count',
                'quantity_sum', 'product_id_nunique', 'shop_id_nunique',
                'avg_basket_size', 'tenure_days'
            ]
            
            for feature in potential_features:
                if feature in self.customer_profiles.columns:
                    features_for_clustering.append(feature)
        
            if len(features_for_clustering) == 0:
                print("No suitable features found for clustering")
                return False
            
            print(f"Using features for segmentation: {features_for_clustering}")
            
            # Prepare data for clustering
            clustering_data = self.customer_profiles[features_for_clustering].copy()
            
            # Handle missing values
            clustering_data = clustering_data.fillna(clustering_data.mean())
            
            # Normalize the features
            scaler = StandardScaler()
            clustering_data_scaled = scaler.fit_transform(clustering_data)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(clustering_data_scaled)
            
            # Add segment labels to customer profiles
            self.customer_profiles['segment'] = clusters
            
            # Create meaningful segment names based on characteristics
            segment_names = {}
            for segment in range(n_clusters):
                segment_data = self.customer_profiles[self.customer_profiles['segment'] == segment]
                
                # Calculate segment characteristics
                avg_spending = segment_data['total_amount_sum'].mean() if 'total_amount_sum' in segment_data.columns else 0
                avg_frequency = segment_data['total_amount_count'].mean() if 'total_amount_count' in segment_data.columns else 0
                
                # Assign names based on spending and frequency
                if avg_spending > self.customer_profiles['total_amount_sum'].median() and avg_frequency > self.customer_profiles['total_amount_count'].median():
                    segment_names[segment] = 'High Value'
                elif avg_spending > self.customer_profiles['total_amount_sum'].median():
                    segment_names[segment] = 'High Spender'
                elif avg_frequency > self.customer_profiles['total_amount_count'].median():
                    segment_names[segment] = 'Frequent Buyer'
                else:
                    segment_names[segment] = 'Casual Shopper'
            
            # Add segment names
            self.customer_profiles['segment_name'] = self.customer_profiles['segment'].map(segment_names)
            
            print(f"✅ Customer segmentation completed with {n_clusters} segments")
            print("Segment distribution:")
            print(self.customer_profiles['segment_name'].value_counts())
            
            return True
            
        except Exception as e:
            print(f"Error in customer segmentation: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def get_segment_analysis(self):
        """Get customer segment analysis"""
        if 'segment' not in self.customer_profiles.columns:
            print("Customer segmentation not performed yet. Running segmentation...")
            success = self.perform_customer_segmentation()
            if not success:
                return {'error': 'Could not perform customer segmentation'}
        
        try:
            segment_analysis = {}
            
            # Overall segment distribution
            segment_distribution = self.customer_profiles['segment_name'].value_counts().to_dict()
            segment_analysis['distribution'] = segment_distribution
            
            # Segment characteristics
            segment_stats = self.customer_profiles.groupby('segment_name').agg({
                'total_amount_sum': ['mean', 'median', 'count'],
                'total_amount_count': 'mean',
                'quantity_sum': 'mean',
                'product_id_nunique': 'mean',
                'shop_id_nunique': 'mean'
            }).round(2)
            
            # Flatten column names
            segment_stats.columns = ['_'.join(col).strip() for col in segment_stats.columns.values]
            segment_analysis['characteristics'] = segment_stats.to_dict('index')
            
            # Revenue by segment
            revenue_by_segment = self.customer_profiles.groupby('segment_name')['total_amount_sum'].sum().to_dict()
            segment_analysis['revenue_by_segment'] = revenue_by_segment
            
            return segment_analysis
            
        except Exception as e:
            print(f"Error in segment analysis: {e}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def get_customer_purchase_summary(self, customer_id):
        """Return a summary of a customer's purchase history."""
        try:
            customer_id = str(customer_id)
            if self.data is None or 'customer_id' not in self.data.columns:
                return {'error': 'No transaction data available'}
            df = self.data[self.data['customer_id'] == customer_id]
            if df.empty:
                return {'error': 'No transactions found for this customer'}
            total_spending = df['total_amount'].sum()
            total_transactions = df['transaction_id'].nunique() if 'transaction_id' in df.columns else len(df)
            avg_transaction_value = df['total_amount'].mean()
            total_items = df['quantity'].sum() if 'quantity' in df.columns else 0
            favorite_category = df['category'].mode().iloc[0] if 'category' in df.columns and not df['category'].isnull().all() else "Unknown"
            unique_shops = df['shop_id'].nunique() if 'shop_id' in df.columns else 0
            return {
                'total_spending': total_spending,
                'total_transactions': total_transactions,
                'avg_transaction_value': avg_transaction_value,
                'total_items': total_items,
                'favorite_category': favorite_category,
                'unique_shops': unique_shops
            }
        except Exception as e:
            return {'error': str(e)}
        
    def get_customer_insights(self):
        """Return summary stats for customer data for UI diagnostics."""
        try:
            total_customers = self.data['customer_id'].nunique() if self.data is not None and 'customer_id' in self.data.columns else 0
            total_transactions = len(self.data) if self.data is not None else 0
            total_products = self.data['product_id'].nunique() if self.data is not None and 'product_id' in self.data.columns else 0
            sample_customer = None
            if total_customers > 0:
                sample_customer = str(self.data['customer_id'].iloc[0])
            return {
                'total_customers': total_customers,
                'total_transactions': total_transactions,
                'total_products': total_products,
                'sample_customer': sample_customer
            }
        except Exception as e:
            return {'error': str(e)}
