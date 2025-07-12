import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import '../models/transaction.dart';
import 'local_data_service.dart';

class DataInitializationService {
  final LocalDataService _localDataService = LocalDataService();

  /// Initialize the app with existing CSV data
  Future<Map<String, dynamic>> initializeWithExistingData() async {
    try {
      // Copy existing CSV files from the app directory to local storage
      await _copyCSVFilesToLocal();

      // Generate sample transactions if they don't exist
      await _generateSampleTransactions();

      return {
        'success': true,
        'message': 'Data initialization completed successfully',
      };
    } catch (e) {
      return {'success': false, 'message': 'Data initialization failed: $e'};
    }
  }

  /// Copy CSV files from app directory to local storage
  Future<void> _copyCSVFilesToLocal() async {
    try {
      final localPath = await getApplicationDocumentsDirectory();

      // Define the CSV files in the app directory
      final csvFiles = {
        'customers.csv': await _loadCustomersFromApp(),
        'products.csv': await _loadProductsFromApp(),
        'shops.csv': await _loadShopsFromApp(),
      };

      // Save each CSV file to local storage
      for (final entry in csvFiles.entries) {
        final fileName = entry.key;
        final data = entry.value;

        if (data.isNotEmpty) {
          final file = File('${localPath.path}/$fileName');
          await file.writeAsString(data);
          print('Copied $fileName to local storage');
        }
      }
    } catch (e) {
      print('Error copying CSV files: $e');
    }
  }

  /// Load customers from the app's CSV file
  Future<String> _loadCustomersFromApp() async {
    try {
      // Try to read from assets first, then from app directory
      String csvContent = '';

      try {
        csvContent = await rootBundle.loadString('assets/data/customers.csv');
      } catch (e) {
        // If assets don't exist, use the hard-coded data from the attachment
        csvContent = _getHardcodedCustomersCSV();
      }

      return csvContent;
    } catch (e) {
      print('Error loading customers CSV: $e');
      return _getHardcodedCustomersCSV();
    }
  }

  /// Load products from the app's CSV file
  Future<String> _loadProductsFromApp() async {
    try {
      String csvContent = '';

      try {
        csvContent = await rootBundle.loadString('assets/data/products.csv');
      } catch (e) {
        csvContent = _getHardcodedProductsCSV();
      }

      return csvContent;
    } catch (e) {
      print('Error loading products CSV: $e');
      return _getHardcodedProductsCSV();
    }
  }

  /// Load shops from the app's CSV file
  Future<String> _loadShopsFromApp() async {
    try {
      String csvContent = '';

      try {
        csvContent = await rootBundle.loadString('assets/data/shops.csv');
      } catch (e) {
        csvContent = _getHardcodedShopsCSV();
      }

      return csvContent;
    } catch (e) {
      print('Error loading shops CSV: $e');
      return _getHardcodedShopsCSV();
    }
  }

  /// Generate sample transactions for testing
  Future<void> _generateSampleTransactions() async {
    try {
      final customers = await _localDataService.loadCustomers();
      final products = await _localDataService.loadProducts();
      final shops = await _localDataService.loadShops();

      if (customers.isEmpty || products.isEmpty || shops.isEmpty) {
        print('Cannot generate transactions: missing reference data');
        return;
      }

      final transactions = <Transaction>[];
      final now = DateTime.now();

      // Generate 50 sample transactions
      for (int i = 1; i <= 50; i++) {
        final customer = customers[i % customers.length];
        final product = products[i % products.length];
        final shop = shops[i % shops.length];

        // Random transaction date within last 30 days
        final daysAgo = (i % 30);
        final transactionDate = now.subtract(Duration(days: daysAgo));

        // Random quantity between 1 and 5
        final quantity = 1 + (i % 5);

        // Price variation: ±20% of standard price
        final priceVariation = 0.8 + (0.4 * (i % 100) / 100);
        final actualPrice = product.standardPrice * priceVariation;

        final transaction = Transaction(
          transactionId: 'T${1000 + i}',
          customerId: customer.customerId,
          productId: product.productId,
          shopId: shop.shopId,
          quantity: quantity,
          actualPrice: double.parse(actualPrice.toStringAsFixed(2)),
          transactionDate: transactionDate,
          paymentMethod: ['Cash', 'Card', 'Digital'][i % 3],
        );

        transactions.add(transaction);
      }

      await _localDataService.saveTransactions(transactions);
      print('Generated ${transactions.length} sample transactions');
    } catch (e) {
      print('Error generating sample transactions: $e');
    }
  }

  /// Get hardcoded customers CSV (fallback)
  String _getHardcodedCustomersCSV() {
    return '''customer_id,customer_name,gender,age,city,preferred_categories,avg_monthly_spending,visits_per_month
1,Customer 1,Other,29,Pokhara,"Snacks, Personal Care",1406.82,12
2,Customer 2,Female,32,Bhaktapur,"Household, Personal Care",4250.83,3
3,Customer 3,Male,53,Biratnagar,Beverage,4588.2,12
4,Customer 4,Other,31,Lalitpur,Beverage,1007.41,11
5,Customer 5,Other,22,Kathmandu,Snacks,1150.9,7
6,Customer 6,Female,35,Bhaktapur,Dairy,2752.53,11
7,Customer 7,Female,38,Biratnagar,"Snacks, Household",2248.15,6
8,Customer 8,Female,23,Bhaktapur,Beverage,1175.22,2
9,Customer 9,Female,37,Biratnagar,"Personal Care, Household",2675.81,10
10,Customer 10,Other,50,Kathmandu,Beverage,4415.39,7''';
  }

  /// Get hardcoded products CSV (fallback)
  String _getHardcodedProductsCSV() {
    return '''product_id,product_name,category,brand,standard_price
1,Pepsi Bev1,Beverage,Pepsi,98.67
2,Wai Wai Sna2,Snacks,Wai Wai,442.06
3,Nestle Bev3,Beverage,Nestle,253.9
4,Nestle Bev4,Beverage,Nestle,373.24
5,Pepsi Bev5,Beverage,Pepsi,70.13
6,Surf Excel Hou6,Household,Surf Excel,166.85
7,Coca-Cola Bev7,Beverage,Coca-Cola,265.17
8,Lays Sna8,Snacks,Lays,222.77
9,Lays Sna9,Snacks,Lays,497.81
10,Coca-Cola Bev10,Beverage,Coca-Cola,395.55''';
  }

  /// Get hardcoded shops CSV (fallback)
  String _getHardcodedShopsCSV() {
    return '''shop_id,city,district
1,Lalitpur,Bhaktapur
2,Biratnagar,Kathmandu
3,Bhaktapur,Lalitpur
4,Pokhara,Lalitpur
5,Pokhara,Kathmandu
6,Biratnagar,Kathmandu
7,Kathmandu,Lalitpur
8,Pokhara,Kaski
9,Bhaktapur,Bhaktapur
10,Bhaktapur,Kaski''';
  }

  /// Copy CSV files from app directory to ML backend
  Future<Map<String, dynamic>> copyDataToMLBackend() async {
    try {
      // Get the directory paths
      final currentDir = Directory.current;
      final mlBackendPath = Directory('${currentDir.parent.path}/ml_backend');
      final appDataPath = await getApplicationDocumentsDirectory();

      if (!await mlBackendPath.exists()) {
        await mlBackendPath.create(recursive: true);
      }

      // List of CSV files to copy
      final csvFiles = [
        'customers.csv',
        'transactions.csv',
        'products.csv',
        'shops.csv',
      ];

      int copiedFiles = 0;

      for (final fileName in csvFiles) {
        final sourceFile = File('${appDataPath.path}/$fileName');
        final targetFile = File('${mlBackendPath.path}/$fileName');

        if (await sourceFile.exists()) {
          // If target exists, merge the data
          if (await targetFile.exists()) {
            await _mergeCSVFiles(sourceFile, targetFile);
          } else {
            await sourceFile.copy(targetFile.path);
          }
          copiedFiles++;
        }
      }

      return {
        'success': true,
        'message': 'Data copied to ML backend successfully',
        'files_copied': copiedFiles,
        'ml_backend_path': mlBackendPath.path,
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to copy data to ML backend: $e',
      };
    }
  }

  /// Merge CSV files while preserving existing data
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

      // If headers don't match, use source data
      if (sourceHeader != targetHeader) {
        await sourceFile.copy(targetFile.path);
        return;
      }

      // Merge data (remove duplicates)
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

  /// Get initialization status
  Future<Map<String, dynamic>> getInitializationStatus() async {
    try {
      final localPath = await getApplicationDocumentsDirectory();
      final customers = await _localDataService.loadCustomers();
      final transactions = await _localDataService.loadTransactions();
      final products = await _localDataService.loadProducts();
      final shops = await _localDataService.loadShops();

      return {
        'success': true,
        'data_path': localPath.path,
        'customers_count': customers.length,
        'transactions_count': transactions.length,
        'products_count': products.length,
        'shops_count': shops.length,
        'is_initialized':
            customers.isNotEmpty && products.isNotEmpty && shops.isNotEmpty,
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to get initialization status: $e',
      };
    }
  }
}
