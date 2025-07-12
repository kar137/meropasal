#!/usr/bin/env python3
"""
Real-time ML Prediction API
Serves trained models for live predictions
"""
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

app = Flask(__name__)

class MLPredictionService:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        model_files = [
            'demand_prediction_model.pkl',
            'customer_segmentation_model.pkl', 
            'price_optimization_model.pkl',
            'churn_prediction_model.pkl'
        ]
        
        scaler_files = [
            'demand_prediction_scaler.pkl',
            'customer_segmentation_scaler.pkl',
            'price_optimization_scaler.pkl', 
            'churn_prediction_scaler.pkl'
        ]
        
        for model_file in model_files:
            if os.path.exists(model_file):
                model_name = model_file.replace('_model.pkl', '')
                self.models[model_name] = joblib.load(model_file)
                print(f"✅ Loaded {model_name} model")
        
        for scaler_file in scaler_files:
            if os.path.exists(scaler_file):
                scaler_name = scaler_file.replace('_scaler.pkl', '')
                self.scalers[scaler_name] = joblib.load(scaler_file)
                print(f"✅ Loaded {scaler_name} scaler")

# Initialize prediction service
ml_service = MLPredictionService()

@app.route('/api/predict/demand', methods=['POST'])
def predict_demand():
    """Predict demand for a product"""
    try:
        data = request.json
        
        # Expected features for demand prediction
        features = [
            data.get('customer_id', 1),
            data.get('product_id', 1),
            data.get('shop_id', 1),
            data.get('age', 30),
            data.get('avg_monthly_spending', 2000),
            data.get('visits_per_month', 5),
            data.get('standard_price', 100),
            data.get('month', datetime.now().month),
            data.get('day_of_week', datetime.now().weekday()),
            data.get('is_weekend', 1 if datetime.now().weekday() >= 5 else 0),
            data.get('gender_encoded', 0),
            data.get('city_encoded', 0),
            data.get('category_encoded', 0),
            data.get('brand_encoded', 0),
            data.get('payment_method_encoded', 0),
            data.get('hour', datetime.now().hour),
            data.get('price_vs_avg_spending_ratio', 0.05)
        ]
        
        # Make prediction
        if 'demand_prediction' in ml_service.models:
            features_scaled = ml_service.scalers['demand_prediction'].transform([features])
            prediction = ml_service.models['demand_prediction'].predict(features_scaled)[0]
            
            return jsonify({
                'success': True,
                'predicted_demand': round(prediction, 2),
                'recommendation': 'high' if prediction > 2 else 'medium' if prediction > 1 else 'low'
            })
        else:
            return jsonify({'success': False, 'error': 'Demand model not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/predict/price', methods=['POST'])
def predict_optimal_price():
    """Predict optimal price for a product"""
    try:
        data = request.json
        
        features = [
            data.get('customer_id', 1),
            data.get('product_id', 1), 
            data.get('shop_id', 1),
            data.get('age', 30),
            data.get('avg_monthly_spending', 2000),
            data.get('standard_price', 100),
            data.get('month', datetime.now().month),
            data.get('day_of_week', datetime.now().weekday()),
            data.get('is_weekend', 1 if datetime.now().weekday() >= 5 else 0),
            data.get('gender_encoded', 0),
            data.get('category_encoded', 0),
            data.get('brand_encoded', 0)
        ]
        
        if 'price_optimization' in ml_service.models:
            features_scaled = ml_service.scalers['price_optimization'].transform([features])
            prediction = ml_service.models['price_optimization'].predict(features_scaled)[0]
            
            standard_price = data.get('standard_price', 100)
            price_difference = prediction - standard_price
            price_change_percent = (price_difference / standard_price) * 100
            
            return jsonify({
                'success': True,
                'optimal_price': round(prediction, 2),
                'standard_price': standard_price,
                'price_difference': round(price_difference, 2),
                'price_change_percent': round(price_change_percent, 1),
                'recommendation': 'increase' if price_difference > 0 else 'decrease' if price_difference < -5 else 'maintain'
            })
        else:
            return jsonify({'success': False, 'error': 'Price model not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/predict/churn', methods=['POST'])
def predict_churn():
    """Predict customer churn probability"""
    try:
        data = request.json
        
        features = [
            data.get('age', 30),
            data.get('avg_monthly_spending', 2000),
            data.get('visits_per_month', 5),
            data.get('gender_encoded', 0),
            data.get('city_encoded', 0)
        ]
        
        if 'churn_prediction' in ml_service.models:
            features_scaled = ml_service.scalers['churn_prediction'].transform([features])
            prediction = ml_service.models['churn_prediction'].predict_proba(features_scaled)[0]
            churn_probability = prediction[1]  # Probability of churn
            
            risk_level = 'high' if churn_probability > 0.7 else 'medium' if churn_probability > 0.3 else 'low'
            
            return jsonify({
                'success': True,
                'churn_probability': round(churn_probability, 3),
                'risk_level': risk_level,
                'recommendation': 'immediate_attention' if risk_level == 'high' else 'monitor' if risk_level == 'medium' else 'maintain'
            })
        else:
            return jsonify({'success': False, 'error': 'Churn model not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/segment/customer', methods=['POST'])
def segment_customer():
    """Get customer segment"""
    try:
        data = request.json
        
        # Customer features for segmentation
        features = [
            data.get('total_amount_sum', 1000),
            data.get('total_amount_mean', 200),
            data.get('total_amount_count', 5),
            data.get('quantity_sum', 10),
            data.get('age', 30),
            data.get('avg_monthly_spending', 2000),
            data.get('visits_per_month', 5),
            data.get('actual_price_mean', 150),
            data.get('is_weekend_mean', 0.3)
        ]
        
        if 'customer_segmentation' in ml_service.models:
            features_scaled = ml_service.scalers['customer_segmentation'].transform([features])
            segment = ml_service.models['customer_segmentation'].predict(features_scaled)[0]
            
            # Define segment characteristics
            segment_names = {
                0: 'High Value',
                1: 'Regular Customer', 
                2: 'Price Sensitive',
                3: 'Occasional Buyer',
                4: 'Premium Customer'
            }
            
            segment_name = segment_names.get(segment, f'Segment {segment}')
            
            return jsonify({
                'success': True,
                'segment_id': int(segment),
                'segment_name': segment_name,
                'marketing_strategy': get_marketing_strategy(segment)
            })
        else:
            return jsonify({'success': False, 'error': 'Segmentation model not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_marketing_strategy(segment):
    """Get marketing strategy based on customer segment"""
    strategies = {
        0: 'Focus on premium products and exclusive offers',
        1: 'Maintain engagement with regular promotions',
        2: 'Offer discounts and value deals',
        3: 'Use targeted campaigns to increase frequency',
        4: 'Provide VIP treatment and luxury options'
    }
    return strategies.get(segment, 'Personalized marketing approach')

@app.route('/api/analytics/insights', methods=['GET'])
def get_analytics_insights():
    """Get business analytics insights"""
    try:
        # Load business insights
        import json
        if os.path.exists('business_insights.json'):
            with open('business_insights.json', 'r') as f:
                insights = json.load(f)
            return jsonify({'success': True, 'insights': insights})
        else:
            return jsonify({'success': False, 'error': 'Insights not available'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/models/status', methods=['GET'])
def get_models_status():
    """Get status of all ML models"""
    try:
        status = {
            'models_loaded': len(ml_service.models),
            'scalers_loaded': len(ml_service.scalers),
            'available_models': list(ml_service.models.keys()),
            'available_endpoints': [
                '/api/predict/demand',
                '/api/predict/price', 
                '/api/predict/churn',
                '/api/segment/customer',
                '/api/analytics/insights'
            ]
        }
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ML Prediction API',
        'timestamp': datetime.now().isoformat(),
        'models_available': len(ml_service.models) > 0
    })

@app.route('/', methods=['GET'])
def home():
    """API documentation"""
    docs = {
        'service': 'ML Prediction API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/models/status': 'Get models status',
            'GET /api/analytics/insights': 'Get business insights',
            'POST /api/predict/demand': 'Predict product demand',
            'POST /api/predict/price': 'Predict optimal price',
            'POST /api/predict/churn': 'Predict customer churn',
            'POST /api/segment/customer': 'Get customer segment'
        },
        'example_usage': {
            'demand_prediction': {
                'url': '/api/predict/demand',
                'method': 'POST',
                'body': {
                    'customer_id': 1,
                    'product_id': 1,
                    'shop_id': 1,
                    'age': 30,
                    'standard_price': 100
                }
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    print("🚀 Starting ML Prediction API...")
    print("📊 Available endpoints:")
    print("   • GET  /api/health - Health check") 
    print("   • GET  /api/models/status - Models status")
    print("   • POST /api/predict/demand - Demand prediction")
    print("   • POST /api/predict/price - Price optimization")
    print("   • POST /api/predict/churn - Churn prediction") 
    print("   • POST /api/segment/customer - Customer segmentation")
    print("   • GET  /api/analytics/insights - Business insights")
    print("\n🌐 API will be available at: http://localhost:5001")
    
    app.run(host='127.0.0.1', port=5001, debug=False)
