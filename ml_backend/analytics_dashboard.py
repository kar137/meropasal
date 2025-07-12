#!/usr/bin/env python3
"""
Real-time Analytics Dashboard
Web-based dashboard for viewing ML analytics results
"""
from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

class AnalyticsDashboard:
    def __init__(self):
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load extracted features data"""
        try:
            self.data = pd.read_csv('extracted_features.csv')
            self.data['transaction_date'] = pd.to_datetime(self.data['transaction_date'])
            print(f"✅ Dashboard loaded {len(self.data)} records")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def get_kpi_metrics(self):
        """Calculate KPI metrics"""
        if self.data is None:
            return {}
        
        total_revenue = self.data['total_amount'].sum()
        total_transactions = len(self.data)
        avg_transaction_value = self.data['total_amount'].mean()
        unique_customers = self.data['customer_id'].nunique()
        
        # Calculate growth (comparing recent vs older data)
        recent_date = self.data['transaction_date'].max()
        cutoff_date = recent_date - timedelta(days=7)
        
        recent_data = self.data[self.data['transaction_date'] >= cutoff_date]
        older_data = self.data[self.data['transaction_date'] < cutoff_date]
        
        revenue_growth = 0
        if len(older_data) > 0:
            recent_revenue = recent_data['total_amount'].sum()
            older_revenue = older_data['total_amount'].sum()
            revenue_growth = ((recent_revenue - older_revenue) / older_revenue) * 100 if older_revenue > 0 else 0
        
        return {
            'total_revenue': f"₹{total_revenue:,.2f}",
            'total_transactions': f"{total_transactions:,}",
            'avg_transaction_value': f"₹{avg_transaction_value:.2f}",
            'unique_customers': f"{unique_customers:,}",
            'revenue_growth': f"{revenue_growth:+.1f}%"
        }
    
    def create_sales_trend_chart(self):
        """Create sales trend chart"""
        daily_sales = self.data.groupby(self.data['transaction_date'].dt.date)['total_amount'].sum().reset_index()
        
        fig = px.line(daily_sales, x='transaction_date', y='total_amount',
                     title='Daily Sales Trend',
                     labels={'total_amount': 'Sales (₹)', 'transaction_date': 'Date'})
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Sales (₹)",
            hovermode='x unified'
        )
        return fig.to_json()
    
    def create_category_distribution_chart(self):
        """Create category distribution chart"""
        category_sales = self.data.groupby('category')['total_amount'].sum().sort_values(ascending=True)
        
        fig = px.bar(x=category_sales.values, y=category_sales.index,
                    orientation='h',
                    title='Sales by Category',
                    labels={'x': 'Sales (₹)', 'y': 'Category'})
        return fig.to_json()
    
    def create_customer_analysis_chart(self):
        """Create customer analysis chart"""
        customer_stats = self.data.groupby('customer_id').agg({
            'total_amount': 'sum',
            'transaction_id': 'count'
        }).rename(columns={'transaction_id': 'transaction_count'})
        
        fig = px.scatter(customer_stats, x='transaction_count', y='total_amount',
                        title='Customer Value vs Frequency',
                        labels={'transaction_count': 'Number of Transactions', 'total_amount': 'Total Spent (₹)'},
                        hover_data={'total_amount': ':,.2f'})
        return fig.to_json()
    
    def create_payment_method_chart(self):
        """Create payment method distribution chart"""
        payment_dist = self.data['payment_method'].value_counts()
        
        fig = px.pie(values=payment_dist.values, names=payment_dist.index,
                    title='Payment Method Distribution')
        return fig.to_json()
    
    def create_hourly_sales_chart(self):
        """Create hourly sales pattern chart"""
        self.data['hour'] = self.data['transaction_date'].dt.hour
        hourly_sales = self.data.groupby('hour')['total_amount'].sum()
        
        fig = px.bar(x=hourly_sales.index, y=hourly_sales.values,
                    title='Sales by Hour of Day',
                    labels={'x': 'Hour', 'y': 'Sales (₹)'})
        return fig.to_json()
    
    def get_top_products(self, limit=10):
        """Get top selling products"""
        top_products = self.data.groupby('product_name').agg({
            'quantity': 'sum',
            'total_amount': 'sum'
        }).sort_values('total_amount', ascending=False).head(limit)
        
        return top_products.to_dict('index')
    
    def get_top_customers(self, limit=10):
        """Get top customers"""
        top_customers = self.data.groupby(['customer_id', 'customer_name']).agg({
            'total_amount': 'sum',
            'transaction_id': 'count'
        }).sort_values('total_amount', ascending=False).head(limit)
        
        return top_customers.to_dict('index')

# Initialize dashboard
dashboard = AnalyticsDashboard()

@app.route('/')
def home():
    """Dashboard home page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/kpis')
def get_kpis():
    """Get KPI metrics"""
    try:
        kpis = dashboard.get_kpi_metrics()
        return jsonify({'success': True, 'data': kpis})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/charts/sales-trend')
def get_sales_trend():
    """Get sales trend chart"""
    try:
        chart = dashboard.create_sales_trend_chart()
        return jsonify({'success': True, 'chart': chart})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/charts/category-distribution')
def get_category_distribution():
    """Get category distribution chart"""
    try:
        chart = dashboard.create_category_distribution_chart()
        return jsonify({'success': True, 'chart': chart})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/charts/customer-analysis')
def get_customer_analysis():
    """Get customer analysis chart"""
    try:
        chart = dashboard.create_customer_analysis_chart()
        return jsonify({'success': True, 'chart': chart})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/charts/payment-methods')
def get_payment_methods():
    """Get payment methods chart"""
    try:
        chart = dashboard.create_payment_method_chart()
        return jsonify({'success': True, 'chart': chart})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/charts/hourly-sales')
def get_hourly_sales():
    """Get hourly sales chart"""
    try:
        chart = dashboard.create_hourly_sales_chart()
        return jsonify({'success': True, 'chart': chart})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/top-products')
def get_top_products():
    """Get top products"""
    try:
        limit = request.args.get('limit', 10, type=int)
        products = dashboard.get_top_products(limit)
        return jsonify({'success': True, 'data': products})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/top-customers')
def get_top_customers():
    """Get top customers"""
    try:
        limit = request.args.get('limit', 10, type=int)
        customers = dashboard.get_top_customers(limit)
        return jsonify({'success': True, 'data': customers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/refresh')
def refresh_data():
    """Refresh dashboard data"""
    try:
        dashboard.load_data()
        return jsonify({'success': True, 'message': 'Data refreshed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Analytics Dashboard...")
    print("📊 Dashboard available at: http://localhost:5002")
    print("🔄 API endpoints:")
    print("   • GET /api/dashboard/kpis - KPI metrics")
    print("   • GET /api/dashboard/charts/* - Various charts")
    print("   • GET /api/dashboard/top-products - Top products")
    print("   • GET /api/dashboard/top-customers - Top customers")
    
    app.run(host='127.0.0.1', port=5002, debug=False)
