# Retail AI Predictor Pro – Streamlit App

## Overview

**Retail AI Predictor Pro** is an advanced, interactive dashboard for retail sales forecasting and market intelligence. Built with Streamlit, it empowers business users and analysts to:

- Upload their own retail datasets (transactions, products, shops)
- Instantly train AI/ML models for sales prediction
- Visualize key metrics, trends, and feature importances
- Simulate "what-if" business scenarios
- Explore geospatial, cluster, and seasonality analytics
- Download predictions and reports

#### Developed by: [Karan Bista](https://github.com/kar137)
## Live Demo
🔗  https://pasale.streamlit.app/

## How It Works

### 1. Data Upload & Integration

- Users upload three CSV files via the sidebar:
  - **Transactions** (sales records)
  - **Products** (catalog info)
  - **Shops** (store locations)
- The app reads these files using Pandas and merges them into a single DataFrame for analysis.

### 2. Data Processing & Feature Engineering

- The merged data is passed to backend logic in [`product_performance.py`](market-fit-analyzer/backend/product_performance.py) via:
  - `prepare_monthly_data`: Aggregates daily transactions into monthly sales per product/shop.
  - `create_features`: Generates lag features, trends, seasonality, and encodes categorical variables.

### 3. Model Training

- The processed data is used to train a machine learning model (default: Random Forest) using the `train_model` function.
- The model predicts future monthly sales and calculates metrics (MAE, RMSE, R², MAPE).

### 4. Interactive Dashboard

- The app displays:
  - **KPI Cards**: Revenue, unique products, store locations, forecast accuracy
  - **Performance Tabs**: Metrics, feature importance, prediction explorer, simulation tools
  - **Advanced Analytics**: Geospatial maps, product clusters, seasonality, word clouds
- Users can interactively select products/shops, run predictions, and simulate business scenarios.

### 5. Export & Reporting

- Users can download predictions, export dashboards (PDF), and save the trained AI model.

## Backend Logic Connection

- All core data processing and ML logic is handled in [`product_performance.py`](market-fit-analyzer/backend/product_performance.py).
- [`app.py`](market-fit-analyzer/backend/app.py) imports and calls these functions:
  - `prepare_monthly_data`
  - `create_features`
  - `train_model`
- The Streamlit app acts as the UI layer, orchestrating data flow between user uploads, backend processing, and interactive visualization.

## Getting Started

1. Install requirements:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the app:
   ```sh
   streamlit run app.py
   ```
3. Upload your CSV files in the sidebar and explore the dashboard!

---

For more details on backend logic, see [`product_performance.py`](market-fit-analyzer/backend/product_performance.py)