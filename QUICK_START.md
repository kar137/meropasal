# Quick Start Guide - ML Backend Data Sync System

This guide will help you quickly set up and use the ML Backend Data Sync System for MeroPasal.

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

**For ML Backend:**
```bash
cd ml_backend
pip install -r requirements.txt
```

**For Flutter App:**
```bash
cd meropasalapp
flutter pub get
```

### Step 2: Initialize the System

**Windows Users:**
```bash
# Run the setup batch file
setup_backend.bat
```

**Mac/Linux Users:**
```bash
cd ml_backend
python setup.py
```

### Step 3: Start the System

**Terminal 1 - Start ML Backend API:**
```bash
cd ml_backend
python start_api.py
```

**Terminal 2 - Run Flutter App:**
```bash
cd meropasalapp
flutter run
```

## 📱 Using the Flutter App

1. **Open the app** and tap "Open Data Management"
2. **Initialize Data** - Tap "Initialize Data" to load sample CSV data
3. **Add a Transaction** - Use the form to add new transactions
4. **Sync with ML Backend** - Tap "Sync with ML" to send data to backend
5. **View Analytics** - See real-time insights from your data

## 🔧 Key Features You Can Test

### 1. Add New Transaction
```dart
// The app automatically:
// - Validates the transaction data
// - Saves locally in CSV format
// - Syncs with ML backend (if auto-sync enabled)
// - Extracts features for ML models
// - Updates analytics in real-time
```

### 2. Feature Extraction
```python
# Features automatically extracted:
# - Customer demographics (age, gender, city)
# - Product information (category, brand, price)
# - Price differences and ratios
# - Time-based features (month, weekday, weekend)
# - Customer behavior patterns
```

### 3. Data Connection
```sql
# Automatic joins:
# transactions LEFT JOIN customers ON customer_id
# transactions LEFT JOIN products ON product_id  
# transactions LEFT JOIN shops ON shop_id
```

## 📊 Sample Data Included

The system comes with pre-loaded sample data:
- **240 Customers** from different cities (Kathmandu, Pokhara, Bhaktapur, etc.)
- **200 Products** across categories (Beverage, Snacks, Dairy, Household, Personal Care)
- **50 Shops** in various districts
- **Sample Transactions** for testing

## 🔄 Auto-Sync Features

### Enable Auto-Sync
```dart
// In Flutter app
controller.enableAutoSync();
```

### What Auto-Sync Does
1. **Monitors** local data changes
2. **Backs up** existing data before sync
3. **Merges** new data with existing ML backend data
4. **Extracts** features from combined dataset
5. **Updates** ML models with new data
6. **Preserves** all historical data

## 📈 Analytics Dashboard

View real-time analytics:
- **Total Revenue** from all transactions
- **Average Transaction Value**
- **Top Customers** by spending
- **Best-Selling Products**
- **Category Performance**
- **Monthly Trends**

## 🛠️ API Endpoints for Testing

Test the ML backend API:

```bash
# Health check
curl http://localhost:8000/api/health

# Sync data
curl -X POST http://localhost:8000/api/sync-data

# Extract features
curl -X POST http://localhost:8000/api/extract-features

# Get sync status
curl http://localhost:8000/api/sync-status
```

## 📁 File Structure After Setup

```
meropasal/
├── meropasalapp/
│   ├── lib/
│   │   ├── models/           # ✅ Data models created
│   │   ├── services/         # ✅ Data services created
│   │   ├── controllers/      # ✅ Transaction controller created
│   │   └── screens/          # ✅ Data management UI created
│   └── [Documents]/          # 📱 Local CSV storage
│       ├── customers.csv
│       ├── transactions.csv
│       ├── products.csv
│       └── extracted_features.csv
│
└── ml_backend/
    ├── customers.csv         # 🔄 Synced data
    ├── transactions.csv      # 🔄 Synced data
    ├── products.csv          # 🔄 Synced data
    ├── shops.csv             # 🔄 Synced data
    ├── extracted_features.csv # 🧠 ML-ready features
    ├── backups/              # 💾 Automatic backups
    └── sync.log              # 📋 Sync history
```

## ⚡ Quick Test Scenarios

### Scenario 1: Add Transaction and Auto-Sync
1. Add a new transaction in the Flutter app
2. Watch it automatically sync to ML backend
3. Check the extracted features file
4. View updated analytics

### Scenario 2: Batch Data Import
1. Add multiple transactions via the batch function
2. See them merge with existing data
3. Verify no duplicates are created
4. Check feature extraction results

### Scenario 3: Historical Data Preservation
1. Check existing data count
2. Add new data
3. Verify old data is still present
4. Check backup files created

## 🐛 Troubleshooting Quick Fixes

### ML Backend Not Starting
```bash
# Check Python version (needs 3.7+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Flutter App Issues
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

### Sync Failing
1. Check if ML backend API is running (`http://localhost:8000/api/health`)
2. Verify network connectivity
3. Check logs in `ml_backend/sync.log`

### Data Not Loading
1. Check if CSV files exist in app documents directory
2. Run "Initialize Data" in the app
3. Verify file permissions

## 📚 Next Steps

Once you have the basic system running:

1. **Customize Data Models** - Modify models to match your specific data
2. **Add More Features** - Extend feature extraction logic
3. **Integrate ML Models** - Connect with your ML pipeline
4. **Scale the System** - Add more data sources and endpoints
5. **Production Deploy** - Configure for production environment

## 💡 Tips for Success

- **Start Small** - Test with sample data first
- **Monitor Logs** - Check log files for any issues
- **Backup Data** - System auto-backs up, but manual backups are good too
- **Test Incrementally** - Add features one at a time
- **Use Analytics** - Monitor system performance through the dashboard

---

🎉 **You're ready to go!** The system is now set up and you can start syncing your transaction data with the ML backend while automatically extracting features and preserving historical data.

For detailed documentation, see: `BACKEND_DATA_SYNC_README.md`
