@echo off
echo ===================================================
echo   MeroPasal ML Analytics System - Complete Setup
echo ===================================================
echo.

REM Set the script directory
cd /d "%~dp0ml_backend"

echo 1. Installing required Python packages...
pip install scikit-learn matplotlib seaborn plotly flask pandas numpy joblib schedule

echo.
echo 2. Running ML Analytics Engine...
python ml_analytics_engine.py

echo.
echo 3. Starting services...
echo.

echo Starting ML Prediction API (Port 5001)...
start "ML Prediction API" cmd /k "python ml_prediction_api.py"

echo.
echo Starting Analytics Dashboard (Port 5002)...
start "Analytics Dashboard" cmd /k "python analytics_dashboard.py"

echo.
echo Starting Data Sync API (Port 5000)...
start "Data Sync API" cmd /k "python start_api.py"

echo.
echo ===================================================
echo   🚀 All Services Started Successfully!
echo ===================================================
echo.
echo Available Services:
echo   • Data Sync API:      http://localhost:5000
echo   • ML Prediction API:  http://localhost:5001
echo   • Analytics Dashboard: http://localhost:5002
echo.
echo API Endpoints:
echo   • Demand Prediction:  POST http://localhost:5001/api/predict/demand
echo   • Price Optimization: POST http://localhost:5001/api/predict/price
echo   • Churn Prediction:   POST http://localhost:5001/api/predict/churn
echo   • Customer Segments:  POST http://localhost:5001/api/segment/customer
echo   • Business Insights:  GET  http://localhost:5001/api/analytics/insights
echo.
echo Generated Files:
echo   • demand_model_features.csv - Feature importance
echo   • customer_segments.csv - Customer segmentation
echo   • business_insights.json - Key metrics
echo   • retail_analytics_dashboard.png - Visualizations
echo   • *_model.pkl - Trained ML models
echo   • *_scaler.pkl - Feature scalers
echo.
echo 🎯 Open http://localhost:5002 to view the dashboard!
echo.
pause
