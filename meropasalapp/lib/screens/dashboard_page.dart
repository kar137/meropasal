import 'package:flutter/material.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:universal_html/html.dart' as html; // Only for web
import 'dart:convert';
import '../shop.dart';

// CSV EXPORT FUNCTION
Future<void> exportSalesToCsv(
  BuildContext context,
  List<SaleRecord> sales,
) async {
  final buffer = StringBuffer();
  buffer.writeln(
    'shop_id,product_id,transaction_type,quantity,unit_price,total_amount,transaction_time,payment_method',
  );
  for (var sale in sales) {
    buffer.writeln(
      '${sale.shopId},${sale.productId},${sale.transactionType},${sale.quantity},${sale.unitPrice},${sale.totalAmount},${sale.transactionTime.toIso8601String()},${sale.paymentMethod}',
    );
  }
  final csv = buffer.toString();

  try {
    final bytes = utf8.encode(csv);
    final filename =
        'sales_log_${DateTime.now().millisecondsSinceEpoch}.csv'; // NEW: Unique filename

    if (kIsWeb) {
      // NEW: Web implementation using universal_html
      final blob = html.Blob([bytes], 'text/csv');
      final url = html.Url.createObjectUrlFromBlob(blob);
      final anchor = html.AnchorElement(href: url)
        ..setAttribute('download', filename)
        ..click();
      html.Url.revokeObjectUrl(url);
    } else {
      // Mobile/Desktop implementation
      final directory = await getTemporaryDirectory();
      final path = '${directory.path}/$filename';
      final file = File(path);
      await file.writeAsBytes(bytes); // UPDATED: Using bytes instead of string
      await Share.shareFiles([path], text: 'Sales Log CSV');
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        // FIXED: Typo (SnackBar was misspelled as "SnackBar" in original)
        content: Text('CSV exported successfully!'),
        backgroundColor: Colors.green,
      ),
    );
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Failed to export CSV: ${e.toString()}',
        ), // UPDATED: Better error message
        backgroundColor: Colors.red,
      ),
    );
  }
}

// ...rest of your DashboardPage code remains unchanged...
class DashboardPage extends StatelessWidget {
  final List<Product> products;
  final List<SaleRecord> sales;

  DashboardPage({required this.products, required this.sales});

  @override
  Widget build(BuildContext context) {
    int totalProducts = products.length;
    int totalStock = products.fold(0, (sum, p) => sum + p.quantity);
    double totalValue = products.fold(
      0.0,
      (sum, p) => sum + p.quantity * p.price,
    );

    int salesTodayCount = sales
        .where(
          (s) =>
              s.time.year == DateTime.now().year &&
              s.time.month == DateTime.now().month &&
              s.time.day == DateTime.now().day,
        )
        .fold(0, (sum, s) => sum + s.quantity);

    double salesTodayAmount = sales
        .where(
          (s) =>
              s.time.year == DateTime.now().year &&
              s.time.month == DateTime.now().month &&
              s.time.day == DateTime.now().day,
        )
        .fold(0.0, (sum, s) => sum + s.totalAmount);

    int totalSalesCount = sales.fold(0, (sum, s) => sum + s.quantity);
    double totalSalesAmount = sales.fold(0.0, (sum, s) => sum + s.totalAmount);

    Map<String, int> salesPerProduct = {
      for (var p in products)
        p.name: sales
            .where((s) => s.productName == p.name)
            .fold(0, (sum, s) => sum + s.quantity),
    };

    Map<String, int> salesTodayPerProduct = {
      for (var p in products)
        p.name: sales
            .where(
              (s) =>
                  s.productName == p.name &&
                  s.time.year == DateTime.now().year &&
                  s.time.month == DateTime.now().month &&
                  s.time.day == DateTime.now().day,
            )
            .fold(0, (sum, s) => sum + s.quantity),
    };

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'User Dashboard',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        backgroundColor: Color(0xFF1E88E5),
        elevation: 8,
        actions: [
          IconButton(
            icon: Icon(Icons.download),
            tooltip: "Export Sales CSV",
            onPressed: () => exportSalesToCsv(context, sales),
          ),
        ],
      ),
      backgroundColor: Color(0xFFF3F8FB),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          ElevatedButton.icon(
            icon: Icon(Icons.download),
            label: Text("Export Sales CSV"),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blue),
            onPressed: () => exportSalesToCsv(context, sales),
          ),
          SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _dashboardCard(
                  icon: Icons.inventory_2,
                  label: 'Total Products',
                  value: totalProducts.toString(),
                  color: Colors.blueAccent,
                ),
              ),
              SizedBox(width: 8),
              Expanded(
                child: _dashboardCard(
                  icon: Icons.storage,
                  label: 'Total Stock',
                  value: totalStock.toString(),
                  color: Colors.green,
                ),
              ),
              SizedBox(width: 8),
              Expanded(
                child: _dashboardCard(
                  icon: Icons.attach_money,
                  label: 'Stock Value',
                  value: 'रू ${totalValue.toStringAsFixed(0)}',
                  color: Colors.amber[800]!,
                ),
              ),
            ],
          ),
          SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _dashboardCard(
                  icon: Icons.sell,
                  label: 'Sales Today',
                  value: salesTodayCount.toString(),
                  color: Colors.teal,
                ),
              ),
              SizedBox(width: 8),
              Expanded(
                child: _dashboardCard(
                  icon: Icons.currency_rupee,
                  label: 'Revenue Today',
                  value: 'रू ${salesTodayAmount.toStringAsFixed(0)}',
                  color: Colors.deepOrange,
                ),
              ),
            ],
          ),
          SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _dashboardCard(
                  icon: Icons.leaderboard,
                  label: 'Total Sales',
                  value: totalSalesCount.toString(),
                  color: Colors.purple,
                ),
              ),
              SizedBox(width: 8),
              Expanded(
                child: _dashboardCard(
                  icon: Icons.account_balance_wallet,
                  label: 'Total Revenue',
                  value: 'रू ${totalSalesAmount.toStringAsFixed(0)}',
                  color: Colors.indigo,
                ),
              ),
            ],
          ),
          SizedBox(height: 24),
          _buildProductSalesTable(
            products,
            salesPerProduct,
            salesTodayPerProduct,
          ),
          SizedBox(height: 24),
          _buildSalesLog(sales),
        ],
      ),
    );
  }

  Widget _dashboardCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(.07),
            blurRadius: 10,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
          SizedBox(height: 10),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: color,
            ),
          ),
          SizedBox(height: 4),
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[700])),
        ],
      ),
    );
  }

  Widget _buildProductSalesTable(
    List<Product> products,
    Map<String, int> perProduct,
    Map<String, int> todayPerProduct,
  ) {
    return Card(
      elevation: 5,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🛒 Product Sales (All Time / Today)',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            SizedBox(height: 8),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: [
                  DataColumn(
                    label: Text(
                      'Product',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  DataColumn(label: Text('Total Sold')),
                  DataColumn(label: Text('Sold Today')),
                ],
                rows: products.map((p) {
                  return DataRow(
                    cells: [
                      DataCell(Text(p.name)),
                      DataCell(Text(perProduct[p.name]?.toString() ?? '0')),
                      DataCell(
                        Text(todayPerProduct[p.name]?.toString() ?? '0'),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSalesLog(List<SaleRecord> sales) {
    final sortedSales = sales.reversed.toList();
    return Card(
      elevation: 5,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '📋 Sales Log',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            SizedBox(height: 8),
            sortedSales.isNotEmpty
                ? Column(
                    children: sortedSales.take(20).map((sale) {
                      return ListTile(
                        dense: true,
                        leading: Icon(
                          sale.type == 'sell'
                              ? Icons.sell
                              : Icons.add_shopping_cart,
                          color: sale.type == 'sell'
                              ? Colors.orangeAccent
                              : Colors.green,
                        ),
                        title: Text('${sale.productName}'),
                        subtitle: Text(
                          '${sale.type == 'sell' ? "Sold" : "Bought"}: ${sale.quantity} | '
                          '${sale.time.hour.toString().padLeft(2, '0')}:${sale.time.minute.toString().padLeft(2, '0')} on '
                          '${sale.time.year}-${sale.time.month.toString().padLeft(2, '0')}-${sale.time.day.toString().padLeft(2, '0')}',
                        ),
                        trailing: Text(
                          'रू ${sale.totalAmount.toStringAsFixed(0)}',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      );
                    }).toList(),
                  )
                : Text('No sales yet.'),
          ],
        ),
      ),
    );
  }
}
