import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from mlxtend.frequent_patterns import apriori, association_rules
import joblib
import os
from datetime import datetime

class RetailAnalyticsPipeline:
    def __init__(self, transactions_path, products_path, shops_path, customers_path):
        """Initialize pipeline with data paths and automatic data loading"""
        self.transactions_path = transactions_path
        self.products_path = products_path 
        self.shops_path = shops_path
        self.customers_path = customers_path
        
        # Initialize attributes
        self.data = None
        self.monthly_data = None
        self.customer_profiles = None
        self.model = None
        self.is_trained = False
        
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
        
        # Automatically load and prepare data on initialization
        self._load_and_prepare_data()
        self._prepare_monthly_data()
        self._create_features()
        self._create_customer_profiles()
    
    def _load_and_prepare_data(self):
        """PRIVATE: Load all data sources and prepare for analysis"""
        print("Loading and preparing data...")
        
        # Validate files exist
        for path in [self.transactions_path, self.products_path, 
                    self.shops_path, self.customers_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Data file not found: {path}")
        
        # Load all datasets
        transactions = pd.read_csv(self.transactions_path)
        products = pd.read_csv(self.products_path)
        shops = pd.read_csv(self.shops_path)
        customers = pd.read_csv(self.customers_path)
        
        # Merge transaction data
        merged_data = transactions.merge(products, on='product_id', how='left')
        merged_data = merged_data.merge(shops, on='shop_id', how='left')
        merged_data = merged_data.merge(customers, on='customer_id', how='left')
        
        # Convert datetime
        merged_data['transaction_time'] = pd.to_datetime(merged_data['transaction_time'])
        self.data = merged_data.dropna(subset=['transaction_time'])
        
        print(f"✅ Loaded {len(self.data)} merged records")
    
    def _prepare_monthly_data(self):
        """PRIVATE: Convert daily transactions to monthly aggregated sales data"""
        print("Preparing monthly sales data...")
        
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
            'city': 'first',
            'standard_price': 'first'
        }).reset_index()
        
        # Customer level aggregation
        customer_monthly = self.data.groupby(
            ['customer_id', 'year_month']
        ).agg({
            'quantity': 'sum',
            'total_amount': 'sum',
            'product_id': pd.Series.nunique
        }).reset_index()
        
        # Rename columns
        product_shop_monthly.rename(columns={
            'quantity': 'monthly_quantity',
            'total_amount': 'monthly_revenue',
            'unit_price': 'avg_price'
        }, inplace=True)
        
        customer_monthly.rename(columns={
            'quantity': 'customer_monthly_quantity',
            'total_amount': 'customer_monthly_spend',
            'product_id': 'unique_products_purchased'
        }, inplace=True)
        
        # Merge customer metrics back
        self.monthly_data = product_shop_monthly.merge(
            customer_monthly,
            on=['customer_id', 'year_month'],
            how='left'
        )
        
        print(f"✅ Created {len(self.monthly_data)} monthly records")
    
    def _create_features(self):
        """PRIVATE: Create features for sales prediction and recommendations"""
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
        self.monthly_data['city_code'] = pd.Categorical(self.monthly_data['city']).codes
        
        # Drop NA from lags
        self.monthly_data = self.monthly_data.dropna(
            subset=['last_month_qty', 'last_2_months_qty', 'last_3_months_qty']
        )
        
        print(f"✅ Created feature set with {len(self.monthly_data)} rows")
    
    def _create_customer_profiles(self):
        """PRIVATE: Create detailed customer profiles for recommendations"""
        print("Creating customer profiles...")
        
        self.customer_profiles = self.data.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'quantity': 'sum',
            'product_id': pd.Series.nunique,
            'shop_id': pd.Series.nunique,
            'transaction_time': ['min', 'max'],
            'gender': 'first',
            'age': 'first',
            'city': 'first',
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
    
    def set_subscription(self, plan='free'):
        """Set the subscription plan for product owners"""
        if plan.lower() not in self.subscription_plans:
            raise ValueError(f"Invalid subscription plan. Available: {list(self.subscription_plans.keys())}")
        self.current_subscription = plan.lower()
        print(f"Subscription set to: {self.current_subscription}")
        print(f"Available features: {self.subscription_plans[self.current_subscription]['product_owner_features']}")
        return True
    
    def get_subscription_info(self):
        """Get current subscription details"""
        return {
            'current_plan': self.current_subscription,
            'features': self.subscription_plans[self.current_subscription],
            'price': self.subscription_plans[self.current_subscription]['price']
        }
    
    def train_model(self, target_col='monthly_quantity'):
        """PUBLIC: Train sales prediction model (to be called manually)"""
        print("Training sales prediction model...")
        
        features = [
            'last_month_qty', 'last_2_months_qty', 'last_3_months_qty',
            'avg_last_3_months', 'trend', 'price_difference',
            'is_holiday_month', 'is_summer', 'category_code', 'city_code'
        ]
        
        X = self.monthly_data[features]
        y = self.monthly_data[target_col]
        
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
            'feature_importance': dict(zip(features, self.model.feature_importances_))
        }
    
    def predict_next_month(self):
        """Generate predictions for next month"""
        print("Generating next month predictions...")
        
        if not self.model:
            raise ValueError("Model not trained. Call train_model() first.")
            
        features = [
            'last_month_qty', 'last_2_months_qty', 'last_3_months_qty',
            'avg_last_3_months', 'trend', 'price_difference',
            'is_holiday_month', 'is_summer', 'category_code', 'city_code'
        ]
        
        self.monthly_data['predicted_quantity'] = self.model.predict(
            self.monthly_data[features]
        )
        
        print("✅ Predictions generated")
        return self.monthly_data
    
    def get_recommendations(self, user_type):
        """Get recommendations based on user type and subscription"""
        if user_type not in ['product_owner', 'shopkeeper', 'customer']:
            raise ValueError("Invalid user type. Must be 'product_owner', 'shopkeeper', or 'customer'")
            
        if user_type == 'product_owner' and self.current_subscription == 'free':
            print("Showing basic analytics. Upgrade to premium for advanced recommendations.")
            return self._get_basic_analytics()
        elif user_type == 'product_owner' and self.current_subscription == 'premium':
            return self._generate_product_owner_recommendations()
        elif user_type == 'shopkeeper':
            return self._generate_shopkeeper_recommendations()
        elif user_type == 'customer':
            return self._generate_customer_recommendations()
    
    def _get_basic_analytics(self):
        """Generate basic analytics for free tier product owners"""
        print("Generating basic analytics for free tier...")
        
        basic_results = {
            'trend_analysis': self._generate_trend_analysis(),
            'seasonality_charts': self._generate_seasonality_charts(),
            'basic_plots': self._generate_basic_plots(),
            'upgrade_message': 'Upgrade to premium for advanced recommendations and competitor analysis'
        }
        return basic_results
    
    def _generate_trend_analysis(self):
        """Generate basic trend analysis"""
        trend_data = self.monthly_data.groupby('year_month').agg({
            'monthly_quantity': 'sum',
            'monthly_revenue': 'sum'
        }).reset_index()
        
        return {
            'total_sales_trend': trend_data.to_dict('records'),
            'message': 'Basic trend analysis - consider premium for advanced insights'
        }
    
    def _generate_seasonality_charts(self):
        """Generate seasonality analysis"""
        seasonality = self.monthly_data.groupby('month').agg({
            'monthly_quantity': 'mean'
        }).reset_index()
        
        return {
            'seasonal_patterns': seasonality.to_dict('records'),
            'message': 'Basic seasonality analysis'
        }
    
    def _generate_basic_plots(self):
        """Generate basic plot data"""
        category_sales = self.monthly_data.groupby('category').agg({
            'monthly_quantity': 'sum'
        }).reset_index()
        
        city_performance = self.monthly_data.groupby('city').agg({
            'monthly_revenue': 'sum'
        }).reset_index()
        
        return {
            'category_distribution': category_sales.to_dict('records'),
            'geographic_performance': city_performance.to_dict('records')
        }
    
    def _generate_product_owner_recommendations(self):
        """Generate premium recommendations for product owners"""
        if self.current_subscription != 'premium':
            raise PermissionError("Premium features require subscription upgrade")
            
        print("Generating premium product owner recommendations...")
        product_recs = []
        
        # Enhanced geographic analysis
        product_city_perf = self.monthly_data.groupby(['product_id', 'city']).agg({
            'monthly_quantity': ['mean', 'std'],
            'monthly_revenue': ['mean', 'sum']
        }).reset_index()
        
        # Competitor analysis (premium feature)
        product_competition = self.monthly_data.groupby(['category', 'city']).agg({
            'product_id': pd.Series.nunique,
            'monthly_revenue': 'sum'
        }).reset_index()
        
        # Custom reports (premium feature)
        for product_id in product_city_perf['product_id'].unique():
            product_data = product_city_perf[
                product_city_perf['product_id'] == product_id
            ].sort_values(('monthly_quantity', 'mean'), ascending=False)
            
            if len(product_data) > 1:
                best_city = product_data.iloc[0]
                worst_city = product_data.iloc[-1]
                
                # Find competitors in same category
                product_category = self.monthly_data[
                    self.monthly_data['product_id'] == product_id
                ]['category'].iloc[0]
                
                competitors = product_competition[
                    product_competition['category'] == product_category
                ]
                
                product_recs.append({
                    'product_id': product_id,
                    'product_name': self.monthly_data[
                        self.monthly_data['product_id'] == product_id
                    ]['product_name'].iloc[0],
                    'type': 'premium_analysis',
                    'best_performing_city': best_city['city'].values[0],
                    'best_city_avg_sales': best_city[('monthly_quantity', 'mean')].values[0],
                    'worst_performing_city': worst_city['city'].values[0],
                    'worst_city_avg_sales': worst_city[('monthly_quantity', 'mean')].values[0],
                    'market_competition': {
                        'competitor_count': len(competitors),
                        'top_competitors': competitors.nlargest(3, 'monthly_revenue').to_dict('records')
                    },
                    'recommendations': [
                        f"Increase marketing in {best_city['city'].values[0]} where demand is highest",
                        f"Review pricing strategy in {worst_city['city'].values[0]}",
                        f"Consider promotions to compete with {len(competitors)} other products in this category"
                    ]
                })
        
        return {
            'product_recommendations': product_recs,
            'generated_at': datetime.now().isoformat(),
            'subscription_level': 'premium'
        }
    
    def _generate_shopkeeper_recommendations(self):
        """Generate shop-specific recommendations"""
        print("Generating shopkeeper recommendations...")
        shop_recs = []
        
        # Inventory optimization
        shop_performance = self.monthly_data.groupby(['shop_id', 'product_id']).agg({
            'predicted_quantity': 'mean',
            'monthly_quantity': 'mean',
            'monthly_revenue': 'mean'
        }).reset_index()
        
        for shop_id in shop_performance['shop_id'].unique():
            shop_data = shop_performance[shop_performance['shop_id'] == shop_id]
            
            # Stock recommendations
            median_sales = shop_data['monthly_quantity'].median()
            for _, row in shop_data.iterrows():
                if row['predicted_quantity'] > row['monthly_quantity'] * 1.5:
                    shop_recs.append({
                        'shop_id': shop_id,
                        'product_id': row['product_id'],
                        'product_name': self.monthly_data[
                            self.monthly_data['product_id'] == row['product_id']
                        ]['product_name'].iloc[0],
                        'type': 'increase_stock',
                        'current_avg': row['monthly_quantity'],
                        'predicted': row['predicted_quantity'],
                        'reason': 'Expected significant demand increase'
                    })
                elif row['predicted_quantity'] < row['monthly_quantity'] * 0.5:
                    shop_recs.append({
                        'shop_id': shop_id,
                        'product_id': row['product_id'],
                        'product_name': self.monthly_data[
                            self.monthly_data['product_id'] == row['product_id']
                        ]['product_name'].iloc[0],
                        'type': 'decrease_stock',
                        'current_avg': row['monthly_quantity'],
                        'predicted': row['predicted_quantity'],
                        'reason': 'Expected demand decrease'
                    })
        
        return {
            'shop_recommendations': shop_recs,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_customer_recommendations(self):
        """Generate personalized customer recommendations"""
        print("Generating customer recommendations...")
        customer_recs = []
        
        # Create customer-product matrix
        cust_prod_matrix = self.data.pivot_table(
            index='customer_id',
            columns='product_id',
            values='quantity',
            aggfunc='sum',
            fill_value=0
        )
        
        # Normalize
        cust_prod_norm = cust_prod_matrix.apply(lambda x: x/x.sum(), axis=1).fillna(0)
        
        # Find similar customers
        nn = NearestNeighbors(n_neighbors=5, metric='cosine')
        nn.fit(cust_prod_norm)
        
        for customer_id in self.customer_profiles.index:
            # Get customer preferences
            cust_prefs = eval(self.customer_profiles.loc[customer_id, 'preferred_categories'])
            
            # Find similar customers
            cust_idx = cust_prod_norm.index.get_loc(customer_id)
            _, neighbor_indices = nn.kneighbors([cust_prod_norm.iloc[cust_idx]])
            
            # Get popular products among neighbors
            neighbor_ids = cust_prod_norm.iloc[neighbor_indices[0]].index
            neighbor_purchases = self.data[self.data['customer_id'].isin(neighbor_ids)]
            
            # Recommend products customer hasn't bought
            cust_products = set(self.data[
                self.data['customer_id'] == customer_id
            ]['product_id'])
            
            recommendations = neighbor_purchases[
                ~neighbor_purchases['product_id'].isin(cust_products)
            ].groupby('product_id')['quantity'].sum().nlargest(3)
            
            for product_id in recommendations.index:
                product_info = self.data[
                    self.data['product_id'] == product_id
                ][['product_name', 'category']].iloc[0]
                
                customer_recs.append({
                    'customer_id': customer_id,
                    'product_id': product_id,
                    'product_name': product_info['product_name'],
                    'category': product_info['category'],
                    'type': 'personalized',
                    'reason': 'Popular among similar customers'
                })
        
        return {
            'customer_recommendations': customer_recs,
            'generated_at': datetime.now().isoformat()
        }
    
    def save_outputs(self, output_dir='outputs'):
        """Save all outputs to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save predictions
        self.monthly_data.to_csv(f"{output_dir}/monthly_predictions.csv", index=False)
        
        # Save recommendations based on subscription
        recommendations = {
            'shopkeepers': self._generate_shopkeeper_recommendations(),
            'customers': self._generate_customer_recommendations()
        }
        
        if self.current_subscription == 'premium':
            recommendations['product_owners'] = self._generate_product_owner_recommendations()
        else:
            recommendations['product_owners'] = self._get_basic_analytics()
        
        pd.DataFrame(recommendations['shopkeepers']['shop_recommendations']).to_csv(
            f"{output_dir}/shopkeeper_recommendations.csv", index=False
        )
        pd.DataFrame(recommendations['customers']['customer_recommendations']).to_csv(
            f"{output_dir}/customer_recommendations.csv", index=False
        )
        
        if self.current_subscription == 'premium':
            pd.DataFrame(recommendations['product_owners']['product_recommendations']).to_csv(
                f"{output_dir}/product_owner_recommendations.csv", index=False
            )
        else:
            with open(f"{output_dir}/product_owner_basic_analytics.json", 'w') as f:
                import json
                json.dump(recommendations['product_owners'], f)
        
        # Save model
        if self.model:
            joblib.dump(self.model, f"{output_dir}/sales_prediction_model.pkl")
        
        print(f"✅ All outputs saved to {output_dir} directory")


# Example usage
if __name__ == '__main__':
    # Initialize pipeline (auto-loads data)
    pipeline = RetailAnalyticsPipeline(
        transactions_path='data/transactions.csv',
        products_path='data/products.csv',
        shops_path='data/shops.csv',
        customers_path='data/customers.csv'
    )
    
    # Check subscription info
    print(pipeline.get_subscription_info())
    
    # Get free tier recommendations
    free_recs = pipeline.get_recommendations('product_owner')
    print("Free tier recommendations:", free_recs.keys())
    
    # Upgrade to premium
    pipeline.set_subscription('premium')
    
    # Train model (could be triggered by UI button)
    training_results = pipeline.train_model()
    print("Model trained with R²:", training_results['r2'])
    
    # Generate predictions
    pipeline.predict_next_month()
    
    # Get premium recommendations
    premium_recs = pipeline.get_recommendations('product_owner')
    print("Premium recommendations:", premium_recs.keys())
    
    # Save all outputs
    pipeline.save_outputs()