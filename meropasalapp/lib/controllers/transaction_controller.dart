import 'package:get/get.dart';
import '../models/transaction.dart';
import '../models/customer.dart';
import '../models/product.dart';
import '../models/shop.dart';
import '../services/local_data_service.dart';
import '../services/ml_backend_sync_service.dart';

class TransactionController extends GetxController {
  final LocalDataService _localDataService = LocalDataService();
  final MLBackendSyncService _syncService = MLBackendSyncService();

  // Observable lists
  final RxList<Transaction> transactions = <Transaction>[].obs;
  final RxList<Customer> customers = <Customer>[].obs;
  final RxList<Product> products = <Product>[].obs;
  final RxList<Shop> shops = <Shop>[].obs;

  // Loading states
  final RxBool isLoading = false.obs;
  final RxBool isSyncing = false.obs;

  // Analytics data
  final RxMap<String, dynamic> analyticsData = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    initializeData();
  }

  // Initialize data from local storage and existing CSV files
  Future<void> initializeData() async {
    try {
      isLoading.value = true;

      // Initialize from existing data
      final initResult = await _syncService.initializeFromExistingData();

      if (initResult['success']) {
        print('Data initialization successful: ${initResult['message']}');
      } else {
        print('Data initialization failed: ${initResult['message']}');
      }

      // Load all data
      await loadAllData();

      // Load analytics
      await loadAnalytics();
    } catch (e) {
      print('Error initializing data: $e');
    } finally {
      isLoading.value = false;
    }
  }

  // Load all data from local storage
  Future<void> loadAllData() async {
    try {
      final loadedTransactions = await _localDataService.loadTransactions();
      final loadedCustomers = await _localDataService.loadCustomers();
      final loadedProducts = await _localDataService.loadProducts();
      final loadedShops = await _localDataService.loadShops();

      transactions.assignAll(loadedTransactions);
      customers.assignAll(loadedCustomers);
      products.assignAll(loadedProducts);
      shops.assignAll(loadedShops);

      print('Loaded ${transactions.length} transactions');
      print('Loaded ${customers.length} customers');
      print('Loaded ${products.length} products');
      print('Loaded ${shops.length} shops');
    } catch (e) {
      print('Error loading data: $e');
    }
  }

  // Add new transaction
  Future<Map<String, dynamic>> addTransaction({
    required String customerId,
    required String productId,
    required String shopId,
    required int quantity,
    required double actualPrice,
    required String paymentMethod,
  }) async {
    try {
      isSyncing.value = true;

      // Generate transaction ID
      final transactionId = 'T${DateTime.now().millisecondsSinceEpoch}';

      // Create transaction
      final transaction = Transaction(
        transactionId: transactionId,
        customerId: customerId,
        productId: productId,
        shopId: shopId,
        quantity: quantity,
        actualPrice: actualPrice,
        transactionDate: DateTime.now(),
        paymentMethod: paymentMethod,
      );

      // Add transaction and sync
      final result = await _syncService.addTransactionAndSync(transaction);

      if (result['success']) {
        // Update local list
        transactions.add(transaction);

        // Reload analytics
        await loadAnalytics();

        return {
          'success': true,
          'message': 'Transaction added successfully',
          'transaction_id': transactionId,
        };
      } else {
        return result;
      }
    } catch (e) {
      return {'success': false, 'message': 'Failed to add transaction: $e'};
    } finally {
      isSyncing.value = false;
    }
  }

  // Add new customer
  Future<Map<String, dynamic>> addCustomer({
    required String customerName,
    required String gender,
    required int age,
    required String city,
    required String preferredCategories,
    required double avgMonthlySpending,
    required int visitsPerMonth,
  }) async {
    try {
      isSyncing.value = true;

      // Generate customer ID
      final customerId = 'C${DateTime.now().millisecondsSinceEpoch}';

      // Create customer
      final customer = Customer(
        customerId: customerId,
        customerName: customerName,
        gender: gender,
        age: age,
        city: city,
        preferredCategories: preferredCategories,
        avgMonthlySpending: avgMonthlySpending,
        visitsPerMonth: visitsPerMonth,
      );

      // Add customer and sync
      final result = await _syncService.addCustomerAndSync(customer);

      if (result['success']) {
        // Update local list
        customers.add(customer);

        return {
          'success': true,
          'message': 'Customer added successfully',
          'customer_id': customerId,
        };
      } else {
        return result;
      }
    } catch (e) {
      return {'success': false, 'message': 'Failed to add customer: $e'};
    } finally {
      isSyncing.value = false;
    }
  }

  // Batch add transactions
  Future<Map<String, dynamic>> batchAddTransactions(
    List<Map<String, dynamic>> transactionData,
  ) async {
    try {
      isSyncing.value = true;

      final newTransactions = transactionData.map((data) {
        return Transaction(
          transactionId:
              data['transaction_id'] ??
              'T${DateTime.now().millisecondsSinceEpoch}_${data.hashCode}',
          customerId: data['customer_id'] ?? '',
          productId: data['product_id'] ?? '',
          shopId: data['shop_id'] ?? '',
          quantity: data['quantity'] ?? 0,
          actualPrice: data['actual_price']?.toDouble() ?? 0.0,
          transactionDate: data['transaction_date'] != null
              ? DateTime.tryParse(data['transaction_date']) ?? DateTime.now()
              : DateTime.now(),
          paymentMethod: data['payment_method'] ?? 'Cash',
        );
      }).toList();

      final result = await _syncService.batchAddTransactions(newTransactions);

      if (result['success']) {
        // Update local list
        transactions.addAll(newTransactions);

        // Reload analytics
        await loadAnalytics();

        return {
          'success': true,
          'message':
              '${newTransactions.length} transactions added successfully',
        };
      } else {
        return result;
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to batch add transactions: $e',
      };
    } finally {
      isSyncing.value = false;
    }
  }

  // Manual sync with ML backend
  Future<Map<String, dynamic>> syncWithMLBackend() async {
    try {
      isSyncing.value = true;

      final result = await _syncService.syncAllData();

      if (result['success']) {
        // Reload all data
        await loadAllData();
        await loadAnalytics();
      }

      return result;
    } catch (e) {
      return {'success': false, 'message': 'Sync failed: $e'};
    } finally {
      isSyncing.value = false;
    }
  }

  // Load analytics data
  Future<void> loadAnalytics() async {
    try {
      final analytics = await _syncService.getAnalyticsData();
      analyticsData.assignAll(analytics);
    } catch (e) {
      print('Error loading analytics: $e');
    }
  }

  // Get customer by ID
  Customer? getCustomerById(String customerId) {
    try {
      return customers.firstWhere((c) => c.customerId == customerId);
    } catch (e) {
      return null;
    }
  }

  // Get product by ID
  Product? getProductById(String productId) {
    try {
      return products.firstWhere((p) => p.productId == productId);
    } catch (e) {
      return null;
    }
  }

  // Get shop by ID
  Shop? getShopById(String shopId) {
    try {
      return shops.firstWhere((s) => s.shopId == shopId);
    } catch (e) {
      return null;
    }
  }

  // Get transactions by customer ID
  List<Transaction> getTransactionsByCustomerId(String customerId) {
    return transactions.where((t) => t.customerId == customerId).toList();
  }

  // Get transactions by product ID
  List<Transaction> getTransactionsByProductId(String productId) {
    return transactions.where((t) => t.productId == productId).toList();
  }

  // Get transactions by shop ID
  List<Transaction> getTransactionsByShopId(String shopId) {
    return transactions.where((t) => t.shopId == shopId).toList();
  }

  // Get transactions by date range
  List<Transaction> getTransactionsByDateRange(
    DateTime startDate,
    DateTime endDate,
  ) {
    return transactions
        .where(
          (t) =>
              t.transactionDate.isAfter(startDate) &&
              t.transactionDate.isBefore(endDate),
        )
        .toList();
  }

  // Get top customers by spending
  List<Customer> getTopCustomersBySpending({int limit = 10}) {
    final customerSpending = <String, double>{};

    for (final transaction in transactions) {
      final total = transaction.quantity * transaction.actualPrice;
      customerSpending[transaction.customerId] =
          (customerSpending[transaction.customerId] ?? 0.0) + total;
    }

    final sortedCustomers = customers
        .where((c) => customerSpending.containsKey(c.customerId))
        .toList();

    sortedCustomers.sort(
      (a, b) => (customerSpending[b.customerId] ?? 0.0).compareTo(
        customerSpending[a.customerId] ?? 0.0,
      ),
    );

    return sortedCustomers.take(limit).toList();
  }

  // Get top products by sales
  List<Product> getTopProductsBySales({int limit = 10}) {
    final productSales = <String, int>{};

    for (final transaction in transactions) {
      productSales[transaction.productId] =
          (productSales[transaction.productId] ?? 0) + transaction.quantity;
    }

    final sortedProducts = products
        .where((p) => productSales.containsKey(p.productId))
        .toList();

    sortedProducts.sort(
      (a, b) => (productSales[b.productId] ?? 0).compareTo(
        productSales[a.productId] ?? 0,
      ),
    );

    return sortedProducts.take(limit).toList();
  }

  // Auto-sync configuration
  void enableAutoSync() {
    _syncService.enableAutoSync();
  }

  void disableAutoSync() {
    _syncService.disableAutoSync();
  }

  bool get isAutoSyncEnabled => _syncService.isAutoSyncEnabled;

  // Extract features manually
  Future<Map<String, dynamic>> extractFeatures() async {
    try {
      return await _localDataService.extractFeatures();
    } catch (e) {
      return {'success': false, 'message': 'Feature extraction failed: $e'};
    }
  }

  // Search functionality
  List<Transaction> searchTransactions(String query) {
    if (query.isEmpty) return transactions;

    final lowerQuery = query.toLowerCase();
    return transactions.where((t) {
      final customer = getCustomerById(t.customerId);
      final product = getProductById(t.productId);
      final shop = getShopById(t.shopId);

      return t.transactionId.toLowerCase().contains(lowerQuery) ||
          (customer?.customerName.toLowerCase().contains(lowerQuery) ??
              false) ||
          (product?.productName.toLowerCase().contains(lowerQuery) ?? false) ||
          (shop?.city.toLowerCase().contains(lowerQuery) ?? false);
    }).toList();
  }

  List<Customer> searchCustomers(String query) {
    if (query.isEmpty) return customers;

    final lowerQuery = query.toLowerCase();
    return customers
        .where(
          (c) =>
              c.customerName.toLowerCase().contains(lowerQuery) ||
              c.city.toLowerCase().contains(lowerQuery) ||
              c.preferredCategories.toLowerCase().contains(lowerQuery),
        )
        .toList();
  }

  List<Product> searchProducts(String query) {
    if (query.isEmpty) return products;

    final lowerQuery = query.toLowerCase();
    return products
        .where(
          (p) =>
              p.productName.toLowerCase().contains(lowerQuery) ||
              p.category.toLowerCase().contains(lowerQuery) ||
              p.brand.toLowerCase().contains(lowerQuery),
        )
        .toList();
  }
}
