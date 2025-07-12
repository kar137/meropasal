#!/usr/bin/env python3
"""
Advanced ML Analytics Engine for Retail Data
Implements multiple ML models using the extracted features
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, classification_report, silhouette_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class MLAnalyticsEngine:
    def __init__(self, features_path='extracted_features.csv'):
        """Initialize the ML Analytics Engine"""
        self.features_path = features_path
        self.data = None
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
    def load_data(self):
        """Load and prepare the extracted features data"""
        try:
            self.data = pd.read_csv(self.features_path)
            print(f"✅ Loaded {len(self.data)} records with {len(self.data.columns)} features")
            
            # Convert date columns
            self.data['transaction_date'] = pd.to_datetime(self.data['transaction_date'])
            
            # Handle missing values
            self.data = self.data.fillna(method='ffill').fillna(0)
            
            print("📊 Data Overview:")
            print(f"   • Transactions: {len(self.data)}")
            print(f"   • Customers: {self.data['customer_id'].nunique()}")
            print(f"   • Products: {self.data['product_id'].nunique()}")
            print(f"   • Date range: {self.data['transaction_date'].min()} to {self.data['transaction_date'].max()}")
            
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def prepare_features(self):
        """Prepare features for ML models"""
        if self.data is None:
            self.load_data()
        
        # Encode categorical variables
        categorical_columns = ['gender', 'city', 'category', 'brand', 'payment_method', 'district']
        
        for col in categorical_columns:
            if col in self.data.columns:
                le = LabelEncoder()
                self.data[f'{col}_encoded'] = le.fit_transform(self.data[col].astype(str))
                self.encoders[col] = le
        
        # Create additional features
        self.data['hour'] = self.data['transaction_date'].dt.hour
        self.data['price_vs_avg_spending_ratio'] = self.data['actual_price'] / self.data['avg_monthly_spending']
        self.data['quantity_per_visit'] = self.data['quantity'] / self.data['visits_per_month']
        
        print("✅ Features prepared for ML modeling")
    
    def build_demand_prediction_model(self):
        """Build demand prediction model"""
        print("\n🎯 Building Demand Prediction Model...")
        
        # Features for demand prediction
        feature_cols = [
            'customer_id', 'product_id', 'shop_id', 'age', 'avg_monthly_spending',
            'visits_per_month', 'standard_price', 'month', 'day_of_week', 'is_weekend',
            'gender_encoded', 'city_encoded', 'category_encoded', 'brand_encoded',
            'payment_method_encoded', 'hour', 'price_vs_avg_spending_ratio'
        ]
        
        # Filter available columns
        available_cols = [col for col in feature_cols if col in self.data.columns]
        X = self.data[available_cols]
        y = self.data['quantity']  # Predict quantity demanded
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = rf_model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Store model and scaler
        self.models['demand_prediction'] = rf_model
        self.scalers['demand_prediction'] = scaler
        
        print(f"   ✅ Model trained with MAE: {mae:.3f}")
        print(f"   📊 Feature importance saved")
        
        # Save feature importance
        importance_df = pd.DataFrame({
            'feature': available_cols,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        importance_df.to_csv('demand_model_features.csv', index=False)
        return rf_model, mae
    
    def build_customer_segmentation_model(self):
        """Build customer segmentation using clustering"""
        print("\n👥 Building Customer Segmentation Model...")
        
        # Aggregate customer features
        customer_features = self.data.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'quantity': 'sum',
            'age': 'first',
            'avg_monthly_spending': 'first',
            'visits_per_month': 'first',
            'actual_price': 'mean',
            'is_weekend': 'mean'
        }).round(2)
        
        # Flatten column names
        customer_features.columns = ['_'.join(col).strip() for col in customer_features.columns]
        customer_features = customer_features.reset_index()
        
        # Select features for clustering
        cluster_features = [
            'total_amount_sum', 'total_amount_mean', 'total_amount_count',
            'quantity_sum', 'age_first', 'avg_monthly_spending_first',
            'visits_per_month_first', 'actual_price_mean', 'is_weekend_mean'
        ]
        
        X_cluster = customer_features[cluster_features]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_cluster)
        
        # Find optimal number of clusters (handle small datasets)
        n_customers = len(X_cluster)
        max_clusters = min(n_customers - 1, 7)  # Ensure we don't exceed valid range
        
        if max_clusters < 2:
            print(f"   ⚠️  Only {n_customers} customers - skipping segmentation")
            return None, None
        
        silhouette_scores = []
        K_range = range(2, max_clusters + 1)
        
        for k in K_range:
            if k < n_customers:  # Ensure k is less than number of samples
                kmeans = KMeans(n_clusters=k, random_state=42)
                labels = kmeans.fit_predict(X_scaled)
                score = silhouette_score(X_scaled, labels)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(0)
        
        # Use best number of clusters
        optimal_k = K_range[np.argmax(silhouette_scores)]
        
        # Train final clustering model
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        customer_features['segment'] = kmeans.fit_predict(X_scaled)
        
        # Store model and scaler
        self.models['customer_segmentation'] = kmeans
        self.scalers['customer_segmentation'] = scaler
        
        print(f"   ✅ Created {optimal_k} customer segments")
        print(f"   📊 Silhouette score: {max(silhouette_scores):.3f}")
        
        # Save customer segments
        customer_features.to_csv('customer_segments.csv', index=False)
        
        return kmeans, customer_features
    
    def build_price_optimization_model(self):
        """Build price optimization model"""
        print("\n💰 Building Price Optimization Model...")
        
        # Features for price optimization
        feature_cols = [
            'customer_id', 'product_id', 'shop_id', 'age', 'avg_monthly_spending',
            'standard_price', 'month', 'day_of_week', 'is_weekend',
            'gender_encoded', 'category_encoded', 'brand_encoded'
        ]
        
        available_cols = [col for col in feature_cols if col in self.data.columns]
        X = self.data[available_cols]
        y = self.data['actual_price']  # Predict optimal price
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Store model
        self.models['price_optimization'] = model
        self.scalers['price_optimization'] = scaler
        
        print(f"   ✅ Model trained with MAE: {mae:.2f}")
        
        return model, mae
    
    def build_churn_prediction_model(self):
        """Build customer churn prediction model"""
        print("\n🚨 Building Churn Prediction Model...")
        
        # Create churn labels (simplified - customers with low recent activity)
        customer_activity = self.data.groupby('customer_id').agg({
            'transaction_date': 'max',
            'total_amount': 'sum',
            'visits_per_month': 'first'
        })
        
        # Define churn as no activity in last 30 days
        recent_date = self.data['transaction_date'].max()
        days_since_last = (recent_date - customer_activity['transaction_date']).dt.days
        
        # Create churn labels
        customer_activity['churn'] = (days_since_last > 30).astype(int)
        
        # Prepare features
        feature_cols = [
            'age', 'avg_monthly_spending', 'visits_per_month',
            'gender_encoded', 'city_encoded'
        ]
        
        # Merge with customer data
        customer_data = self.data.groupby('customer_id')[feature_cols].first()
        model_data = customer_data.merge(customer_activity[['churn']], left_index=True, right_index=True)
        
        available_cols = [col for col in feature_cols if col in model_data.columns]
        X = model_data[available_cols]
        y = model_data['churn']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        
        # Store model
        self.models['churn_prediction'] = model
        self.scalers['churn_prediction'] = scaler
        
        print(f"   ✅ Churn model trained")
        print(f"   📊 Accuracy: {model.score(X_test_scaled, y_test):.3f}")
        
        return model
    
    def generate_insights(self):
        """Generate business insights from the data"""
        print("\n📈 Generating Business Insights...")
        
        insights = {}
        
        # Sales insights
        insights['total_revenue'] = self.data['total_amount'].sum()
        insights['avg_transaction_value'] = self.data['total_amount'].mean()
        insights['total_transactions'] = len(self.data)
        insights['unique_customers'] = self.data['customer_id'].nunique()
        
        # Customer insights
        insights['avg_customer_age'] = self.data['age'].mean()
        insights['top_customer_city'] = self.data['city'].mode().iloc[0]
        insights['weekend_vs_weekday_ratio'] = self.data['is_weekend'].mean()
        
        # Product insights
        top_products = self.data.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(5)
        insights['top_products'] = top_products.to_dict()
        
        # Payment method insights
        payment_distribution = self.data['payment_method'].value_counts(normalize=True)
        insights['payment_preferences'] = payment_distribution.to_dict()
        
        # Price insights
        insights['avg_price_markup'] = self.data['price_ratio'].mean()
        insights['price_variance'] = self.data['price_difference'].std()
        
        print("✅ Business insights generated")
        
        # Save insights
        import json
        with open('business_insights.json', 'w') as f:
            json.dump(insights, f, indent=2, default=str)
        
        return insights
    
    def create_visualizations(self):
        """Create data visualizations"""
        print("\n📊 Creating Visualizations...")
        
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Retail Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Sales by day of week
        daily_sales = self.data.groupby('day_of_week')['total_amount'].sum()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Create arrays for actual data
        days_present = daily_sales.index.tolist()
        sales_values = daily_sales.values.tolist()
        day_labels = [day_names[int(day)] for day in days_present]
        
        axes[0,0].bar(day_labels, sales_values)
        axes[0,0].set_title('Sales by Day of Week')
        axes[0,0].set_ylabel('Total Sales')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # 2. Customer age distribution
        axes[0,1].hist(self.data['age'], bins=20, alpha=0.7, color='skyblue')
        axes[0,1].set_title('Customer Age Distribution')
        axes[0,1].set_xlabel('Age')
        axes[0,1].set_ylabel('Frequency')
        
        # 3. Price vs Standard Price
        axes[0,2].scatter(self.data['standard_price'], self.data['actual_price'], alpha=0.6)
        axes[0,2].plot([self.data['standard_price'].min(), self.data['standard_price'].max()], 
                      [self.data['standard_price'].min(), self.data['standard_price'].max()], 
                      'r--', label='Standard Price Line')
        axes[0,2].set_title('Actual vs Standard Price')
        axes[0,2].set_xlabel('Standard Price')
        axes[0,2].set_ylabel('Actual Price')
        axes[0,2].legend()
        
        # 4. Payment method distribution
        payment_counts = self.data['payment_method'].value_counts()
        axes[1,0].pie(payment_counts.values, labels=payment_counts.index, autopct='%1.1f%%')
        axes[1,0].set_title('Payment Method Distribution')
        
        # 5. Category sales
        category_sales = self.data.groupby('category')['total_amount'].sum().sort_values(ascending=True)
        axes[1,1].barh(category_sales.index, category_sales.values)
        axes[1,1].set_title('Sales by Category')
        axes[1,1].set_xlabel('Total Sales')
        
        # 6. Monthly trend
        monthly_sales = self.data.groupby('month')['total_amount'].sum()
        axes[1,2].plot(monthly_sales.index, monthly_sales.values, marker='o', linewidth=2)
        axes[1,2].set_title('Monthly Sales Trend')
        axes[1,2].set_xlabel('Month')
        axes[1,2].set_ylabel('Total Sales')
        axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('retail_analytics_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Dashboard saved as 'retail_analytics_dashboard.png'")
    
    def save_models(self):
        """Save all trained models"""
        print("\n💾 Saving Models...")
        
        for model_name, model in self.models.items():
            joblib.dump(model, f'{model_name}_model.pkl')
            print(f"   ✅ Saved {model_name}_model.pkl")
        
        for scaler_name, scaler in self.scalers.items():
            joblib.dump(scaler, f'{scaler_name}_scaler.pkl')
            print(f"   ✅ Saved {scaler_name}_scaler.pkl")
    
    def run_full_analysis(self):
        """Run complete ML analysis pipeline"""
        print("🚀 Starting Complete ML Analytics Pipeline...\n")
        
        # Load and prepare data
        if not self.load_data():
            return False
        
        self.prepare_features()
        
        # Build all models
        self.build_demand_prediction_model()
        self.build_customer_segmentation_model()
        self.build_price_optimization_model()
        self.build_churn_prediction_model()
        
        # Generate insights and visualizations
        insights = self.generate_insights()
        self.create_visualizations()
        
        # Save everything
        self.save_models()
        
        print("\n🎉 Complete ML Analytics Pipeline Finished!")
        print("\n📋 Generated Files:")
        print("   • demand_model_features.csv - Feature importance")
        print("   • customer_segments.csv - Customer segmentation")
        print("   • business_insights.json - Key metrics")
        print("   • retail_analytics_dashboard.png - Visualizations")
        print("   • *_model.pkl - Trained ML models")
        print("   • *_scaler.pkl - Feature scalers")
        
        return True

def main():
    """Main function to run the analytics"""
    engine = MLAnalyticsEngine()
    success = engine.run_full_analysis()
    
    if success:
        print("\n✅ ML Analytics completed successfully!")
    else:
        print("\n❌ ML Analytics failed!")

if __name__ == "__main__":
    main()
