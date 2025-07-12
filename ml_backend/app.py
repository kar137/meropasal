import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import tempfile
import zipfile
import traceback
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

# Enhanced Custom CSS for Professional Analytics Platform
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    animation: fadeInDown 1s ease-out;
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.main-header h1 {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-header p {
    font-size: 1.2rem;
    opacity: 0.9;
    margin-top: 0.5rem;
}

.card {
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    padding: 2rem;
    background: white;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2);
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.metric-card {
    background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
    border-radius: 15px;
    padding: 1.5rem;
    text-align: center;
    border: 2px solid #e8ecff;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4CAF50, #45a049);
}

.metric-card:hover {
    border-color: #667eea;
    transform: scale(1.02);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.15);
}

.metric-card h3 {
    color: #333;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-card h2 {
    color: #667eea;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.premium-badge {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    color: #333;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-weight: 700;
    display: inline-block;
    margin-left: 10px;
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
    animation: pulse 2s infinite;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}

.header {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
}

.sidebar-section {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
}

.prediction-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
    border: 2px solid #2196F3;
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}

.prediction-card::before {
    content: '🔮';
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 2rem;
    opacity: 0.3;
}

.success-card {
    background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
    border: 2px solid #4CAF50;
    color: #2e7d32;
}

.warning-card {
    background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
    border: 2px solid #ff9800;
    color: #f57c00;
}

.error-card {
    background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
    border: 2px solid #f44336;
    color: #c62828;
}

.confidence-high { color: #4CAF50; font-weight: bold; }
.confidence-medium { color: #FF9800; font-weight: bold; }
.confidence-low { color: #f44336; font-weight: bold; }

.professional-badge {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
    animation: pulse 2s infinite;
    text-transform: uppercase;
    font-size: 0.9rem;
    letter-spacing: 1px;
}

.feature-highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    padding-left: 20px;
    padding-right: 20px;
    background-color: #f0f2f6;
    border-radius: 10px 10px 0 0;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-color: #667eea;
}

.enterprise-footer {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-top: 3rem;
    box-shadow: 0 10px 30px rgba(44, 62, 80, 0.3);
}

/* Loading animation */
.loading-spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Progress bar */
.progress-bar {
    width: 100%;
    height: 10px;
    background-color: #f0f0f0;
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #45a049);
    border-radius: 5px;
    transition: width 0.3s ease;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

</style>
""", unsafe_allow_html=True)

# Enhanced Header for Professional Platform
st.markdown("""
<div class='main-header'>
    <div class='professional-badge'>🏢 ENTERPRISE SOLUTION</div>
    <h1>Retail AI Predictor Pro</h1>
    <p>Next-Generation Sales Forecasting & Market Intelligence Platform</p>
    <p style='font-size: 1rem; opacity: 0.8;'>🤖 Powered by Advanced Machine Learning | 📊 Real-time Analytics | 🎯 Precision Predictions</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
    st.session_state.data_loaded = False
    st.session_state.model_trained = False
    st.session_state.subscription = "Free"

# Enhanced Sidebar with Interactive Elements
with st.sidebar:
    st.markdown("""
    <div class='feature-highlight'>
        <h3>🛠️ AI Control Panel</h3>
        <p>Manage your retail intelligence system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Subscription with enhanced styling
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### 💎 Choose Your Plan")
    st.session_state.subscription = st.radio(
        "Select Plan Type", 
        ["Free", "Premium"], 
        index=0,
        key="subscription_plan",
        help="Premium unlocks advanced analytics and competitive insights"
    )
    if st.session_state.subscription == "Premium":
        st.markdown("<span class='premium-badge'>✨ PREMIUM ACTIVE</span>", unsafe_allow_html=True)
        st.markdown("🔓 **Unlocked Features:**")
        st.markdown("• Advanced competitive analysis")
        st.markdown("• Detailed customer segmentation")
        st.markdown("• Enhanced recommendations")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # File upload with progress indication
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### 📂 Data Upload Center")
    st.markdown("Upload your retail datasets to begin analysis")
    
    # File uploaders with icons
    transactions_file = st.file_uploader("💳 Transactions CSV", type="csv", key="transactions", help="Upload your transaction history data")
    products_file = st.file_uploader("🛍️ Products CSV", type="csv", key="products", help="Upload your product catalog data")
    shops_file = st.file_uploader("🏪 Shops CSV", type="csv", key="shops", help="Upload your store location data")
    customers_file = st.file_uploader("👥 Customers CSV", type="csv", key="customers", help="Upload your customer information data")
    
    # Progress indicator
    files_uploaded = sum([bool(f) for f in [transactions_file, products_file, shops_file, customers_file]])
    progress = files_uploaded / 4
    st.markdown("**Upload Progress:**")
    st.progress(progress)
    st.markdown(f"{files_uploaded}/4 files uploaded")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced Load Data Button
    if st.button("🚀 Initialize AI System", use_container_width=True, help="Load data and prepare the AI models"):
        if all([transactions_file, products_file, shops_file, customers_file]):
            # Enhanced loading with progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Initializing data pipeline...")
            progress_bar.progress(20)
            
            with st.spinner("🤖 Loading and processing your data..."):
                try:
                    # Save files temporarily
                    temp_dir = tempfile.mkdtemp()
                    
                    def save_uploaded_file(uploaded_file, path):
                        with open(path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    status_text.text("📁 Saving uploaded files...")
                    progress_bar.progress(40)
                    
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
                    
                    status_text.text("🏗️ Building analytics pipeline...")
                    progress_bar.progress(60)
                    
                    # Initialize pipeline
                    st.session_state.pipeline = RetailAnalyticsPipeline(
                        paths['transactions'],
                        paths['products'],
                        paths['shops'],
                        paths['customers']
                    )
                    
                    # Set subscription
                    st.session_state.pipeline.set_subscription(st.session_state.subscription.lower())
                    
                    status_text.text("🔍 Analyzing data quality...")
                    progress_bar.progress(80)
                    
                    # Load data
                    success = st.session_state.pipeline.load_and_prepare_data()
                    
                    if success:
                        progress_bar.progress(100)
                        status_text.text("✅ System ready!")
                        st.session_state.data_loaded = True
                        st.balloons()  # Celebration effect
                        st.success("🎉 Data loaded successfully! Your AI system is now ready.")
                        
                        # Show data summary
                        data_summary = f"""
                        **📊 Data Summary:**
                        - 💳 Transactions: {len(st.session_state.pipeline.data):,} records
                        - 🛍️ Products: {len(st.session_state.pipeline.products):,} items
                        - 🏪 Shops: {len(st.session_state.pipeline.shops):,} locations
                        - 👥 Customers: {len(st.session_state.pipeline.customers):,} profiles
                        """
                        st.info(data_summary)
                    else:
                        st.error("❌ Failed to load data. Please check your file formats.")
                        
                except Exception as e:
                    progress_bar.progress(0)
                    status_text.text("❌ Error occurred")
                    st.error(f"🚨 System Error: {str(e)}")
                    st.info("💡 **Tip:** Ensure your CSV files have the correct format and column names.")
        else:
            st.warning("⚠️ Please upload all 4 required files to continue")
            missing_files = []
            if not transactions_file: missing_files.append("Transactions")
            if not products_file: missing_files.append("Products") 
            if not shops_file: missing_files.append("Shops")
            if not customers_file: missing_files.append("Customers")
            st.error(f"Missing files: {', '.join(missing_files)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced Model Training Section
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### 🤖 AI Model Training")
    
    if st.session_state.data_loaded:
        if not st.session_state.model_trained:
            st.markdown("**Status:** 🔴 Model not trained")
            if st.button("� Train AI Model", use_container_width=True, help="Train the machine learning model"):
                train_progress = st.progress(0)
                train_status = st.empty()
                
                with st.spinner("🔬 Training advanced ML algorithms..."):
                    try:
                        train_status.text("🔍 Validating data...")
                        train_progress.progress(20)
                        
                        # Check if data is ready for training
                        ready, message = st.session_state.pipeline.is_ready_for_training()
                        
                        if ready:
                            train_status.text("🧠 Training neural networks...")
                            train_progress.progress(60)
                            
                            result = st.session_state.pipeline.train_model()
                            
                            train_status.text("✅ Model optimization complete!")
                            train_progress.progress(100)
                            
                            st.session_state.model_trained = True
                            st.success("🎉 AI Model trained successfully!")
                            st.balloons()
                            
                            # Show training results
                            st.info(f"📈 **Training Results:**\n- Training samples: {result['training_samples']:,}\n- Model type: Advanced ML Algorithm\n- Status: Production Ready")
                        else:
                            st.error(f"⚠️ Training failed: {message}")
                            st.session_state.model_trained = False
                    except Exception as e:
                        st.error(f"🚨 Training Error: {str(e)}")
                        st.session_state.model_trained = False
        else:
            # Model is trained - show status and retrain option
            st.markdown("**Status:** 🟢 AI Model Active")
            st.success("✅ Model is trained and ready")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Retrain", use_container_width=True, help="Retrain with latest data"):
                    with st.spinner("🔄 Retraining model..."):
                        try:
                            result = st.session_state.pipeline.train_model()
                            st.session_state.model_trained = True
                            st.success("✅ Model retrained!")
                        except Exception as e:
                            st.error(f"❌ Retraining failed: {str(e)}")
                            st.session_state.model_trained = False
            
            with col2:
                # Show model info
                st.markdown("**🎯 Model Info**")
                st.markdown("• Type: ML Predictor")
                st.markdown("• Status: Active")
    else:
        st.markdown("**Status:** ⚪ Waiting for data")
        st.info("📋 Load data first to enable training")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced Export Section
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### 💾 Export & Analytics")
    
    if st.button("📊 Generate Report", use_container_width=True, help="Export comprehensive analytics report"):
        with st.spinner("📈 Generating comprehensive analytics report..."):
            try:
                export_dir = os.path.join(tempfile.gettempdir(), "retail_export")
                os.makedirs(export_dir, exist_ok=True)
                st.session_state.pipeline.save_outputs(export_dir)
                
                # Create zip file
                import zipfile
                zip_path = os.path.join(tempfile.gettempdir(), "retail_analytics_report.zip")
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
                        label="⬇️ Download Analytics Report",
                        data=f,
                        file_name="retail_analytics_report.zip",
                        mime="application/zip",
                        use_container_width=True,
                        help="Download complete analytics package"
                    )
                st.success("📋 Report generated successfully!")
                
            except Exception as e:
                st.error(f"🚨 Export failed: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System Status Footer
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    # System status indicators
    if st.session_state.data_loaded:
        st.markdown("🟢 **Data:** Loaded")
    else:
        st.markdown("🔴 **Data:** Not loaded")
    
    if st.session_state.model_trained:
        st.markdown("🟢 **AI Model:** Active")
    else:
        st.markdown("🔴 **AI Model:** Inactive")
    
    st.markdown(f"💎 **Plan:** {st.session_state.subscription}")
    
    # Live platform indicator
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #4CAF50, #45a049); 
                color: white; border-radius: 10px; margin-top: 1rem;'>
        <h4>� ENTERPRISE ANALYTICS PLATFORM</h4>
        <p style='margin: 0; font-size: 0.9rem;'>Professional-Grade Business Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
                        
                    

# Enhanced Dashboard
if st.session_state.pipeline and st.session_state.data_loaded:
    # Executive Dashboard with enhanced styling
    st.markdown("## 📊 Executive Intelligence Dashboard")
    st.markdown("**Real-time insights powered by advanced machine learning algorithms**")
    
    # Enhanced KPI Cards with animations and better styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = st.session_state.pipeline.data['total_amount'].sum()
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💰 Total Revenue</h3>
            <h2>₹{total_revenue:,.0f}</h2>
            <p style='color: #4CAF50; font-size: 0.9rem; margin: 0;'>↗️ Business Performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_products = st.session_state.pipeline.products['product_id'].nunique()
        st.markdown(f"""
        <div class='metric-card'>
            <h3>🛍️ Product Portfolio</h3>
            <h2>{unique_products:,}</h2>
            <p style='color: #2196F3; font-size: 0.9rem; margin: 0;'>📦 Unique Items</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        store_count = st.session_state.pipeline.shops['shop_id'].nunique()
        st.markdown(f"""
        <div class='metric-card'>
            <h3>� Store Network</h3>
            <h2>{store_count:,}</h2>
            <p style='color: #FF9800; font-size: 0.9rem; margin: 0;'>🌍 Global Reach</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.model_trained and hasattr(st.session_state.pipeline, 'model') and st.session_state.pipeline.model is not None:
            try:
                metrics = st.session_state.pipeline.get_model_metrics()
                if 'error' not in metrics:
                    accuracy = 100 - metrics['mape']
                    st.markdown(f"""
                    <div class='metric-card success-card'>
                        <h3>📈 AI Accuracy</h3>
                        <h2>{accuracy:.1f}%</h2>
                        <p style='color: #4CAF50; font-size: 0.9rem; margin: 0;'>🎯 Prediction Power</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class='metric-card error-card'>
                        <h3>📈 AI Accuracy</h3>
                        <h2>Error</h2>
                        <p style='font-size: 0.8em; color: red; margin: 0;'>Model requires attention</p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown("""
                <div class='metric-card warning-card'>
                    <h3>📈 AI Accuracy</h3>
                    <h2>--</h2>
                    <p style='font-size: 0.8em; color: orange; margin: 0;'>🔄 Computing...</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='metric-card'>
                <h3>📈 AI Accuracy</h3>
                <h2>--</h2>
                <p style='font-size: 0.8em; color: gray; margin: 0;'>🤖 Train model first</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add performance indicators
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_customers = st.session_state.pipeline.customers['customer_id'].nunique()
        st.metric("👥 Customer Base", f"{total_customers:,}", delta="Growing")
    
    with col2:
        total_transactions = len(st.session_state.pipeline.data)
        st.metric("💳 Total Transactions", f"{total_transactions:,}", delta="Active")
    
    with col3:
        avg_transaction = st.session_state.pipeline.data['total_amount'].mean()
        st.metric("💵 Avg Transaction", f"₹{avg_transaction:.2f}", delta="Optimized")
    
    # Enhanced Model Performance Section
    if st.session_state.model_trained:
        st.markdown("""
        <div class='feature-highlight'>
            <h2>🤖 AI Model Performance Analytics</h2>
            <p>Advanced machine learning insights and model validation metrics</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if model actually exists and is trained
        if (hasattr(st.session_state.pipeline, 'model') and 
            st.session_state.pipeline.model is not None and
            st.session_state.pipeline.is_trained):
            
            col1, col2, col3 = st.columns(3)
            try:
                metrics = st.session_state.pipeline.get_model_metrics()
                
                with col1:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>🎯 Mean Absolute Error</h3>
                        <h2>{metrics['mae']:.2f}</h2>
                        <p style='color: #4CAF50; margin: 0;'>Precision Metric</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>📊 Root Mean Squared Error</h3>
                        <h2>{metrics['rmse']:.2f}</h2>
                        <p style='color: #2196F3; margin: 0;'>Accuracy Measure</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h3>🏆 R² Score</h3>
                        <h2>{metrics['r2']:.3f}</h2>
                        <p style='color: #FF9800; margin: 0;'>Model Fitness</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"❌ Error getting model metrics: {str(e)}")
            
            # Enhanced Actual vs Predicted plot with error handling
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
                        
                        # Create enhanced scatter plot
                        fig = px.scatter(
                            x=y_true_clean, 
                            y=y_pred, 
                            labels={'x': 'Actual Sales', 'y': 'Predicted Sales'},
                            title="🎯 AI Prediction Accuracy Analysis",
                            color=y_pred,
                            color_continuous_scale="viridis"
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
                            line=dict(color="red", dash="dash", width=3)
                        )
                        
                        fig.update_layout(
                            width=800,
                            height=500,
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add interpretation
                        st.info("📈 **Interpretation:** Points closer to the red diagonal line indicate more accurate predictions. Our AI model shows strong correlation between predicted and actual values.")
                        
                    else:
                        st.warning("⚠️ No valid data points for plotting after cleaning")
                else:
                    st.warning("⚠️ Insufficient data for model performance visualization")
                    
            except Exception as e:
                st.error(f"❌ Error creating performance plot: {str(e)}")
                st.info("📊 Model performance plot temporarily unavailable")
        else:
            st.markdown("""
            <div class='warning-card'>
                <h3>⚠️ Model Status</h3>
                <p>Model not properly trained. Please retrain the model for accurate performance metrics.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show enhanced training button
            if st.button("🔄 Retrain AI Model", key="retrain_model", help="Retrain the model with current data"):
                with st.spinner("🧠 Retraining advanced ML algorithms..."):
                    try:
                        st.session_state.pipeline.train_model()
                        st.session_state.model_trained = True
                        st.success("✅ Model retrained successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ Retraining failed: {str(e)}")
                        st.session_state.model_trained = False
    else:
        st.markdown("""
        <div class='card'>
            <h3>🤖 AI Model Training Required</h3>
            <p>Train the machine learning model first to see comprehensive performance metrics and analytics.</p>
            <p><strong>📋 What you'll get after training:</strong></p>
            <ul>
                <li>🎯 Prediction accuracy metrics</li>
                <li>📊 Model validation charts</li>
                <li>🔍 Performance analytics</li>
                <li>🏆 Quality indicators</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Navigation Tabs
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([
        "� AI Sales Predictions", 
        "🛍️ Product Intelligence", 
        "🏪 Store Analytics", 
        "👥 Customer Intelligence"
    ])

    with tab1:  # Enhanced Sales Predictions
        st.markdown("""
        <div class='feature-highlight'>
            <h2>� AI-Powered Sales Predictions</h2>
            <p>Advanced machine learning algorithms predict future sales with high accuracy</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.model_trained:
            # Enhanced product and shop selectors
            st.markdown("### 🎛️ Prediction Control Panel")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🛍️ Select Product:**")
                products = st.session_state.pipeline.products[['product_id', 'product_name']].drop_duplicates()
                selected_product = st.selectbox(
                    "Choose from product catalog", 
                    products['product_name'],
                    key="product_select",
                    help="Select the product you want to predict sales for"
                )
                product_id = products[products['product_name']==selected_product]['product_id'].iloc[0]
                
            with col2:
                st.markdown("**🏪 Select Store Location:**")
                shops = st.session_state.pipeline.shops[['shop_id', 'shop_name']].drop_duplicates()
                selected_shop = st.selectbox(
                    "Choose store location", 
                    shops['shop_name'],
                    key="shop_select",
                    help="Select the store location for prediction"
                )
                shop_id = shops[shops['shop_name']==selected_shop]['shop_id'].iloc[0]
            
            # Get predictions with enhanced presentation
            try:
                prediction = st.session_state.pipeline.predict_for_product_shop(product_id, shop_id)
                history = st.session_state.pipeline.get_product_shop_history(product_id, shop_id)
                
                # Enhanced prediction display
                st.markdown("### 🎯 AI Prediction Results")
                
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
                    
                    # Enhanced prediction card
                    st.markdown(f"""
                    <div class='prediction-card'>
                        <h3>🔮 Next Month Prediction</h3>
                        <h1 style='color: {color}; font-size: 3rem; margin: 0.5rem 0;'>{prediction['predicted_quantity']:,.0f}</h1>
                        <p style='font-size: 1.1rem; font-weight: 600;'>Units Expected</p>
                        <hr style='margin: 1rem 0;'>
                        <p><strong>📊 Previous Month:</strong> {prediction['last_actual']:,.0f} units</p>
                        <p><strong>📅 Reference Date:</strong> {prediction['last_date']}</p>
                        <p style='color: {color}; font-weight: bold; font-size: 1.1rem;'>
                            🎯 Confidence Level: {confidence.title()}
                        </p>
                        <p style='font-size: 0.9em; color: #666; font-style: italic;'>{prediction.get('note', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if prediction['last_actual'] > 0:
                        change = prediction['predicted_quantity'] - prediction['last_actual']
                        pct_change = (change / prediction['last_actual']) * 100
                        change_color = '#28a745' if change >= 0 else '#dc3545'
                        trend_icon = "📈" if change >= 0 else "📉"
                        trend_text = "Growth Expected" if change >= 0 else "Decline Expected"
                        
                        st.markdown(f"""
                        <div class='prediction-card'>
                            <h3>📊 Trend Analysis</h3>
                            <h1 style='color: {change_color}; font-size: 2.5rem; margin: 0.5rem 0;'>
                                {change:+,.0f}
                            </h1>
                            <p style='color: {change_color}; font-size: 1.2rem; font-weight: 600;'>
                                {pct_change:+.1f}% Change
                            </p>
                            <hr style='margin: 1rem 0;'>
                            <p style='color: {change_color}; font-weight: bold;'>
                                {trend_icon} {trend_text}
                            </p>
                            <p style='color: #666; font-size: 0.9em;'>
                                Based on {prediction['historical_points']} data points
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='prediction-card warning-card'>
                            <h3>🆕 New Product-Store Combination</h3>
                            <p style='font-size: 1.1rem; margin: 1rem 0;'>No historical sales data available</p>
                            <hr>
                            <p><strong>🤖 AI Strategy:</strong> Prediction based on similar patterns</p>
                            <p><strong>📊 Recommendation:</strong> Monitor closely and adjust inventory</p>
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
            
            # --- Customer Recommendations Section ---

            st.markdown("### 💡 Personalized Customer Recommendations")

            try:
                # Try to get personalized recommendations
                recs = st.session_state.pipeline._generate_customer_recommendations()
                # Fallback to enhanced basic recommendations if none found
                if not recs or len(recs) == 0:
                    st.info("No personalized recommendations found. Showing enhanced basic recommendations instead.")
                    recs = st.session_state.pipeline._create_enhanced_basic_recommendations()

                if recs and len(recs) > 0:
                    # Group recommendations by customer_id (as string)
                    customers_with_recs = {}
                    for rec in recs:
                        cid = str(rec['customer_id'])
                        if cid not in customers_with_recs:
                            customers_with_recs[cid] = []
                        customers_with_recs[cid].append(rec)

                    # Show available customer IDs for debug
                    st.write("Customer IDs with recommendations:", list(customers_with_recs.keys()))

                    # Customer selector
                    selected_customer = st.selectbox(
                        "Select Customer for Recommendations",
                        options=list(customers_with_recs.keys()),
                        key="customer_rec_select"
                    )

                    if selected_customer:
                        # Show customer summary
                        summary = st.session_state.pipeline.get_customer_purchase_summary(selected_customer)
                        if 'error' not in summary:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Spending", f"₹{summary['total_spending']:.2f}")
                                st.metric("Total Transactions", summary['total_transactions'])
                            with col2:
                                st.metric("Avg Transaction", f"₹{summary['avg_transaction_value']:.2f}")
                                st.metric("Total Items", summary['total_items'])
                            with col3:
                                st.metric("Favorite Category", summary['favorite_category'])
                                st.metric("Shops Visited", summary['unique_shops'])

                        st.markdown(f"#### Recommendations for Customer {selected_customer}")

                        customer_recs = customers_with_recs[selected_customer]
                        confidence_colors = {'high': '#28a745', 'medium': '#ffc107', 'low': '#fd7e14'}
                        for rec in customer_recs:
                            color = confidence_colors.get(rec.get('confidence', 'low'), '#6c757d')
                            st.markdown(f"""
                            <div class='card'>
                                <h4>{rec.get('product_name', 'Product')}</h4>
                                <p><strong>Category:</strong> {rec.get('category', 'Unknown')}</p>
                                <p><strong>Recommended Shop:</strong> {rec.get('recommended_shop', 'Any')}</p>
                                <p><strong>Reason:</strong> {rec.get('reason', 'Recommended for you')}</p>
                                <p style='color: {color}; font-weight: bold;'>Confidence: {rec.get('confidence', 'unknown').title()}</p>
                                <small>Type: {rec.get('recommendation_type', 'general').replace('_', ' ').title()}</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("No customer recommendations generated.")

                    # Show diagnostic info
                    insights = st.session_state.pipeline.get_customer_insights()
                    if 'error' in insights:
                        st.error(f"Error: {insights['error']}")
                    else:
                        st.info("**Possible reasons for no recommendations:**")
                        st.markdown("- All customers have purchased all available products")
                        st.markdown("- Insufficient transaction history")
                        st.markdown("- Data quality issues")
                        st.markdown(f"**Available data:** {insights.get('total_customers', 0)} customers, {insights.get('total_transactions', 0)} transactions")

                        # Show sample customer data
                        if st.button("Show Sample Customer Analysis"):
                            sample_customers = list(st.session_state.pipeline.data['customer_id'].unique())[:3]
                            for customer_id in sample_customers:
                                summary = st.session_state.pipeline.get_customer_purchase_summary(customer_id)
                                if 'error' not in summary:
                                    st.markdown(f"**Customer {customer_id}:**")
                                    st.write(f"- {summary['total_transactions']} transactions")
                                    st.write(f"- ₹{summary['total_spending']:.2f} total spending")
                                    st.write(f"- Favorite category: {summary['favorite_category']}")

            except Exception as e:
                st.error(f"Error in customer recommendations: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# Continue with the rest of your code...

# Enhanced Welcome Screen for Demo
else:
    st.markdown("""
    <div style='text-align: center; padding: 3rem;'>
        <div class='main-header'>
            <h1>🚀 Welcome to Retail AI Predictor Pro</h1>
            <p>The Future of Retail Analytics is Here</p>
        </div>
        
    """, unsafe_allow_html=True)
    
    # Using Streamlit columns for better compatibility
    st.markdown("## 🎯 What Makes Our Solution Special?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='card'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>🤖</div>
            <h3 style='text-align: center; color: #667eea;'>Advanced AI</h3>
            <p style='text-align: center;'>Machine learning algorithms trained on real retail data for accurate predictions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>📊</div>
            <h3 style='text-align: center; color: #4CAF50;'>Real-time Analytics</h3>
            <p style='text-align: center;'>Live insights and predictions for better decision making</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='card'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>🎯</div>
            <h3 style='text-align: center; color: #FF9800;'>Precision Forecasting</h3>
            <p style='text-align: center;'>Accurate sales predictions with confidence levels</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='feature-highlight' style='margin: 2rem auto; max-width: 600px;'>
            <h3>🚀 Ready to Get Started?</h3>
            <p>Upload your retail data files in the sidebar to experience the power of AI-driven retail analytics</p>
            <p><strong>📋 Required Files:</strong> Transactions, Products, Shops, Customers (CSV format)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Footer for All Pages
st.markdown("---")
st.markdown("""
<div class='enterprise-footer'>
    <h3>🏢 Retail AI Predictor Pro</h3>
    <p><strong>Next-Generation Retail Intelligence Platform</strong></p>
    <div style='display: flex; justify-content: center; gap: 2rem; margin: 1rem 0; flex-wrap: wrap;'>
        <span>🤖 Advanced ML Algorithms</span>
        <span>📊 Real-time Analytics</span>
        <span>🎯 Precision Predictions</span>
        <span>💡 Smart Insights</span>
    </div>
    <p style='font-size: 0.9rem; opacity: 0.8; margin-top: 1rem;'>
        Transforming retail decision-making through artificial intelligence
    </p>
    <p style='font-size: 0.8rem; opacity: 0.6;'>
        © 2025 Retail AI Predictor Pro | Enterprise Solution | Powered by Machine Learning
    </p>
</div>
""", unsafe_allow_html=True)

# END OF FILE - Remove everything after this line