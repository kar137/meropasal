import 'package:flutter/material.dart';
import '../services/customer_service.dart';

class ShopDashboard extends StatefulWidget {
  @override
  _ShopDashboardState createState() => _ShopDashboardState();
}

class _ShopDashboardState extends State<ShopDashboard> {
  List<Customer> customers = [];

  // Load more comprehensive sample data
  void _loadSampleCustomers() {
    customers = [
      Customer(
        id: '1',
        name: 'Customer 1',
        gender: 'Male',
        age: 29,
        city: 'Pokhara',
        preferredCategories: ['Snacks', 'Personal Care'],
        avgMonthlySpending: 1406.82,
        visitsPerMonth: 12.0,
      ),
      Customer(
        id: '2',
        name: 'Customer 2',
        gender: 'Female',
        age: 32,
        city: 'Bhaktapur',
        preferredCategories: ['Household', 'Personal Care'],
        avgMonthlySpending: 4250.83,
        visitsPerMonth: 3.0,
      ),
      Customer(
        id: '3',
        name: 'Customer 3',
        gender: 'Male',
        age: 53,
        city: 'Biratnagar',
        preferredCategories: ['Beverage'],
        avgMonthlySpending: 4588.2,
        visitsPerMonth: 12.0,
      ),
      Customer(
        id: '4',
        name: 'Customer 4',
        gender: 'Other',
        age: 31,
        city: 'Lalitpur',
        preferredCategories: ['Beverage'],
        avgMonthlySpending: 1007.41,
        visitsPerMonth: 11.0,
      ),
      Customer(
        id: '5',
        name: 'Customer 5',
        gender: 'Other',
        age: 22,
        city: 'Kathmandu',
        preferredCategories: ['Snacks'],
        avgMonthlySpending: 1150.9,
        visitsPerMonth: 7.0,
      ),
      // Add more customers to match your existing data...
    ];
  }

  Future<void> _exportCustomersToML() async {
    if (customers.isEmpty) {
      _loadSampleCustomers();
    }

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 20),
            Expanded(
              child: Text('Writing customer CSV to ML backend...'),
            ),
          ],
        ),
      ),
    );

    // Write CSV directly to ML backend folder
    final success = await CustomerService.writeCustomersCsvToMLBackend(customers);
    
    Navigator.pop(context); // Close loading dialog
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(success ? 'Success' : 'Error'),
        content: Text(success 
          ? 'Customer CSV written successfully to ML backend!\nFile: ml_backend/data/customers.csv\nCustomers: ${customers.length}'
          : 'Failed to write customer CSV. Please check file permissions.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Shop Dashboard'),
        actions: [
          IconButton(
            icon: Icon(Icons.file_download),
            onPressed: _exportCustomersToML,
            tooltip: 'Export Customers CSV to ML Backend',
          ),
        ],
      ),
      body: Column(
        children: [
          // ML Integration Card
          Card(
            margin: EdgeInsets.all(16),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ML Backend Integration',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  SizedBox(height: 10),
                  Text('Export customer data to train ML models'),
                  SizedBox(height: 10),
                  Row(
                    children: [
                      ElevatedButton.icon(
                        onPressed: _exportCustomersToML,
                        icon: Icon(Icons.file_download),
                        label: Text('Export CSV to ML Backend'),
                      ),
                      SizedBox(width: 10),
                      Text('${customers.length} customers ready'),
                    ],
                  ),
                  SizedBox(height: 5),
                  Text(
                    'Target: ml_backend/data/customers.csv',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
          ),
          
          // Your existing dashboard content...
        ],
      ),
    );
  }
}