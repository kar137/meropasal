# ML Backend Data Sync System

A comprehensive Flutter backend system that automatically extracts features from transaction and customer data, connects datasets, and continuously syncs with an ML backend while preserving historical data.

## Features

- 🔄 **Automatic Data Synchronization**: Continuously sync data between Flutter app and ML backend
- 📊 **Feature Extraction**: Extract meaningful features from transactions, customers, products, and shops data
- 🔗 **Data Connection**: Join transactions with customer, product, and shop data
- 💾 **Data Preservation**: Preserve old data while adding new records
- 📈 **Real-time Analytics**: Get insights from your transaction data
- 🚀 **ML Pipeline Integration**: Automatically update ML models with new data
- 🛡️ **Data Backup**: Automatic backup system for data safety

## Architecture

```
Flutter App (meropasalapp/)
├── Local CSV Storage
├── Data Models (Transaction, Customer, Product, Shop)
├── Data Services (LocalDataService, MLBackendSyncService)
├── Transaction Controller (GetX)
└── Data Management UI

ML Backend (ml_backend/)
├── Data Sync Manager
├── Feature Extraction Engine
├── Flask API Server
├── Retail Analytics Pipeline
└── Automatic Backup System
```

## Project Structure

```
meropasal/
├── meropasalapp/               # Flutter Application
│   ├── lib/
│   │   ├── models/             # Data Models
│   │   │   ├── transaction.dart
│   │   │   ├── customer.dart
│   │   │   ├── product.dart
│   │   │   └── shop.dart
│   │   ├── services/           # Data Services
│   │   │   ├── local_data_service.dart
│   │   │   ├── ml_backend_sync_service.dart
│   │   │   └── data_initialization_service.dart
│   │   ├── controllers/        # GetX Controllers
│   │   │   └── transaction_controller.dart
│   │   └── screens/            # UI Screens
│   │       └── data_management_page.dart
│   ├── customers.csv           # Sample customer data
│   ├── products.csv           # Sample product data
│   └── shops.csv              # Sample shop data
│
└── ml_backend/                # ML Backend System
    ├── data_sync_manager.py   # Core sync functionality
    ├── sync_api.py           # Flask API server
    ├── setup.py              # Setup script
    ├── requirements.txt      # Python dependencies
    ├── retail_analytics_pipeline.py  # ML pipeline
    └── backups/              # Automatic backups
```

## Installation & Setup

### 1. Setup ML Backend

```bash
cd ml_backend
python setup.py
```

This will:
- Install all Python dependencies
- Create necessary directories
- Setup sample data
- Create startup scripts
- Test the system

### 2. Setup Flutter App

```bash
cd meropasalapp
flutter pub get
```

### 3. Start the System

#### Start ML Backend API Server
```bash
cd ml_backend
python start_api.py
```

#### Start Data Sync (Optional - for continuous sync)
```bash
cd ml_backend
python sync_data.py --auto
```

#### Run Flutter App
```bash
cd meropasalapp
flutter run
```

## Usage

### Data Management in Flutter App

1. **Initialize Data**: Load existing CSV data into the app
2. **Add Transactions**: Add new transactions through the UI
3. **Auto-sync**: Enable automatic synchronization with ML backend
4. **Extract Features**: Generate feature datasets for ML models
5. **View Analytics**: See real-time insights from your data

### API Endpoints

The ML backend provides the following API endpoints:

- `GET /api/health` - Health check
- `POST /api/sync-data` - Sync all data
- `POST /api/process-data` - Process data and update ML pipeline
- `POST /api/extract-features` - Extract features from transactions
- `POST /api/backup-data` - Create data backup
- `GET /api/sync-status` - Get sync status and statistics

### Data Flow

1. **Flutter App** → Adds/Updates transactions locally
2. **Local Storage** → Stores data in CSV format
3. **Sync Service** → Automatically syncs with ML backend
4. **Feature Extraction** → Joins all datasets and extracts features
5. **ML Backend** → Updates models with new data
6. **Analytics** → Provides insights back to the app

## Data Schema

### Transaction Model
```dart
class Transaction {
  String transactionId;
  String customerId;
  String productId;
  String shopId;
  int quantity;
  double actualPrice;
  DateTime transactionDate;
  String paymentMethod;
}
```

### Customer Model
```dart
class Customer {
  String customerId;
  String customerName;
  String gender;
  int age;
  String city;
  String preferredCategories;
  double avgMonthlySpending;
  int visitsPerMonth;
}
```

### Product Model
```dart
class Product {
  String productId;
  String productName;
  String category;
  String brand;
  double standardPrice;
}
```

### Shop Model
```dart
class Shop {
  String shopId;
  String city;
  String district;
}
```

## Feature Extraction

The system automatically extracts the following features:

### Basic Features
- Transaction ID, Customer ID, Product ID, Shop ID
- Customer demographics (age, gender, city)
- Product information (category, brand, price)
- Shop location data

### Calculated Features
- `price_difference`: Actual price - Standard price
- `price_ratio`: Actual price / Standard price
- `total_amount`: Quantity × Actual price

### Time-based Features
- `month`: Month of transaction
- `day_of_week`: Day of week (0-6)
- `is_weekend`: 1 if weekend, 0 otherwise

### Customer Behavior Features
- `preferred_categories`: Customer's preferred product categories
- `avg_monthly_spending`: Average monthly spending
- `visits_per_month`: Average visits per month

## Configuration

### Auto-sync Configuration
```dart
// Enable auto-sync
controller.enableAutoSync();

// Disable auto-sync
controller.disableAutoSync();

// Check status
bool isEnabled = controller.isAutoSyncEnabled;
```

### ML Backend Configuration
Edit `ml_backend/config.json`:
```json
{
  "ml_backend_path": "/path/to/ml_backend",
  "flutter_data_path": "/path/to/flutter/data",
  "api_port": 8000,
  "sync_interval_minutes": 5,
  "auto_backup": true,
  "max_backups": 10,
  "log_level": "INFO"
}
```

## Analytics & Insights

The system provides real-time analytics:

- **Total Revenue**: Sum of all transaction amounts
- **Average Transaction Value**: Mean transaction value
- **Customer Insights**: Top customers by spending
- **Product Analysis**: Best-selling products
- **Category Performance**: Revenue by product category
- **Temporal Patterns**: Sales trends over time

## Data Backup & Recovery

### Automatic Backups
- Backups are created before each sync operation
- Configurable backup retention (default: 10 backups)
- Backups stored in `ml_backend/backups/`

### Manual Backup
```bash
# Via API
curl -X POST http://localhost:8000/api/backup-data

# Via Python
python -c "from data_sync_manager import DataSyncManager; DataSyncManager('.', '../meropasalapp').backup_data()"
```

## Troubleshooting

### Common Issues

1. **Sync Failed**
   - Check if ML backend API is running
   - Verify network connectivity
   - Check log files in `ml_backend/logs/`

2. **Feature Extraction Failed**
   - Ensure all CSV files exist and have data
   - Check data format consistency
   - Verify column names match expected schema

3. **Flutter App Issues**
   - Run `flutter clean && flutter pub get`
   - Check device/emulator connectivity
   - Verify permissions for file access

### Debug Mode

Enable debug logging:
```python
# In ML backend
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files
- Sync operations: `ml_backend/sync.log`
- API requests: `ml_backend/api.log`
- Feature extraction: `ml_backend/features.log`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review log files for error details

---

**Note**: This system is designed to work with the existing MeroPasal retail analytics pipeline and can be extended to support additional ML models and data sources.
