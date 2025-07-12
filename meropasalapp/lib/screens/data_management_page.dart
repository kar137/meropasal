import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:meropasalapp/utils/app_colors.dart';
import '../controllers/transaction_controller.dart';
import '../services/data_initialization_service.dart';

class DataManagementPage extends StatefulWidget {
  const DataManagementPage({Key? key}) : super(key: key);

  @override
  State<DataManagementPage> createState() => _DataManagementPageState();
}

class _DataManagementPageState extends State<DataManagementPage> {
  final TransactionController _controller = Get.find<TransactionController>();
  final DataInitializationService _initService = DataInitializationService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Data Management'),
        backgroundColor: AppColors.MainColor,
        foregroundColor: Colors.white,
      ),
      body: Obx(
        () => SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Data Status Card
              _buildDataStatusCard(),
              const SizedBox(height: 16),

              // Quick Actions
              _buildQuickActionsCard(),
              const SizedBox(height: 16),

              // Analytics Card
              _buildAnalyticsCard(),
              const SizedBox(height: 16),

              // Data Management Actions
              _buildDataManagementCard(),
              const SizedBox(height: 16),

              // Transaction Form
              _buildAddTransactionCard(),
              const SizedBox(height: 16),

              // Recent Transactions
              _buildRecentTransactionsCard(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDataStatusCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.dashboard, color: AppColors.MainColor),
                const SizedBox(width: 8),
                const Text(
                  'Data Status',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatusItem(
                    'Customers',
                    _controller.customers.length.toString(),
                    Icons.people,
                    Colors.green,
                  ),
                ),
                Expanded(
                  child: _buildStatusItem(
                    'Products',
                    _controller.products.length.toString(),
                    Icons.inventory,
                    Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildStatusItem(
                    'Shops',
                    _controller.shops.length.toString(),
                    Icons.store,
                    Colors.purple,
                  ),
                ),
                Expanded(
                  child: _buildStatusItem(
                    'Transactions',
                    _controller.transactions.length.toString(),
                    Icons.receipt,
                    Colors.blue,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.symmetric(horizontal: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        ],
      ),
    );
  }

  Widget _buildQuickActionsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.flash_on, color: Colors.amber[600]),
                const SizedBox(width: 8),
                const Text(
                  'Quick Actions',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _controller.isSyncing.value ? null : _syncData,
                    icon: _controller.isSyncing.value
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.sync),
                    label: const Text('Sync with ML'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.MainColor,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _extractFeatures,
                    icon: const Icon(Icons.analytics),
                    label: const Text('Extract Features'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green[600],
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.analytics, color: Colors.green[600]),
                const SizedBox(width: 8),
                const Text(
                  'Analytics Overview',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (_controller.analyticsData.isNotEmpty)
              Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: _buildAnalyticsItem(
                          'Total Revenue',
                          'Rs. ${_controller.analyticsData['total_revenue']?.toStringAsFixed(2) ?? '0.00'}',
                          Icons.monetization_on,
                          Colors.green,
                        ),
                      ),
                      Expanded(
                        child: _buildAnalyticsItem(
                          'Avg Transaction',
                          'Rs. ${_controller.analyticsData['avg_transaction_value']?.toStringAsFixed(2) ?? '0.00'}',
                          Icons.receipt_long,
                          Colors.blue,
                        ),
                      ),
                    ],
                  ),
                ],
              )
            else
              const Text(
                'Loading analytics data...',
                style: TextStyle(color: Colors.grey),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.symmetric(horizontal: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildDataManagementCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.settings, color: Colors.grey[600]),
                const SizedBox(width: 8),
                const Text(
                  'Data Management',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.refresh),
                  title: const Text('Initialize Data'),
                  subtitle: const Text('Load existing CSV data'),
                  onTap: _initializeData,
                ),
                ListTile(
                  leading: Icon(
                    _controller.isAutoSyncEnabled
                        ? Icons.sync
                        : Icons.sync_disabled,
                    color: _controller.isAutoSyncEnabled
                        ? Colors.green
                        : Colors.grey,
                  ),
                  title: Text(
                    _controller.isAutoSyncEnabled
                        ? 'Auto-sync Enabled'
                        : 'Auto-sync Disabled',
                  ),
                  subtitle: const Text('Toggle automatic synchronization'),
                  onTap: _toggleAutoSync,
                ),
                ListTile(
                  leading: const Icon(Icons.copy),
                  title: const Text('Copy to ML Backend'),
                  subtitle: const Text('Copy data files to ML backend'),
                  onTap: _copyToMLBackend,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAddTransactionCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.add_shopping_cart, color: Colors.blue[600]),
                const SizedBox(width: 8),
                const Text(
                  'Add New Transaction',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: () => _showAddTransactionDialog(),
              icon: const Icon(Icons.add),
              label: const Text('Add Transaction'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.MainColor,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 40),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentTransactionsCard() {
    final recentTransactions = _controller.transactions.take(5).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.history, color: Colors.grey[600]),
                const SizedBox(width: 8),
                const Text(
                  'Recent Transactions',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (recentTransactions.isEmpty)
              const Text(
                'No transactions yet',
                style: TextStyle(color: Colors.grey),
              )
            else
              Column(
                children: recentTransactions.map((transaction) {
                  final customer = _controller.getCustomerById(
                    transaction.customerId,
                  );
                  final product = _controller.getProductById(
                    transaction.productId,
                  );

                  return ListTile(
                    leading: CircleAvatar(
                      backgroundColor: Colors.blue[100],
                      child: Text(
                        transaction.quantity.toString(),
                        style: TextStyle(color: Colors.blue[600]),
                      ),
                    ),
                    title: Text(product?.productName ?? 'Unknown Product'),
                    subtitle: Text(
                      '${customer?.customerName ?? 'Unknown Customer'} • Rs. ${transaction.actualPrice.toStringAsFixed(2)}',
                    ),
                    trailing: Text(
                      '${transaction.transactionDate.day}/${transaction.transactionDate.month}',
                      style: const TextStyle(fontSize: 12),
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  // Action methods
  Future<void> _syncData() async {
    final result = await _controller.syncWithMLBackend();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result['message'] ?? 'Sync completed'),
        backgroundColor: result['success'] ? Colors.green : Colors.red,
      ),
    );
  }

  Future<void> _extractFeatures() async {
    final result = await _controller.extractFeatures();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result['message'] ?? 'Feature extraction completed'),
        backgroundColor: result['success'] ? Colors.green : Colors.red,
      ),
    );
  }

  Future<void> _initializeData() async {
    final result = await _initService.initializeWithExistingData();

    if (result['success']) {
      await _controller.loadAllData();
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result['message'] ?? 'Data initialization completed'),
        backgroundColor: result['success'] ? Colors.green : Colors.red,
      ),
    );
  }

  void _toggleAutoSync() {
    if (_controller.isAutoSyncEnabled) {
      _controller.disableAutoSync();
    } else {
      _controller.enableAutoSync();
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _controller.isAutoSyncEnabled
              ? 'Auto-sync enabled'
              : 'Auto-sync disabled',
        ),
      ),
    );
  }

  Future<void> _copyToMLBackend() async {
    final result = await _initService.copyDataToMLBackend();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result['message'] ?? 'Copy completed'),
        backgroundColor: result['success'] ? Colors.green : Colors.red,
      ),
    );
  }

  void _showAddTransactionDialog() {
    if (_controller.customers.isEmpty ||
        _controller.products.isEmpty ||
        _controller.shops.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please initialize data first'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    String? selectedCustomerId;
    String? selectedProductId;
    String? selectedShopId;
    int quantity = 1;
    double actualPrice = 0.0;
    String paymentMethod = 'Cash';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Add New Transaction'),
          content: SizedBox(
            width: double.maxFinite,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'Customer'),
                  value: selectedCustomerId,
                  items: _controller.customers.map((customer) {
                    return DropdownMenuItem<String>(
                      value: customer.customerId,
                      child: Text(customer.customerName),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      selectedCustomerId = value;
                    });
                  },
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'Product'),
                  value: selectedProductId,
                  items: _controller.products.map((product) {
                    return DropdownMenuItem<String>(
                      value: product.productId,
                      child: Text(
                        '${product.productName} - Rs. ${product.standardPrice}',
                      ),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      selectedProductId = value;
                      final product = _controller.getProductById(value!);
                      if (product != null) {
                        actualPrice = product.standardPrice;
                      }
                    });
                  },
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'Shop'),
                  value: selectedShopId,
                  items: _controller.shops.map((shop) {
                    return DropdownMenuItem<String>(
                      value: shop.shopId,
                      child: Text('${shop.city} - ${shop.district}'),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      selectedShopId = value;
                    });
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  decoration: const InputDecoration(labelText: 'Quantity'),
                  keyboardType: TextInputType.number,
                  initialValue: quantity.toString(),
                  onChanged: (value) {
                    quantity = int.tryParse(value) ?? 1;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  decoration: const InputDecoration(labelText: 'Actual Price'),
                  keyboardType: TextInputType.number,
                  initialValue: actualPrice.toString(),
                  onChanged: (value) {
                    actualPrice = double.tryParse(value) ?? 0.0;
                  },
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(
                    labelText: 'Payment Method',
                  ),
                  value: paymentMethod,
                  items: ['Cash', 'Card', 'Digital'].map((method) {
                    return DropdownMenuItem<String>(
                      value: method,
                      child: Text(method),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      paymentMethod = value ?? 'Cash';
                    });
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (selectedCustomerId != null &&
                    selectedProductId != null &&
                    selectedShopId != null) {
                  final result = await _controller.addTransaction(
                    customerId: selectedCustomerId!,
                    productId: selectedProductId!,
                    shopId: selectedShopId!,
                    quantity: quantity,
                    actualPrice: actualPrice,
                    paymentMethod: paymentMethod,
                  );

                  Navigator.of(context).pop();

                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(result['message'] ?? 'Transaction added'),
                      backgroundColor: result['success']
                          ? Colors.green
                          : Colors.red,
                    ),
                  );
                }
              },
              child: const Text('Add Transaction'),
            ),
          ],
        ),
      ),
    );
  }
}
