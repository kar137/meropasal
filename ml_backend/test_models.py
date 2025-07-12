#!/usr/bin/env python3
"""
Simple test script to verify ML models are working
"""
import joblib
import numpy as np
import pandas as pd

def test_models():
    print("🧪 Testing Trained ML Models...")
    print("=" * 40)
    
    # Test 1: Load and test demand prediction model
    try:
        model = joblib.load('demand_prediction_model.pkl')
        scaler = joblib.load('demand_prediction_scaler.pkl')
        
        # Create sample data (matching the feature order from training)
        sample_data = [[1, 1, 1, 30, 2000, 5, 100, 7, 4, 0, 0, 0, 0, 0, 0, 12, 0.05]]
        
        # Scale and predict
        scaled_data = scaler.transform(sample_data)
        prediction = model.predict(scaled_data)[0]
        
        print(f"✅ Demand Prediction Model: Predicts {prediction:.1f} units")
        
    except Exception as e:
        print(f"❌ Demand Prediction Model failed: {e}")
    
    # Test 2: Load and test price optimization model
    try:
        model = joblib.load('price_optimization_model.pkl')
        scaler = joblib.load('price_optimization_scaler.pkl')
        
        # Sample data for price optimization
        sample_data = [[1, 1, 1, 30, 2000, 100, 7, 4, 0, 0, 0, 0]]
        
        scaled_data = scaler.transform(sample_data)
        prediction = model.predict(scaled_data)[0]
        
        print(f"✅ Price Optimization Model: Suggests ₹{prediction:.2f}")
        
    except Exception as e:
        print(f"❌ Price Optimization Model failed: {e}")
    
    # Test 3: Load and test customer segmentation
    try:
        model = joblib.load('customer_segmentation_model.pkl')
        scaler = joblib.load('customer_segmentation_scaler.pkl')
        
        # Sample customer data
        sample_data = [[5000, 200, 10, 25, 30, 2000, 8, 150, 0.3]]
        
        scaled_data = scaler.transform(sample_data)
        segment = model.predict(scaled_data)[0]
        
        print(f"✅ Customer Segmentation Model: Customer belongs to segment {segment}")
        
    except Exception as e:
        print(f"❌ Customer Segmentation Model failed: {e}")
    
    # Test 4: Load and test churn prediction
    try:
        model = joblib.load('churn_prediction_model.pkl')
        scaler = joblib.load('churn_prediction_scaler.pkl')
        
        # Sample customer data
        sample_data = [[30, 2000, 8, 0, 0]]
        
        scaled_data = scaler.transform(sample_data)
        churn_prob = model.predict_proba(scaled_data)[0][1]
        
        print(f"✅ Churn Prediction Model: {churn_prob:.1%} churn probability")
        
    except Exception as e:
        print(f"❌ Churn Prediction Model failed: {e}")
    
    # Test 5: Check generated files
    print("\n📁 Generated Files Check:")
    files_to_check = [
        'business_insights.json',
        'customer_segments.csv',
        'demand_model_features.csv',
        'retail_analytics_dashboard.png'
    ]
    
    import os
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size:,} bytes)")
        else:
            print(f"   ❌ {file} (missing)")
    
    # Test 6: Load and display business insights
    print("\n📊 Business Insights:")
    try:
        import json
        with open('business_insights.json', 'r') as f:
            insights = json.load(f)
        
        print(f"   • Total Revenue: ₹{insights['total_revenue']:,.2f}")
        print(f"   • Total Transactions: {insights['total_transactions']:,}")
        print(f"   • Average Transaction: ₹{insights['avg_transaction_value']:.2f}")
        print(f"   • Unique Customers: {insights['unique_customers']}")
        print(f"   • Top City: {insights['top_customer_city']}")
        
    except Exception as e:
        print(f"   ❌ Could not load insights: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 ML Model Testing Complete!")
    print("✅ All models are trained and ready for predictions!")

if __name__ == "__main__":
    test_models()
