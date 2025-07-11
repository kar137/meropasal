import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import tempfile
from wordcloud import WordCloud
from sklearn.cluster import KMeans  # Add this import
import matplotlib.pyplot as plt
from retail_analytics_pipeline import RetailAnalyticsPipeline

# Configure page
st.set_page_config(
    page_title="🚀 Retail AI Predictor Pro", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.card {
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    padding: 1.5rem;
    background: white;
    margin-bottom: 1.5rem;
}
.premium-badge {
    background-color: gold;
    color: black;
    padding: 0.2rem 0.5rem;
    border-radius: 10px;
    font-weight: bold;
    display: inline-block;
    margin-left: 10px;
}
.header {
    background-color: #4CAF50;
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='header'>
    <h1 style='color: white; text-align: center;'>Retail AI Predictor Pro</h1>
    <p style='text-align: center;'>Next-Gen Sales Forecasting & Market Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
    st.session_state.data_loaded = False
    st.session_state.model_trained = False
    st.session_state.subscription = "Free"

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ Control Panel")
    
    # Subscription
    st.session_state.subscription = st.radio(
        "Choose Plan", 
        ["Free", "Premium"], 
        index=0,
        key="subscription_plan"
    )
    if st.session_state.subscription == "Premium":
        st.markdown("<span class='premium-badge'>PREMIUM</span>", unsafe_allow_html=True)
    
    # File upload
    st.markdown("### 📂 Upload Data Files")
    transactions_file = st.file_uploader("Transactions CSV", type="csv", key="transactions")
    products_file = st.file_uploader("Products CSV", type="csv", key="products")
    shops_file = st.file_uploader("Shops CSV", type="csv", key="shops")
    customers_file = st.file_uploader("Customers CSV", type="csv", key="customers")
    
    if st.button("🚀 Load Data", use_container_width=True):
        if all([transactions_file, products_file, shops_file, customers_file]):
            with st.spinner("Loading data..."):
                try:
                    # Save files temporarily
                    temp_dir = tempfile.mkdtemp()
                    
                    def save_uploaded_file(uploaded_file, path):
                        with open(path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    paths = {
                        'transactions': os.path.join(temp_dir, "transactions.csv"),
                        'products': os.path.join(temp_dir, "products.csv"), 
                        'shops': os.path.join(temp_dir, "shops.csv"),
                        'customers': os.path.join(temp_dir, "customers.csv")
                    }
                    
                    save_uploaded_file(transactions_file, paths['transactions'])
                    save_uploaded_file(products_file, paths['products'])
                    save_uploaded_file(shops_file, paths['shops'])
                    save_uploaded_file(customers_file, paths['customers'])
                    
                    # Initialize pipeline
                    st.session_state.pipeline = RetailAnalyticsPipeline(
                        paths['transactions'],
                        paths['products'],
                        paths['shops'],
                        paths['customers']
                    )
                    
                    # Set subscription
                    st.session_state.pipeline.set_subscription(st.session_state.subscription.lower())
                    
                    # Load data
                    success = st.session_state.pipeline.load_and_prepare_data()
                    if success:
                        st.session_state.data_loaded = True
                        st.success("Data loaded successfully!")
                    else:
                        st.error("Failed to load data")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload all files")
    
    # Model training
    if st.session_state.data_loaded:
        if not st.session_state.model_trained:
            if st.button("🤖 Train Model", use_container_width=True):
                with st.spinner("Training model..."):
                    try:
                        # Check if data is ready for training
                        ready, message = st.session_state.pipeline.is_ready_for_training()
                        if ready:
                            result = st.session_state.pipeline.train_model()
                            st.session_state.model_trained = True
                            st.success("Model trained successfully!")
                            st.info(f"Training completed with {result['training_samples']} samples")
                        else:
                            st.error(f"Cannot train model: {message}")
                            st.session_state.model_trained = False
                    except Exception as e:
                        st.error(f"Training failed: {str(e)}")
                        st.session_state.model_trained = False
        else:
            # Model is trained - show retrain option
            st.success("✅ Model is trained")
            if st.button("🔄 Retrain Model", use_container_width=True):
                with st.spinner("Retraining model..."):
                    try:
                        result = st.session_state.pipeline.train_model()
                        st.session_state.model_trained = True
                        st.success("Model retrained successfully!")
                    except Exception as e:
                        st.error(f"Retraining failed: {str(e)}")
                        st.session_state.model_trained = False
    
    if st.button("💾 Export Results", use_container_width=True):
        with st.spinner("Exporting data..."):
            try:
                export_dir = os.path.join(tempfile.gettempdir(), "retail_export")
                os.makedirs(export_dir, exist_ok=True)
                st.session_state.pipeline.save_outputs(export_dir)
                
                # Create zip file
                import zipfile
                zip_path = os.path.join(tempfile.gettempdir(), "retail_export.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(export_dir):
                        for file in files:
                            zipf.write(
                                os.path.join(root, file), 
                                os.path.relpath(os.path.join(root, file), 
                                os.path.join(export_dir, '..')
                            ))
                
                # Provide download link
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Export",
                        data=f,
                        file_name="retail_export.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
                        
                    

# Main app
if st.session_state.pipeline and st.session_state.data_loaded:
    # Dashboard
    st.markdown("## 📊 Executive Dashboard")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_revenue = st.session_state.pipeline.data['total_amount'].sum()
        st.markdown(f"""
        <div class='card'>
            <h3>💰 Total Revenue</h3>
            <h2>${total_revenue:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_products = st.session_state.pipeline.products['product_id'].nunique()
        st.markdown(f"""
        <div class='card'>
            <h3>🛍️ Unique Products</h3>
            <h2>{unique_products:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        store_count = st.session_state.pipeline.shops['shop_id'].nunique()
        st.markdown(f"""
        <div class='card'>
            <h3>🏬 Store Locations</h3>
            <h2>{store_count:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.model_trained and hasattr(st.session_state.pipeline, 'model') and st.session_state.pipeline.model is not None:
            try:
                metrics = st.session_state.pipeline.get_model_metrics()
                if 'error' not in metrics:
                    accuracy = 100 - metrics['mape']
                    st.markdown(f"""
                    <div class='card'>
                        <h3>📈 Forecast Accuracy</h3>
                        <h2>{accuracy:.1f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class='card'>
                        <h3>📈 Forecast Accuracy</h3>
                        <h2>Error</h2>
                        <p style='font-size: 0.8em; color: red;'>Model issue</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown("""
                <div class='card'>
                    <h3>📈 Forecast Accuracy</h3>
                    <h2>--</h2>
                    <p style='font-size: 0.8em; color: orange;'>Calculating...</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card'>
                <h3>📈 Forecast Accuracy</h3>
                <h2>--</h2>
                <p style='font-size: 0.8em; color: gray;'>Train model first</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Model Performance
    if st.session_state.model_trained:
        st.markdown("## 🤖 AI Model Performance")
        
        # Check if model actually exists and is trained
        if (hasattr(st.session_state.pipeline, 'model') and 
            st.session_state.pipeline.model is not None and
            st.session_state.pipeline.is_trained):
            
            col1, col2, col3 = st.columns(3)
            try:
                metrics = st.session_state.pipeline.get_model_metrics()
                col1.metric("Mean Absolute Error", f"{metrics['mae']:.2f}")
                col2.metric("Root Mean Squared Error", f"{metrics['rmse']:.2f}")
                col3.metric("R² Score", f"{metrics['r2']:.2f}")
            except Exception as e:
                st.error(f"Error getting model metrics: {str(e)}")
            
            # Actual vs Predicted plot - with error handling
            try:
                if (st.session_state.pipeline.monthly_data is not None and 
                    len(st.session_state.pipeline.monthly_data) > 0 and
                    all(col in st.session_state.pipeline.monthly_data.columns 
                        for col in st.session_state.pipeline.feature_columns)):
                    
                    y_true = st.session_state.pipeline.monthly_data['monthly_quantity']
                    X_features = st.session_state.pipeline.monthly_data[st.session_state.pipeline.feature_columns]
                    
                    # Remove any NaN or infinite values
                    mask = np.isfinite(X_features).all(axis=1) & np.isfinite(y_true)
                    y_true_clean = y_true[mask]
                    X_features_clean = X_features[mask]
                    
                    if len(y_true_clean) > 0:
                        y_pred = st.session_state.pipeline.model.predict(X_features_clean)
                        
                        fig = px.scatter(
                            x=y_true_clean, 
                            y=y_pred, 
                            labels={'x': 'Actual Sales', 'y': 'Predicted Sales'},
                            title="Actual vs Predicted Sales"
                        )
                        
                        # Add perfect prediction line
                        min_val = min(y_true_clean.min(), y_pred.min())
                        max_val = max(y_true_clean.max(), y_pred.max())
                        
                        fig.add_shape(
                            type="line", 
                            x0=min_val, 
                            y0=min_val, 
                            x1=max_val, 
                            y1=max_val,
                            line=dict(color="red", dash="dash")
                        )
                        fig.update_layout(
                            width=800,
                            height=500,
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No valid data points for plotting after cleaning")
                else:
                    st.warning("Insufficient data for model performance visualization")
                    
            except Exception as e:
                st.error(f"Error creating performance plot: {str(e)}")
                st.info("Model performance plot temporarily unavailable")
        else:
            st.warning("Model not properly trained. Please retrain the model.")
            
            # Show training button
            if st.button("🔄 Retrain Model", key="retrain_model"):
                with st.spinner("Retraining model..."):
                    try:
                        st.session_state.pipeline.train_model()
                        st.session_state.model_trained = True
                        st.success("Model retrained successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Retraining failed: {str(e)}")
                        st.session_state.model_trained = False
    else:
        st.info("Train the model first to see performance metrics")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Sales Predictions", 
        "🛍 Product Insights", 
        "🏪 Store Analytics", 
        "👥 Customer Intelligence"
    ])

    with tab1:  # Sales Predictions
        st.markdown("## 📈 Sales Predictions")
        
        if st.session_state.model_trained:
            col1, col2 = st.columns(2)
            
            with col1:
                # Product selector
                products = st.session_state.pipeline.products[['product_id', 'product_name']].drop_duplicates()
                selected_product = st.selectbox(
                    "Select Product", 
                    products['product_name'],
                    key="product_select"
                )
                product_id = products[products['product_name']==selected_product]['product_id'].iloc[0]
                
            with col2:
                # Shop selector
                shops = st.session_state.pipeline.shops[['shop_id', 'shop_name']].drop_duplicates()
                selected_shop = st.selectbox(
                    "Select Shop", 
                    shops['shop_name'],
                    key="shop_select"
                )
                shop_id = shops[shops['shop_name']==selected_shop]['shop_id'].iloc[0]
            
            # Get predictions with better error handling
            try:
                prediction = st.session_state.pipeline.predict_for_product_shop(product_id, shop_id)
                history = st.session_state.pipeline.get_product_shop_history(product_id, shop_id)
                
                # Display prediction with confidence indicator
                col1, col2 = st.columns(2)
                with col1:
                    confidence_colors = {
                        'high': '#28a745',      # Green
                        'medium': '#ffc107',    # Yellow
                        'low': '#fd7e14',       # Orange
                        'very_low': '#dc3545'   # Red
                    }
                    confidence = prediction.get('confidence', 'unknown')
                    color = confidence_colors.get(confidence, '#6c757d')
                    
                    st.markdown(f"""
                    <div class='card'>
                        <h3>🔮 Next Month Prediction</h3>
                        <h2 style='color: {color};'>{prediction['predicted_quantity']:,.0f} units</h2>
                        <p><strong>Last month:</strong> {prediction['last_actual']:,.0f} units ({prediction['last_date']})</p>
                        <p style='color: {color}; font-weight: bold;'>Confidence: {confidence.title()}</p>
                        <p style='font-size: 0.9em; color: #666;'>{prediction.get('note', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if prediction['last_actual'] > 0:
                        change = prediction['predicted_quantity'] - prediction['last_actual']
                        pct_change = (change / prediction['last_actual']) * 100
                        change_color = '#28a745' if change >= 0 else '#dc3545'
                        
                        st.markdown(f"""
                        <div class='card'>
                            <h3>📊 Change from Last Month</h3>
                            <h2 style='color: {change_color};'>
                                {change:+,.0f} units ({pct_change:+.1f}%)
                            </h2>
                            <p style='color: #666; font-size: 0.9em;'>
                                Historical data points: {prediction['historical_points']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='card'>
                            <h3>📊 New Combination</h3>
                            <p style='color: #666;'>No historical sales data</p>
                            <p style='color: #666; font-size: 0.9em;'>Prediction based on similar patterns</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show available combinations for this product or shop
                if prediction['historical_points'] == 0:
                    st.info("💡 **Tip:** This product-shop combination has no historical data. Try selecting a different combination or check the 'Available Combinations' section below.")
                    
                    # Show available combinations
                    with st.expander("🔍 View Available Product-Shop Combinations"):
                        combinations = st.session_state.pipeline.get_available_combinations()
                        if len(combinations) > 0:
                            # Filter by current product or shop
                            product_combinations = combinations[combinations['product_id'] == str(product_id)]
                            shop_combinations = combinations[combinations['shop_id'] == str(shop_id)]
                            
                            if len(product_combinations) > 0:
                                st.markdown(f"**Available shops for {selected_product}:**")
                                st.dataframe(product_combinations[['shop_id', 'shop_city', 'data_points', 'avg_monthly_qty']].head())
                            
                            if len(shop_combinations) > 0:
                                st.markdown(f"**Available products for {selected_shop}:**")
                                st.dataframe(shop_combinations[['product_name', 'data_points', 'avg_monthly_qty']].head())
                        else:
                            st.warning("No historical data available for any product-shop combinations")
                
                # Historical trend (only if data exists)
                if len(history) > 0:
                    st.markdown("### 📈 Historical Sales Trend")
                    fig = px.line(
                        history, 
                        x='year_month', 
                        y='monthly_quantity',
                        title=f"Sales History: {selected_product} at {selected_shop}",
                        markers=True
                    )
                    fig.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Quantity Sold",
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 No historical sales chart available - this is a new product-shop combination")
                
            except Exception as e:
                st.error(f"Error generating prediction: {str(e)}")
                st.info("💡 This might be a new product-shop combination. Try selecting a different product or shop from the dropdowns.")
                
                # Show debug info
                with st.expander("🔧 Debug Information"):
                    st.write(f"Selected Product ID: {product_id}")
                    st.write(f"Selected Shop ID: {shop_id}")
                    st.write(f"Error details: {str(e)}")
        
        else:
            st.warning("Please train the model first using the sidebar")

    with tab2:  # Product Insights
        st.markdown("## 🛍 Product Insights")
        
        if st.session_state.model_trained:
            # Top products
            top_products = st.session_state.pipeline.monthly_data.groupby(['product_id', 'product_name'])\
                .agg({'monthly_quantity': 'sum'})\
                .sort_values('monthly_quantity', ascending=False)\
                .head(10)\
                .reset_index()
            
            fig = px.bar(
                top_products, 
                x='monthly_quantity', 
                y='product_name',
                title="Top Selling Products",
                orientation='h',
                color='monthly_quantity'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Competitive analysis (premium only)
            if st.session_state.subscription == "Premium":
                try:
                    st.markdown("### 🏆 Competitive Analysis")
                    product_for_analysis = st.selectbox(
                        "Select Product for Analysis",
                        st.session_state.pipeline.products['product_name'].unique(),
                        key="comp_product_select"
                    )
                    product_id = st.session_state.pipeline.products[
                        st.session_state.pipeline.products['product_name'] == product_for_analysis
                    ]['product_id'].iloc[0]
                    
                    analysis = st.session_state.pipeline.get_competitive_analysis(product_id)
                    
                    st.markdown(f"**Category:** {analysis['category']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Top Competing Products")
                        st.dataframe(
                            analysis['top_products'].merge(
                                st.session_state.pipeline.products[['product_id', 'product_name']],
                                on='product_id'
                            ).rename(columns={'monthly_quantity': 'Avg Monthly Sales'}),
                            hide_index=True
                        )
                    
                    with col2:
                        st.markdown("#### Top Selling Locations")
                        st.dataframe(
                            analysis['top_shops'].merge(
                                st.session_state.pipeline.shops[['shop_id', 'shop_name', 'city']],
                                on='shop_id'
                            ).rename(columns={'monthly_quantity': 'Avg Monthly Sales'}),
                            hide_index=True
                        )
                    
                except Exception as e:
                    st.error(f"Error in competitive analysis: {str(e)}")
            else:
                st.markdown("""
                <div class='card'>
                    <h3>🔒 Premium Feature</h3>
                    <p>Upgrade to Premium to unlock competitive analysis</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Category analysis
            st.markdown("### 📦 Category Performance")
            category_sales = st.session_state.pipeline.monthly_data.groupby('category')\
                .agg({'monthly_quantity': 'sum'})\
                .reset_index()
            
            fig = px.pie(
                category_sales,
                values='monthly_quantity',
                names='category',
                title="Sales by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("Please train the model first using the sidebar")

    with tab3:  # Store Analytics
        st.markdown("## 🏪 Store Analytics")
        
        if st.session_state.model_trained:
            # Store selector
            selected_store = st.selectbox(
                "Select Store",
                st.session_state.pipeline.shops['shop_name'],
                key="store_select"
            )
            shop_id = st.session_state.pipeline.shops[
                st.session_state.pipeline.shops['shop_name'] == selected_store
            ]['shop_id'].iloc[0]
            
            # Store performance
            store_perf = st.session_state.pipeline.monthly_data[
                st.session_state.pipeline.monthly_data['shop_id'] == shop_id
            ].groupby('year_month').agg({
                'monthly_quantity': 'sum',
                'monthly_revenue': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=store_perf['year_month'].astype(str),
                y=store_perf['monthly_quantity'],
                name="Units Sold",
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=store_perf['year_month'].astype(str),
                y=store_perf['monthly_revenue'],
                name="Revenue",
                yaxis="y2",
                line=dict(color='green')
            ))
            
            fig.update_layout(
                title=f"Performance for {selected_store}",
                yaxis=dict(title="Units Sold"),
                yaxis2=dict(
                    title="Revenue",
                    overlaying="y",
                    side="right",
                    rangemode="tozero"
                ),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Store recommendations
            try:
                st.markdown("### 📋 Store Recommendations")
                recs = st.session_state.pipeline._generate_shopkeeper_recommendations()
                store_recs = [r for r in recs if r['shop_id'] == shop_id]
                
                if store_recs:
                    for rec in store_recs[:5]:  # Show top 5 recommendations
                        st.markdown(f"""
                        <div class='card'>
                            <h4>{rec['product_name']}</h4>
                            <p><strong>Action:</strong> {rec['type'].replace('_', ' ').title()}</p>
                            <p><strong>Reason:</strong> {rec['reason']}</p>
                            <p>Current: {rec['current_avg']:.1f} | Predicted: {rec['predicted']:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No specific recommendations for this store")
                    
            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")
        else:
            st.warning("Please train the model first using the sidebar")

    with tab4:  # Customer Intelligence
        st.markdown("## 👥 Customer Intelligence")
        
        if st.session_state.model_trained:
            # Customer segmentation
            st.markdown("### 🧩 Customer Segmentation")
            
            # Check if customer profiles exist
            if hasattr(st.session_state.pipeline, 'customer_profiles') and len(st.session_state.pipeline.customer_profiles) > 0:
                try:
                    # Prepare data for clustering with proper handling of missing values
                    available_columns = []
                    for col in ['total_amount_sum', 'quantity_sum', 'product_id_nunique', 'tenure_days', 'avg_basket_size']:
                        if col in st.session_state.pipeline.customer_profiles.columns:
                            available_columns.append(col)
                    
                    if len(available_columns) < 2:
                        st.warning("Not enough customer features available for segmentation")
                    else:
                        # Get features and handle missing values
                        features = st.session_state.pipeline.customer_profiles[available_columns].copy()
                        
                        # Replace infinite values with NaN
                        features = features.replace([np.inf, -np.inf], np.nan)
                        
                        # Fill NaN values with median for each column
                        for col in features.columns:
                            if features[col].isna().any():
                                median_val = features[col].median()
                                if pd.isna(median_val):  # If median is also NaN, use 0
                                    median_val = 0
                                features[col] = features[col].fillna(median_val)
                        
                        # Ensure all values are finite
                        features = features.select_dtypes(include=[np.number])
                        
                        # Normalize features (handle case where std is 0)
                        features_norm = features.copy()
                        for col in features.columns:
                            mean_val = features[col].mean()
                            std_val = features[col].std()
                            if std_val > 0:
                                features_norm[col] = (features[col] - mean_val) / std_val
                            else:
                                features_norm[col] = 0  # If std is 0, set normalized values to 0
                        
                        # Ensure no NaN or infinite values remain
                        features_norm = features_norm.fillna(0)
                        features_norm = features_norm.replace([np.inf, -np.inf], 0)
                        
                        # Check if we have enough data points for clustering
                        if len(features_norm) < 4:
                            st.warning("Not enough customers for meaningful segmentation (need at least 4)")
                        else:
                            # Cluster (using cached result)
                            @st.cache_data
                            def perform_clustering(data, n_clusters=4):
                                # Ensure we don't have more clusters than data points
                                actual_clusters = min(n_clusters, len(data))
                                if actual_clusters < 2:
                                    actual_clusters = 2
                                
                                kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
                                clusters = kmeans.fit_predict(data)
                                return clusters, actual_clusters
                            
                            clusters, n_clusters_used = perform_clustering(features_norm.values)
                            st.session_state.pipeline.customer_profiles['cluster'] = clusters
                            
                            # Cluster visualization
                            if len(features_norm.columns) >= 2:
                                # Use first two features for visualization
                                x_col = features_norm.columns[0]
                                y_col = features_norm.columns[1]
                                
                                plot_data = pd.DataFrame({
                                    'x': features_norm[x_col],
                                    'y': features_norm[y_col],
                                    'cluster': clusters,
                                    'customer_id': st.session_state.pipeline.customer_profiles.index
                                })
                                
                                fig = px.scatter(
                                    plot_data,
                                    x='x',
                                    y='y',
                                    color='cluster',
                                    hover_data=['customer_id'],
                                    title=f"Customer Segmentation ({n_clusters_used} clusters)",
                                    labels={'x': x_col.replace('_', ' ').title(), 
                                           'y': y_col.replace('_', ' ').title()}
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Cluster summary
                                st.markdown("#### Cluster Summary")
                                cluster_summary = st.session_state.pipeline.customer_profiles.groupby('cluster').agg({
                                    col: ['mean', 'count'] for col in available_columns
                                }).round(2)
                                
                                # Flatten column names
                                cluster_summary.columns = ['_'.join(col).strip() for col in cluster_summary.columns.values]
                                st.dataframe(cluster_summary)
                            else:
                                st.info("Need at least 2 features for visualization")
                
                except Exception as e:
                    st.error(f"Error in customer segmentation: {str(e)}")
                    st.info("This might be due to insufficient customer data or data quality issues")
                    
                    # Show available customer data for debugging
                    if hasattr(st.session_state.pipeline, 'customer_profiles'):
                        st.markdown("**Available customer data:**")
                        st.write(f"Number of customers: {len(st.session_state.pipeline.customer_profiles)}")
                        st.write(f"Available columns: {list(st.session_state.pipeline.customer_profiles.columns)}")
                        if len(st.session_state.pipeline.customer_profiles) > 0:
                            st.write("Sample data:")
                            st.dataframe(st.session_state.pipeline.customer_profiles.head())
            else:
                st.warning("No customer profiles available. This might be because customer data is missing or not properly processed.")
            
            # Customer recommendations
            st.markdown("### 💡 Personalized Recommendations")
            try:
                # Check if we have customer data
                if hasattr(st.session_state.pipeline, 'customer_profiles') and len(st.session_state.pipeline.customer_profiles) > 0:
                    # Try to generate recommendations
                    try:
                        recs = st.session_state.pipeline._generate_customer_recommendations()
                        
                        if recs and len(recs) > 0:
                            # Select a customer
                            available_customers = list(st.session_state.pipeline.customer_profiles.index.unique())
                            if available_customers:
                                customer_id = st.selectbox(
                                    "Select Customer",
                                    available_customers,
                                    key="customer_select"
                                )
                                
                                # Filter recommendations
                                customer_recs = [r for r in recs if r.get('customer_id') == customer_id]
                                
                                if customer_recs:
                                    st.markdown(f"#### Recommendations for customer {customer_id}")
                                    for rec in customer_recs[:3]:  # Show top 3 recommendations
                                        st.markdown(f"""
                                        <div class='card'>
                                            <h4>{rec.get('product_name', 'Product')}</h4>
                                            <p><strong>Category:</strong> {rec.get('category', 'Unknown')}</p>
                                            <p><strong>Reason:</strong> {rec.get('reason', 'Recommended based on purchase history')}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info(f"No specific recommendations available for customer {customer_id}")
                            else:
                                st.info("No customers available for recommendations")
                        else:
                            st.info("No customer recommendations generated")
                    except AttributeError:
                        st.info("Customer recommendation feature not available in current pipeline version")
                    except Exception as rec_error:
                        st.warning(f"Could not generate customer recommendations: {str(rec_error)}")
                        st.info("Showing basic customer analysis instead")
                        
                        # Show basic customer analysis
                        if len(st.session_state.pipeline.customer_profiles) > 0:
                            st.markdown("#### Top Customers by Spending")
                            if 'total_amount_sum' in st.session_state.pipeline.customer_profiles.columns:
                                top_customers = st.session_state.pipeline.customer_profiles.nlargest(5, 'total_amount_sum')
                                st.dataframe(top_customers[['total_amount_sum', 'quantity_sum']].round(2))
                else:
                    st.info("Customer recommendations require customer profile data")
                    
            except Exception as e:
                st.error(f"Error in customer recommendations section: {str(e)}")
            
            # Word cloud of popular terms (premium only)
            if st.session_state.subscription == "Premium":
                try:
                    st.markdown("### ☁️ Popular Product Terms")
                    
                    # Check if the method exists
                    if hasattr(st.session_state.pipeline, 'generate_naming_recommendations'):
                        naming_recs = st.session_state.pipeline.generate_naming_recommendations()
                        
                        # Create word cloud
                        if 'top_words' in naming_recs and naming_recs['top_words']:
                            wordcloud = WordCloud(width=800, height=400).generate_from_frequencies(
                                dict(naming_recs['top_words'])
                            )
                            
                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)
                            
                            if 'recommendation' in naming_recs:
                                st.markdown(f"**Recommendation:** {naming_recs['recommendation']}")
                        else:
                            st.info("No word frequency data available")
                    else:
                        # Fallback: create basic word cloud from product names
                        product_names = " ".join(st.session_state.pipeline.products['product_name'].astype(str))
                        if product_names.strip():
                            wordcloud = WordCloud(width=800, height=400).generate(product_names)
                            
                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)
                            
                            st.markdown("**Analysis:** Word cloud generated from product names in your catalog")
                        else:
                            st.info("No product name data available for word cloud")
                        
                except Exception as e:
                    st.error(f"Error generating word cloud: {str(e)}")
                    st.info("Word cloud feature temporarily unavailable")
            else:
                st.markdown("""
                <div class='card'>
                    <h3>🔒 Premium Feature</h3>
                    <p>Upgrade to Premium to unlock product naming insights</p>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.warning("Please train the model first using the sidebar")

else:
    st.markdown("""
    <div style='text-align: center; padding: 5rem;'>
        <h2>Welcome to Retail AI Predictor Pro</h2>
        <p>Upload your retail data in the sidebar to get started</p>
        <div style='margin-top: 2rem;'>
            <img src='https://cdn-icons-png.flaticon.com/512/3713/3713543.png' width='200'>
        </div>
    </div>
    """, unsafe_allow_html=True)

# END OF FILE - Remove everything after this line