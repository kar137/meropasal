import '../services/customer_service.dart';

// Example usage of CustomerService for exporting data to ML backend
class CustomerExportExample {
  static Future<void> generateAndExportSampleCustomers() async {
    // Create sample customer data
    List<Customer> sampleCustomers = [
      Customer(
        id: 'C001',
        name: 'Priya Sharma',
        gender: 'Female',
        age: 28,
        city: 'Kathmandu',
        preferredCategories: ['Groceries', 'Electronics'],
        avgMonthlySpending: 15000.0,
        visitsPerMonth: 12.5,
      ),
      Customer(
        id: 'C002',
        name: 'Rajesh Thapa',
        gender: 'Male',
        age: 35,
        city: 'Pokhara',
        preferredCategories: ['Groceries', 'Clothing'],
        avgMonthlySpending: 8500.0,
        visitsPerMonth: 8.2,
      ),
      Customer(
        id: 'C003',
        name: 'Sunita Rai',
        gender: 'Female',
        age: 42,
        city: 'Biratnagar',
        preferredCategories: ['Food & Beverage', 'Health & Beauty'],
        avgMonthlySpending: 12300.0,
        visitsPerMonth: 15.8,
      ),
      Customer(
        id: 'C004',
        name: 'Bikash Gurung',
        gender: 'Male',
        age: 24,
        city: 'Kathmandu',
        preferredCategories: ['Electronics', 'Sports'],
        avgMonthlySpending: 22000.0,
        visitsPerMonth: 6.5,
      ),
      Customer(
        id: 'C005',
        name: 'Maya Magar',
        gender: 'Female',
        age: 31,
        city: 'Lalitpur',
        preferredCategories: ['Books', 'Home & Garden'],
        avgMonthlySpending: 9800.0,
        visitsPerMonth: 10.3,
      ),
    ];

    // Export to ML backend
    bool success = await CustomerService.writeCustomersCsvToMLBackend(sampleCustomers);
    
    if (success) {
      print('✅ Successfully exported ${sampleCustomers.length} customers to ML backend');
      print('📁 File location: ml_backend/data/customers.csv');
      print('🤖 Ready for ML model training!');
    } else {
      print('❌ Failed to export customers to ML backend');
    }
  }

  // Method to export customers from your app's actual data
  static Future<void> exportActualCustomers(List<Customer> actualCustomers) async {
    print('📤 Exporting ${actualCustomers.length} customers to ML backend...');
    
    bool success = await CustomerService.writeCustomersCsvToMLBackend(actualCustomers);
    
    if (success) {
      print('✅ Customer data exported successfully!');
      print('📊 ML backend can now use this data for training');
    } else {
      print('❌ Export failed. Please check file permissions and path.');
    }
  }
}

// How to use in your main app:
/*
void main() async {
  // For testing with sample data:
  await CustomerExportExample.generateAndExportSampleCustomers();
  
  // For real app usage:
  // List<Customer> myAppCustomers = getCustomersFromDatabase();
  // await CustomerExportExample.exportActualCustomers(myAppCustomers);                                                                                                       
}
*/
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   