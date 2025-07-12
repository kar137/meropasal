class Shop {
  final String shopId;
  final String city;
  final String district;

  Shop({required this.shopId, required this.city, required this.district});

  Map<String, dynamic> toJson() {
    return {'shop_id': shopId, 'city': city, 'district': district};
  }

  factory Shop.fromJson(Map<String, dynamic> json) {
    return Shop(
      shopId: json['shop_id'] ?? '',
      city: json['city'] ?? '',
      district: json['district'] ?? '',
    );
  }

  String toCsvRow() {
    return '${shopId},${city},${district}';
  }

  static String getCsvHeader() {
    return 'shop_id,city,district';
  }
}
