class Product {
  final String productId;
  final String productName;
  final String category;
  final String brand;
  final double standardPrice;

  Product({
    required this.productId,
    required this.productName,
    required this.category,
    required this.brand,
    required this.standardPrice,
  });

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'product_name': productName,
      'category': category,
      'brand': brand,
      'standard_price': standardPrice,
    };
  }

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      productId: json['product_id'] ?? '',
      productName: json['product_name'] ?? '',
      category: json['category'] ?? '',
      brand: json['brand'] ?? '',
      standardPrice: json['standard_price']?.toDouble() ?? 0.0,
    );
  }

  String toCsvRow() {
    return '${productId},${productName},${category},${brand},${standardPrice}';
  }

  static String getCsvHeader() {
    return 'product_id,product_name,category,brand,standard_price';
  }
}
