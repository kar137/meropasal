class Customer {
  final String customerId;
  final String customerName;
  final String gender;
  final int age;
  final String city;
  final String preferredCategories;
  final double avgMonthlySpending;
  final int visitsPerMonth;

  Customer({
    required this.customerId,
    required this.customerName,
    required this.gender,
    required this.age,
    required this.city,
    required this.preferredCategories,
    required this.avgMonthlySpending,
    required this.visitsPerMonth,
  });

  Map<String, dynamic> toJson() {
    return {
      'customer_id': customerId,
      'customer_name': customerName,
      'gender': gender,
      'age': age,
      'city': city,
      'preferred_categories': preferredCategories,
      'avg_monthly_spending': avgMonthlySpending,
      'visits_per_month': visitsPerMonth,
    };
  }

  factory Customer.fromJson(Map<String, dynamic> json) {
    return Customer(
      customerId: json['customer_id'] ?? '',
      customerName: json['customer_name'] ?? '',
      gender: json['gender'] ?? '',
      age: json['age'] ?? 0,
      city: json['city'] ?? '',
      preferredCategories: json['preferred_categories'] ?? '',
      avgMonthlySpending: json['avg_monthly_spending']?.toDouble() ?? 0.0,
      visitsPerMonth: json['visits_per_month'] ?? 0,
    );
  }

  String toCsvRow() {
    return '${customerId},${customerName},${gender},${age},${city},"${preferredCategories}",${avgMonthlySpending},${visitsPerMonth}';
  }

  static String getCsvHeader() {
    return 'customer_id,customer_name,gender,age,city,preferred_categories,avg_monthly_spending,visits_per_month';
  }
}
