import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../models/transaction.dart';
import '../models/customer.dart';
import '../models/product.dart';
import '../models/shop.dart';

class LocalDataService {
  static const String _customersFileName = 'customers.csv';
  static const String _transactionsFileName = 'transactions.csv';
  static const String _productsFileName = 'products.csv';
  static const String _shopsFileName = 'shops.csv';
  static const String _featuresFileName = 'extracted_features.csv';

  // Get the application documents directory
  Future<Directory> get _localPath async {
    final directory = await getApplicationDocumentsDirectory();
    return directory;
  }

  // Get file paths
  Future<File> get _customersFile async {
    final path = await _localPath;
    return File('${path.path}/$_customersFileName');
  }

  Future<File> get _transactionsFile async {
    final path = await _localPath;
    return File('${path.path}/$_transactionsFileName');
  }

  Future<File> get _productsFile async {
    final path = await _localPath;
    return File('${path.path}/$_productsFileName');
  }

  Future<File> get _shopsFile async {
    final path = await _localPath;
    return File('${path.path}/$_shopsFileName');
  }

  Future<File> get _featuresFile async {
    final path = await _localPath;
    return File('${path.path}/$_featuresFileName');
  }

  // Customer operations
  Future<List<Customer>> loadCustomers() async {
    try {
      final file = await _customersFile;
      if (!await file.exists()) {
        return [];
      }

      final contents = await file.readAsString();
      final lines = contents.split('\n');

      if (lines.isEmpty || lines.first.trim().isEmpty) {
        return [];
      }

      // Skip header line
      final customers = <Customer>[];
      for (int i = 1; i < lines.length; i++) {
        if (lines[i].trim().isNotEmpty) {
          final parts = _parseCsvLine(lines[i]);
          if (parts.length >= 8) {
            customers.add(
              Customer(
                customerId: parts[0],
                customerName: parts[1],
                gender: parts[2],
                age: int.tryParse(parts[3]) ?? 0,
                city: parts[4],
                preferredCategories: parts[5],
                avgMonthlySpending: double.tryParse(parts[6]) ?? 0.0,
                visitsPerMonth: int.tryParse(parts[7]) ?? 0,
              ),
            );
          }
        }
      }
      return customers;
    } catch (e) {
      print('Error loading customers: $e');
      return [];
    }
  }

  Future<void> saveCustomers(List<Customer> customers) async {
    try {
      final file = await _customersFile;
      final buffer = StringBuffer();

      // Add header
      buffer.writeln(Customer.getCsvHeader());

      // Add data
      for (final customer in customers) {
        buffer.writeln(customer.toCsvRow());
      }

      await file.writeAsString(buffer.toString());
    } catch (e) {
      print('Error saving customers: $e');
    }
  }

  Future<void> addCustomer(Customer customer) async {
    final customers = await loadCustomers();

    // Check if customer already exists
    final existingIndex = customers.indexWhere(
      (c) => c.customerId == customer.customerId,
    );
    if (existingIndex != -1) {
      customers[existingIndex] = customer;
    } else {
      customers.add(customer);
    }

    await saveCustomers(customers);
  }

  // Transaction operations
  Future<List<Transaction>> loadTransactions() async {
    try {
      final file = await _transactionsFile;
      if (!await file.exists()) {
        return [];
      }

      final contents = await file.readAsString();
      final lines = contents.split('\n');

      if (lines.isEmpty || lines.first.trim().isEmpty) {
        return [];
      }

      // Skip header line
      final transactions = <Transaction>[];
      for (int i = 1; i < lines.length; i++) {
        if (lines[i].trim().isNotEmpty) {
          final parts = _parseCsvLine(lines[i]);
          if (parts.length >= 8) {
            transactions.add(
              Transaction(
                transactionId: parts[0],
                customerId: parts[1],
                productId: parts[2],
                shopId: parts[3],
                quantity: int.tryParse(parts[4]) ?? 0,
                actualPrice: double.tryParse(parts[5]) ?? 0.0,
                transactionDate: DateTime.tryParse(parts[6]) ?? DateTime.now(),
                paymentMethod: parts[7],
              ),
            );
          }
        }
      }
      return transactions;
    } catch (e) {
      print('Error loading transactions: $e');
      return [];
    }
  }

  Future<void> saveTransactions(List<Transaction> transactions) async {
    try {
      final file = await _transactionsFile;
      final buffer = StringBuffer();

      // Add header
      buffer.writeln(Transaction.getCsvHeader());

      // Add data
      for (final transaction in transactions) {
        buffer.writeln(transaction.toCsvRow());
      }

      await file.writeAsString(buffer.toString());
    } catch (e) {
      print('Error saving transactions: $e');
    }
  }

  Future<void> addTransaction(Transaction transaction) async {
    final transactions = await loadTransactions();

    // Check if transaction already exists
    final existingIndex = transactions.indexWhere(
      (t) => t.transactionId == transaction.transactionId,
    );
    if (existingIndex != -1) {
      transactions[existingIndex] = transaction;
    } else {
      transactions.add(transaction);
    }

    await saveTransactions(transactions);
  }

  // Product operations
  Future<List<Product>> loadProducts() async {
    try {
      final file = await _productsFile;
      if (!await file.exists()) {
        return [];
      }

      final contents = await file.readAsString();
      final lines = contents.split('\n');

      if (lines.isEmpty || lines.first.trim().isEmpty) {
        return [];
      }

      // Skip header line
      final products = <Product>[];
      for (int i = 1; i < lines.length; i++) {
        if (lines[i].trim().isNotEmpty) {
          final parts = _parseCsvLine(lines[i]);
          if (parts.length >= 5) {
            products.add(
              Product(
                productId: parts[0],
                productName: parts[1],
                category: parts[2],
                brand: parts[3],
                standardPrice: double.tryParse(parts[4]) ?? 0.0,
              ),
            );
          }
        }
      }
      return products;
    } catch (e) {
      print('Error loading products: $e');
      return [];
    }
  }

  Future<void> saveProducts(List<Product> products) async {
    try {
      final file = await _productsFile;
      final buffer = StringBuffer();

      // Add header
      buffer.writeln(Product.getCsvHeader());

      // Add data
      for (final product in products) {
        buffer.writeln(product.toCsvRow());
      }

      await file.writeAsString(buffer.toString());
    } catch (e) {
      print('Error saving products: $e');
    }
  }

  // Shop operations
  Future<List<Shop>> loadShops() async {
    try {
      final file = await _shopsFile;
      if (!await file.exists()) {
        return [];
      }

      final contents = await file.readAsString();
      final lines = contents.split('\n');

      if (lines.isEmpty || lines.first.trim().isEmpty) {
        return [];
      }

      // Skip header line
      final shops = <Shop>[];
      for (int i = 1; i < lines.length; i++) {
        if (lines[i].trim().isNotEmpty) {
          final parts = _parseCsvLine(lines[i]);
          if (parts.length >= 3) {
            shops.add(
              Shop(shopId: parts[0], city: parts[1], district: parts[2]),
            );
          }
        }
      }
      return shops;
    } catch (e) {
      print('Error loading shops: $e');
      return [];
    }
  }

  Future<void> saveShops(List<Shop> shops) async {
    try {
      final file = await _shopsFile;
      final buffer = StringBuffer();

      // Add header
      buffer.writeln(Shop.getCsvHeader());

      // Add data
      for (final shop in shops) {
        buffer.writeln(shop.toCsvRow());
      }

      await file.writeAsString(buffer.toString());
    } catch (e) {
      print('Error saving shops: $e');
    }
  }

  // Helper method to parse CSV lines properly
  List<String> _parseCsvLine(String line) {
    final result = <String>[];
    bool inQuotes = false;
    String current = '';

    for (int i = 0; i < line.length; i++) {
      final char = line[i];

      if (char == '"') {
        inQuotes = !inQuotes;
      } else if (char == ',' && !inQuotes) {
        result.add(current.trim());
        current = '';
      } else {
        current += char;
      }
    }

    result.add(current.trim());
    return result;
  }

  // Feature extraction and ML backend integration
  Future<Map<String, dynamic>> extractFeatures() async {
    try {
      final customers = await loadCustomers();
      final transactions = await loadTransactions();
      final products = await loadProducts();
      final shops = await loadShops();

      // Create joined dataset
      final joinedData = <Map<String, dynamic>>[];

      for (final transaction in transactions) {
        final customer = customers.firstWhere(
          (c) => c.customerId == transaction.customerId,
          orElse: () => Customer(
            customerId: transaction.customerId,
            customerName: 'Unknown',
            gender: 'Unknown',
            age: 0,
            city: 'Unknown',
            preferredCategories: '',
            avgMonthlySpending: 0.0,
            visitsPerMonth: 0,
          ),
        );

        final product = products.firstWhere(
          (p) => p.productId == transaction.productId,
          orElse: () => Product(
            productId: transaction.productId,
            productName: 'Unknown',
            category: 'Unknown',
            brand: 'Unknown',
            standardPrice: 0.0,
          ),
        );

        final shop = shops.firstWhere(
          (s) => s.shopId == transaction.shopId,
          orElse: () => Shop(
            shopId: transaction.shopId,
            city: 'Unknown',
            district: 'Unknown',
          ),
        );

        // Extract features
        final features = {
          'transaction_id': transaction.transactionId,
          'customer_id': customer.customerId,
          'customer_name': customer.customerName,
          'customer_age': customer.age,
          'customer_gender': customer.gender,
          'customer_city': customer.city,
          'customer_preferred_categories': customer.preferredCategories,
          'customer_avg_monthly_spending': customer.avgMonthlySpending,
          'customer_visits_per_month': customer.visitsPerMonth,
          'product_id': product.productId,
          'product_name': product.productName,
          'product_category': product.category,
          'product_brand': product.brand,
          'product_standard_price': product.standardPrice,
          'shop_id': shop.shopId,
          'shop_city': shop.city,
          'shop_district': shop.district,
          'transaction_quantity': transaction.quantity,
          'transaction_actual_price': transaction.actualPrice,
          'transaction_date': transaction.transactionDate.toIso8601String(),
          'payment_method': transaction.paymentMethod,
          'price_difference': transaction.actualPrice - product.standardPrice,
          'price_ratio': product.standardPrice > 0
              ? transaction.actualPrice / product.standardPrice
              : 0.0,
          'total_amount': transaction.quantity * transaction.actualPrice,
          'month': transaction.transactionDate.month,
          'day_of_week': transaction.transactionDate.weekday,
          'is_weekend': transaction.transactionDate.weekday >= 6 ? 1 : 0,
        };

        joinedData.add(features);
      }

      // Save extracted features
      await _saveExtractedFeatures(joinedData);

      return {
        'success': true,
        'message': 'Features extracted successfully',
        'total_records': joinedData.length,
        'features': joinedData,
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Error extracting features: $e',
        'total_records': 0,
        'features': [],
      };
    }
  }

  Future<void> _saveExtractedFeatures(
    List<Map<String, dynamic>> features,
  ) async {
    try {
      final file = await _featuresFile;
      final buffer = StringBuffer();

      if (features.isNotEmpty) {
        // Add header
        buffer.writeln(features.first.keys.join(','));

        // Add data
        for (final feature in features) {
          final values = feature.values.map((v) => v.toString()).join(',');
          buffer.writeln(values);
        }
      }

      await file.writeAsString(buffer.toString());
    } catch (e) {
      print('Error saving extracted features: $e');
    }
  }

  // Get file paths for ML backend
  Future<Map<String, String>> getDataFilePaths() async {
    final localPath = await _localPath;
    return {
      'customers': '${localPath.path}/$_customersFileName',
      'transactions': '${localPath.path}/$_transactionsFileName',
      'products': '${localPath.path}/$_productsFileName',
      'shops': '${localPath.path}/$_shopsFileName',
      'features': '${localPath.path}/$_featuresFileName',
    };
  }

  // Initialize with sample data if files don't exist
  Future<void> initializeWithSampleData() async {
    try {
      // Check if files exist
      final customersFile = await _customersFile;
      final transactionsFile = await _transactionsFile;
      final productsFile = await _productsFile;
      final shopsFile = await _shopsFile;

      // If any file doesn't exist, copy from assets or create sample data
      if (!await customersFile.exists()) {
        await _copySampleCustomers();
      }

      if (!await transactionsFile.exists()) {
        await _createSampleTransactions();
      }

      if (!await productsFile.exists()) {
        await _copySampleProducts();
      }

      if (!await shopsFile.exists()) {
        await _copySampleShops();
      }

      // Extract features after initialization
      await extractFeatures();
    } catch (e) {
      print('Error initializing sample data: $e');
    }
  }

  Future<void> _copySampleCustomers() async {
    // This would copy from assets, for now create sample data
    final sampleCustomers = [
      Customer(
        customerId: '1',
        customerName: 'Sample Customer 1',
        gender: 'Male',
        age: 25,
        city: 'Kathmandu',
        preferredCategories: 'Snacks, Beverage',
        avgMonthlySpending: 2000.0,
        visitsPerMonth: 5,
      ),
    ];
    await saveCustomers(sampleCustomers);
  }

  Future<void> _createSampleTransactions() async {
    final sampleTransactions = [
      Transaction(
        transactionId: '1',
        customerId: '1',
        productId: '1',
        shopId: '1',
        quantity: 2,
        actualPrice: 100.0,
        transactionDate: DateTime.now(),
        paymentMethod: 'Cash',
      ),
    ];
    await saveTransactions(sampleTransactions);
  }

  Future<void> _copySampleProducts() async {
    final sampleProducts = [
      Product(
        productId: '1',
        productName: 'Sample Product',
        category: 'Snacks',
        brand: 'Sample Brand',
        standardPrice: 95.0,
      ),
    ];
    await saveProducts(sampleProducts);
  }

  Future<void> _copySampleShops() async {
    final sampleShops = [
      Shop(shopId: '1', city: 'Kathmandu', district: 'Kathmandu'),
    ];
    await saveShops(sampleShops);
  }
}
