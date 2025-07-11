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
                'predicted_quantity': 0,
                'last_actual': 0,
                'last_date': 'No data',
                'confidence': 'very_low',
                'historical_points': 0,
                'note': 'Product not found in catalog'
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

    def get_available_combinations(self):
        """Get all available product-shop combinations with historical data"""
        if self.monthly_data is None:
            return pd.DataFrame()
    
        combinations = self.monthly_data.groupby(['product_id', 'shop_id']).agg({
            'monthly_quantity': ['count', 'mean', 'sum'],
            'product_name': 'first',
            'shop_city': 'first'
        }).reset_index()
    
        # Flatten column names
        combinations.columns = ['product_id', 'shop_id', 'data_points', 'avg_monthly_qty', 
                          'total_qty', 'product_name', 'shop_city']
    
        return combinations.sort_values('data_points', ascending=False)