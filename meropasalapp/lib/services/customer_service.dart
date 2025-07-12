import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;

class Customer {
  final String id;
  final String name;
  final String gender;
  final int age;
  final String city;
  final List<String> preferredCategories;
  final double avgMonthlySpending;
  final double visitsPerMonth;

  Customer({
    required this.id,
    required this.name,
    required this.gender,
    required this.age,
    required this.city,
    required this.preferredCategories,
    required this.avgMonthlySpending,
    required this.visitsPerMonth,
  });

  Map<String, dynamic> toJson() => {
    'customer_id': id,
    'customer_name': name,
    'gender': gender,
    'age': age,
    'city': city,
    'preferred_categories': preferredCategories.join(', '),
    'avg_monthly_spending': avgMonthlySpending,
    'visits_per_month': visitsPerMonth,
  };                                             
}                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                                                                                                                
class CustomerService {                                        
  // Path to your ML backend data folder                             
  static const String _mlBackendPath = r'c:\Users\Dell\OneDrive\D                          esktop\KaranCodes\Hackathon_projects\meropasal\ml_backend\data';
  // Example method to generate and export sample customers
  static String exportCustomersToCsv(List<Customer> customers, {bool includeHeaders = true}) {
    final headers = includeHeaders ? 'customer_id,customer_name,gender,age,city,preferred_categories,avg_monthly_spending,visits_per_month\n' : '';
    final rows = customers.map((c) =>
      '${c.id},${c.name},${c.gender},${c.age},${c.city},"${c.preferredCategories.join(', ')}",${c.avgMonthlySpending},${c.visitsPerMonth}'
    ).join('\n');
    return headers + rows;
  }
  static Future<bool> writeCustomersCsvToMLBackend(List<Customer> customers) async {
    try {
      // Ensure the ML backend data directory exists
      final dataDir = Directory(_mlBackendPath);
      if (!await dataDir.exists()) {
        await dataDir.create(recursive: true);
      }
      
      final csvFile = File(path.join(_mlBackendPath, 'customers.csv'));
      
      // Check if file exists to determine if we need headers
      bool fileExists = await csvFile.exists();
      bool includeHeaders = !fileExists;
      
      // If file exists, check for duplicate customer IDs to avoid duplicates
      Set<String> existingIds = {};
      if (fileExists) {
        try {
          String existingContent = await csvFile.readAsString();
          List<String> lines = existingContent.split('\n');
          
          // Skip header and empty lines, extract customer IDs
          for (int i = 1; i < lines.length; i++) {
            if (lines[i].trim().isNotEmpty) {
              List<String> parts = lines[i].split(',');
              if (parts.isNotEmpty) {
                existingIds.add(parts[0].trim());
              }
            }
          }
        } catch (e) {
          print('Warning: Could not read existing file for duplicate check: $e');
        }
      }
      
      // Filter out customers that already exist
      List<Customer> newCustomers = customers.where((c) => !existingIds.contains(c.id)).toList();
      
      if (newCustomers.isEmpty) {
        print('No new customers to add. All customers already exist in the dataset.');
        return true;
      }
      
      final csvData = exportCustomersToCsv(newCustomers, includeHeaders: includeHeaders);
      
      // Append to file or create new file
      if (fileExists) {
        await csvFile.writeAsString('\n$csvData', mode: FileMode.append);
        print('Appended ${newCustomers.length} new customers to existing dataset');
      } else {
        await csvFile.writeAsString(csvData);
        print('Created new customer dataset with ${newCustomers.length} customers');
      }
      
      print('Customer CSV updated at: ${csvFile.path}');
      print('Total customers in file: ${existingIds.length + newCustomers.length}');
      return true;
      
    } catch (e) {
      print('Error writing customers CSV: $e');
      return false;
    }
  }

  // Method to get current dataset statistics
  static Future<Map<String, dynamic>> getDatasetStats() async {
    try {
      final csvFile = File(path.join(_mlBackendPath, 'customers.csv'));
      
      if (!await csvFile.exists()) {
        return {
          'exists': false,
          'totalCustomers': 0,
          'message': 'No customer dataset found'
        };
      }
      
      String content = await csvFile.readAsString();
      List<String> lines = content.split('\n');
      
      // Count non-empty lines (excluding header)
      int totalCustomers = lines.where((line) => line.trim().isNotEmpty).length - 1;
      
      return {
        'exists': true,
        'totalCustomers': totalCustomers,
        'filePath': csvFile.path,
        'fileSize': '${(await csvFile.length() / 1024).toStringAsFixed(2)} KB'
      };
      
    } catch (e) {
      return {
        'exists': false,
        'error': e.toString()
      };
    }
  }
  
  // Method to clear the dataset (use with caution)
  static Future<bool> clearDataset() async {
    try {
      final csvFile = File(path.join(_mlBackendPath, 'customers.csv'));
      
      if (await csvFile.exists()) {
        await csvFile.delete();
        print('Customer dataset cleared successfully');
        return true;
      } else {
        print('No dataset file found to clear');
        return true;
      }
      
    } catch (e) {
      print('Error clearing dataset: $e');
      return false;
    }
  }

  // Alternative method for HTTP upload (if needed)
  static Future<bool> sendCustomersToBackend(List<Customer> customers) async {
    try {
      final csvData = exportCustomersToCsv(customers);
      
      final response = await http.post(
        Uri.parse('http://localhost:8000/upload_customers/'),
        headers: {'Content-Type': 'text/csv'},
        body: csvData,
      );
      
      return response.statusCode == 200;
    } catch (e) {
      print('Error sending customers to backend: $e');
      return false;
    }
  }
}