class Transaction {
  final String transactionId;
  final String customerId;
  final String productId;
  final String shopId;
  final int quantity;
  final double actualPrice;
  final DateTime transactionDate;
  final String paymentMethod;

  Transaction({
    required this.transactionId,
    required this.customerId,
    required this.productId,
    required this.shopId,
    required this.quantity,
    required this.actualPrice,
    required this.transactionDate,
    required this.paymentMethod,
  });

  Map<String, dynamic> toJson() {
    return {
      'transaction_id': transactionId,
      'customer_id': customerId,
      'product_id': productId,
      'shop_id': shopId,
      'quantity': quantity,
      'actual_price': actualPrice,
      'transaction_date': transactionDate.toIso8601String(),
      'payment_method': paymentMethod,
    };
  }

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      transactionId: json['transaction_id'] ?? '',
      customerId: json['customer_id'] ?? '',
      productId: json['product_id'] ?? '',
      shopId: json['shop_id'] ?? '',
      quantity: json['quantity'] ?? 0,
      actualPrice: json['actual_price']?.toDouble() ?? 0.0,
      transactionDate: DateTime.parse(json['transaction_date']),
      paymentMethod: json['payment_method'] ?? '',
    );
  }

  String toCsvRow() {
    return '${transactionId},${customerId},${productId},${shopId},${quantity},${actualPrice},${transactionDate.toIso8601String()},${paymentMethod}';
  }

  static String getCsvHeader() {
    return 'transaction_id,customer_id,product_id,shop_id,quantity,actual_price,transaction_date,payment_method';
  }
}
