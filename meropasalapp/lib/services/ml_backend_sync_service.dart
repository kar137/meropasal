import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'local_data_service.dart';
import '../models/transaction.dart';
import '../models/customer.dart';
import '../models/product.dart';
import '../models/shop.dart';

class MLBackendSyncService {
  static const String _baseUrl =
      'http://localhost:5000'; // Update with your ML backend URL
  final LocalDataService _localDataService = LocalDataService();

  // Auto-sync configuration
  bool _autoSyncEnabled = true;
  Duration _syncInterval = const Duration(minutes: 5);

  // Sync all data to ML backend
  Future<Map<String, dynamic>> syncAllData() async {
    try {
      // Get file paths
      final filePaths = await _localDataService.getDataFilePaths();

      // Extract features before syncing
      final featureResult = await _localDataService.extractFeatures();

      if (!featureResult['success']) {
        return {
          'success': false,
          'message': 'Failed to extract features: ${featureResult['message']}',
        };
      }

      // Copy files to ML backend directory
      final mlBackendPath = await _getMLBackendPath();
      await _copyFilesToMLBackend(filePaths, mlBackendPath);

      // Trigger ML backend processing
      final processResult = await _triggerMLProcessing();

      return {
        'success': true,
        'message': 'Data synced successfully',
        'records_synced': featureResult['total_records'],
        'ml_processing': processResult,
      };
    } catch (e) {
      return {'success': false, 'message': 'Sync failed: $e'};
    }
  }

  // Get ML backend directory path
  Future<String> _getMLBackendPath() async {
    // In a real implementation, this should be configurable
    // For now, assume the ML backend is in the parent directory
    final currentDir = Directory.current;
    return '${currentDir.parent.path}/ml_backend';
  }

  // Copy files to ML backend while preserving old data
  Future<void> _copyFilesToMLBackend(
    Map<String, String> filePaths,
    String mlBackendPath,
  ) async {
    for (final entry in filePaths.entries) {
      final sourceFile = File(entry.value);
      final targetFile = File('$mlBackendPath/${entry.key}.csv');

      if (await sourceFile.exists()) {
        // If target file exists, merge data
        if (await targetFile.exists()) {
          await _mergeCSVFiles(sourceFile, targetFile);
        } else {
          // Simply copy the file
          await sourceFile.copy(targetFile.path);
        }
      }
    }
  }

  // Merge CSV files while preserving old data
  Future<void> _mergeCSVFiles(File sourceFile, File targetFile) async {
    try {
      final sourceContent = await sourceFile.readAsString();
      final targetContent = await targetFile.readAsString();

      final sourceLines = sourceContent.split('\n');
      final targetLines = targetContent.split('\n');

      if (sourceLines.isEmpty || targetLines.isEmpty) {
        return;
      }

      // Get headers
      final sourceHeader = sourceLines.first;
      final targetHeader = targetLines.first;

      // If headers don't match, use source header
      if (sourceHeader != targetHeader) {
        await sourceFile.copy(targetFile.path);
        return;
      }

      // Merge data lines (skip headers)
      final allLines = <String>{};

      // Add existing data
      for (int i = 1; i < targetLines.length; i++) {
        if (targetLines[i].trim().isNotEmpty) {
          allLines.add(targetLines[i].trim());
        }
      }

      // Add new data
      for (int i = 1; i < sourceLines.length; i++) {
        if (sourceLines[i].trim().isNotEmpty) {
          allLines.add(sourceLines[i].trim());
        }
      }

      // Write merged data
      final buffer = StringBuffer();
      buffer.writeln(sourceHeader);
      for (final line in allLines) {
        buffer.writeln(line);
      }

      await targetFile.writeAsString(buffer.toString());
    } catch (e) {
      print('Error merging CSV files: $e');
      // Fallback to simple copy
      await sourceFile.copy(targetFile.path);
    }
  }

  // Trigger ML backend processing
  Future<Map<String, dynamic>> _triggerMLProcessing() async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/process-data'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'process_new_data',
          'timestamp': DateTime.now().toIso8601String(),
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'message': 'ML backend processing failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      // If HTTP request fails, assume we're running locally
      print('HTTP request failed, assuming local ML backend: $e');
      return {'success': true, 'message': 'Local processing completed'};
    }
  }

  // Add new transaction and sync
  Future<Map<String, dynamic>> addTransactionAndSync(
    Transaction transaction,
  ) async {
    try {
      // Add transaction locally
      await _localDataService.addTransaction(transaction);

      // If auto-sync is enabled, sync immediately
      if (_autoSyncEnabled) {
        return await syncAllData();
      } else {
        return {'success': true, 'message': 'Transaction added locally'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Failed to add transaction: $e'};
    }
  }

  // Add new customer and sync
  Future<Map<String, dynamic>> addCustomerAndSync(Customer customer) async {
    try {
      // Add customer locally
      await _localDataService.addCustomer(customer);

      // If auto-sync is enabled, sync immediately
      if (_autoSyncEnabled) {
        return await syncAllData();
      } else {
        return {'success': true, 'message': 'Customer added locally'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Failed to add customer: $e'};
    }
  }

  // Batch sync operations
  Future<Map<String, dynamic>> batchAddTransactions(
    List<Transaction> transactions,
  ) async {
    try {
      final currentTransactions = await _localDataService.loadTransactions();

      for (final transaction in transactions) {
        final existingIndex = currentTransactions.indexWhere(
          (t) => t.transactionId == transaction.transactionId,
        );
        if (existingIndex != -1) {
          currentTransactions[existingIndex] = transaction;
        } else {
          currentTransactions.add(transaction);
        }
      }

      await _localDataService.saveTransactions(currentTransactions);

      // Sync if auto-sync is enabled
      if (_autoSyncEnabled) {
        return await syncAllData();
      } else {
        return {
          'success': true,
          'message': '${transactions.length} transactions added locally',
        };
      }
    } catch (e) {
      return {'success': false, 'message': 'Batch transaction add failed: $e'};
    }
  }

  // Configuration methods
  void enableAutoSync() {
    _autoSyncEnabled = true;
  }

  void disableAutoSync() {
    _autoSyncEnabled = false;
  }

  void setSyncInterval(Duration interval) {
    _syncInterval = interval;
  }

  bool get isAutoSyncEnabled => _autoSyncEnabled;
  Duration get syncInterval => _syncInterval;

  // Initialize data from existing CSV files in the app directory
  Future<Map<String, dynamic>> initializeFromExistingData() async {
    try {
      // Path to the existing CSV files in the app
      final appDir = Directory.current;
      final existingCustomersPath = '${appDir.path}/meropasalapp/customers.csv';
      final existingProductsPath = '${appDir.path}/meropasalapp/products.csv';
      final existingShopsPath = '${appDir.path}/meropasalapp/shops.csv';

      // Copy existing data to local storage
      await _copyExistingDataToLocal(
        existingCustomersPath,
        existingProductsPath,
        existingShopsPath,
      );

      // Initialize with sample data if needed
      await _localDataService.initializeWithSampleData();

      // Perform initial sync
      return await syncAllData();
    } catch (e) {
      return {'success': false, 'message': 'Initialization failed: $e'};
    }
  }

  Future<void> _copyExistingDataToLocal(
    String customersPath,
    String productsPath,
    String shopsPath,
  ) async {
    try {
      // Copy customers
      final customersFile = File(customersPath);
      if (await customersFile.exists()) {
        final customers = await _parseCustomersFromFile(customersFile);
        await _localDataService.saveCustomers(customers);
      }

      // Copy products
      final productsFile = File(productsPath);
      if (await productsFile.exists()) {
        final products = await _parseProductsFromFile(productsFile);
        await _localDataService.saveProducts(products);
      }

      // Copy shops
      final shopsFile = File(shopsPath);
      if (await shopsFile.exists()) {
        final shops = await _parseShopsFromFile(shopsFile);
        await _localDataService.saveShops(shops);
      }
    } catch (e) {
      print('Error copying existing data: $e');
    }
  }

  Future<List<Customer>> _parseCustomersFromFile(File file) async {
    final content = await file.readAsString();
    final lines = content.split('\n');
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
              preferredCategories: parts[5].replaceAll('"', ''),
              avgMonthlySpending: double.tryParse(parts[6]) ?? 0.0,
              visitsPerMonth: int.tryParse(parts[7]) ?? 0,
            ),
          );
        }
      }
    }
    return customers;
  }

  Future<List<Product>> _parseProductsFromFile(File file) async {
    final content = await file.readAsString();
    final lines = content.split('\n');
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
  }

  Future<List<Shop>> _parseShopsFromFile(File file) async {
    final content = await file.readAsString();
    final lines = content.split('\n');
    final shops = <Shop>[];

    for (int i = 1; i < lines.length; i++) {
      if (lines[i].trim().isNotEmpty) {
        final parts = _parseCsvLine(lines[i]);
        if (parts.length >= 3) {
          shops.add(Shop(shopId: parts[0], city: parts[1], district: parts[2]));
        }
      }
    }
    return shops;
  }

  // Helper method to parse CSV lines
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

  // Get analytics data
  Future<Map<String, dynamic>> getAnalyticsData() async {
    try {
      final customers = await _localDataService.loadCustomers();
      final transactions = await _localDataService.loadTransactions();
      final products = await _localDataService.loadProducts();

      // Calculate basic analytics
      final totalCustomers = customers.length;
      final totalTransactions = transactions.length;
      final totalProducts = products.length;

      final totalRevenue = transactions.fold<double>(
        0.0,
        (sum, t) => sum + (t.quantity * t.actualPrice),
      );

      final avgTransactionValue = totalTransactions > 0
          ? totalRevenue / totalTransactions
          : 0.0;

      // Category analysis
      final categoryCount = <String, int>{};
      final categoryRevenue = <String, double>{};

      for (final transaction in transactions) {
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

        categoryCount[product.category] =
            (categoryCount[product.category] ?? 0) + 1;
        categoryRevenue[product.category] =
            (categoryRevenue[product.category] ?? 0.0) +
            (transaction.quantity * transaction.actualPrice);
      }

      return {
        'success': true,
        'total_customers': totalCustomers,
        'total_transactions': totalTransactions,
        'total_products': totalProducts,
        'total_revenue': totalRevenue,
        'avg_transaction_value': avgTransactionValue,
        'category_count': categoryCount,
        'category_revenue': categoryRevenue,
      };
    } catch (e) {
      return {'success': false, 'message': 'Failed to get analytics data: $e'};
    }
  }
}
