import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import '../services/location_service.dart';
import 'dart:async';

class LocationMapPage extends StatefulWidget {
  final String itemName;
  final String shopName;
  final String itemCategory;

  const LocationMapPage({
    Key? key,
    required this.itemName,
    required this.shopName,
    required this.itemCategory,
  }) : super(key: key);

  @override
  State<LocationMapPage> createState() => _LocationMapPageState();
}

class _LocationMapPageState extends State<LocationMapPage> {
  final LocationService _locationService = LocationService();
  final MapController _mapController = MapController();
  final TextEditingController _searchController = TextEditingController();

  LatLng? _currentLocation;
  bool _isLoading = true;
  String _errorMessage = '';
  List<Marker> _markers = [];
  List<Map<String, dynamic>> _mockShops = [];
  StreamSubscription<Position>? _locationSubscription;

  @override
  void initState() {
    super.initState();
    _initializeLocation();
  }

  Future<void> _initializeLocation() async {
    try {
      await _locationService.initialize();
      _locationSubscription = _locationService.locationStream.listen(
        (position) {
          final latLng = LatLng(position.latitude, position.longitude);
          setState(() {
            _currentLocation = latLng;
            _isLoading = false;
          });
          if (_markers.isEmpty) {
            _generateMockShops(latLng);
            _updateMarkers();
            _mapController.move(latLng, 15.0);
          }
        },
        onError: (error) {
          setState(() {
            _isLoading = false;
            _errorMessage = error.toString();
          });
        },
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString();
      });
    }
  }

  void _generateMockShops(LatLng location) {
    _mockShops.clear();
    final random = DateTime.now().millisecondsSinceEpoch;
    final numberOfShops = 5 + (random % 4);

    final shopNames = _getShopNamesForCategory(widget.itemCategory);

    for (int i = 0; i < numberOfShops; i++) {
      final latOffset = (random % 20 + i * 10) * 0.0001;
      final lngOffset = (random % 15 + i * 8) * 0.0001;
      final lat = location.latitude + (i % 2 == 0 ? latOffset : -latOffset);
      final lng = location.longitude + (i % 3 == 0 ? lngOffset : -lngOffset);
      final shopLocation = LatLng(lat, lng);

      final distance = _locationService.calculateDistance(
        location,
        shopLocation,
      );

      _mockShops.add({
        'name': i == 0 ? widget.shopName : shopNames[i % shopNames.length],
        'location': shopLocation,
        'distance': distance.toInt(),
        'rating': 3.5 + (random % 15) / 10,
        'category': widget.itemCategory,
        'item': widget.itemName,
      });
    }

    _mockShops.sort(
      (a, b) => (a['distance'] as int).compareTo(b['distance'] as int),
    );
  }

  List<String> _getShopNamesForCategory(String category) {
    final Map<String, List<String>> shopNamesByCategory = {
      'Grocery': [
        'Fresh Mart',
        'Organic Food Store',
        'Daily Needs',
        'Green Grocers',
        'Food Palace',
      ],
      'Electronics': [
        'Tech Hub',
        'Digital World',
        'Gadget Galaxy',
        'ElectroMart',
        'Power Zone',
      ],
      'Fashion': [
        'Fashion Point',
        'Style Studio',
        'Trendy Wear',
        'Elegance',
        'Fashion Hub',
      ],
      'Vegetables': [
        'Fresh Veggies',
        'Green Garden',
        'Organic Farms',
        'Vegetable Market',
        'Nature\'s Basket',
      ],
      'Fruits': [
        'Fruit Paradise',
        'Juicy Fruits',
        'Fresh Orchard',
        'Fruit Market',
        'Sweet Harvest',
      ],
      'Bakery': [
        'Bread House',
        'Sweet Delights',
        'Cake Factory',
        'Fresh Bakes',
        'Pastry Paradise',
      ],
    };

    return shopNamesByCategory[category] ??
        ['Local Shop', 'Mini Mart', 'Super Store', 'Quick Shop', 'City Store'];
  }

  void _updateMarkers() {
    _markers.clear();

    if (_currentLocation != null) {
      _markers.add(_buildCurrentLocationMarker(_currentLocation!));
    }

    _markers.addAll(_mockShops.map((shop) => _buildShopMarker(shop)));

    setState(() {});
  }

  Marker _buildCurrentLocationMarker(LatLng position) {
    return Marker(
      point: position,
      width: 80,
      height: 80,
      builder: (context) => Column(
        children: [
          Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: Colors.blue,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
            ),
            child: const Icon(
              Icons.person_pin_circle,
              color: Colors.white,
              size: 24,
            ),
          ),
          const Text('You', style: TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Marker _buildShopMarker(Map<String, dynamic> shop) {
    return Marker(
      point: shop['location'] as LatLng,
      width: 110,
      height: 60,
      builder: (context) => GestureDetector(
        onTap: () => _showShopDetails(shop),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: const Color(0xFF4F46E5),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 2),
                boxShadow: const [
                  BoxShadow(
                    color: Colors.black26,
                    blurRadius: 4,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(
                Icons.storefront,
                color: Colors.white,
                size: 20,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(4),
                boxShadow: const [
                  BoxShadow(
                    color: Colors.black12,
                    blurRadius: 3,
                    offset: Offset(0, 1),
                  ),
                ],
              ),
              child: Text(
                shop['name'] as String,
                style: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showShopDetails(Map<String, dynamic> shop) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _ShopDetailsSheet(
        shop: shop,
        itemName: widget.itemName,
        itemCategory: widget.itemCategory,
        onGetDirections: () {
          Navigator.pop(context);
          _showDirectionsDialog(shop);
        },
      ),
    );
  }

  void _showDirectionsDialog(Map<String, dynamic> shop) {
    final distance = shop['distance'] as int;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Get Directions'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Directions to ${shop['name']}'),
            const SizedBox(height: 10),
            Text(
              'Distance: ${_locationService.formatDistance(distance.toDouble())}',
            ),
            const SizedBox(height: 10),
            Text('Estimated time: ${(distance / 80).ceil()} minutes walking'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          "Nearby Shops for ${widget.itemName}",
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
        ),
        backgroundColor: const Color(0xFF4F46E5),
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _initializeLocation,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF4F46E5)),
      );
    }

    if (_errorMessage.isNotEmpty) {
      return _buildErrorView();
    }

    return Stack(
      children: [
        _buildMap(),
        _buildSearchBar(),
        _buildMyLocationButton(),
        _buildShopListButton(),
      ],
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.red),
          const SizedBox(height: 16),
          Text(
            _errorMessage,
            style: const TextStyle(fontSize: 16),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _initializeLocation,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF4F46E5),
              foregroundColor: Colors.white,
            ),
            child: const Text('Try Again'),
          ),
        ],
      ),
    );
  }

  Widget _buildMap() {
    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        center: _currentLocation ?? const LatLng(27.7172, 85.3240),
        zoom: 15.0,
        minZoom: 5.0,
        maxZoom: 18.0,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.example.meropasalapp',
        ),
        MarkerLayer(markers: _markers),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Positioned(
      top: 16,
      left: 16,
      right: 16,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            const Icon(Icons.search, color: Colors.grey),
            const SizedBox(width: 8),
            Expanded(
              child: GestureDetector(
                onTap: _showLocationSearchDialog,
                child: const AbsorbPointer(
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Search for a location...',
                      border: InputBorder.none,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMyLocationButton() {
    return Positioned(
      bottom: 16,
      right: 16,
      child: FloatingActionButton(
        onPressed: _initializeLocation,
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF4F46E5),
        child: const Icon(Icons.my_location),
      ),
    );
  }

  Widget _buildShopListButton() {
    return Positioned(
      bottom: 16,
      left: 16,
      child: FloatingActionButton.extended(
        onPressed: _showShopListModal,
        backgroundColor: const Color(0xFF4F46E5),
        foregroundColor: Colors.white,
        icon: const Icon(Icons.storefront),
        label: Text('${_mockShops.length} Shops Nearby'),
      ),
    );
  }

  void _showLocationSearchDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Search Location'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Enter location name',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              if (_searchController.text.isNotEmpty) {
                // For demo, use default location
                const defaultLocation = LatLng(27.7172, 85.3240);
                setState(() {
                  _currentLocation = defaultLocation;
                  _mapController.move(defaultLocation, 15.0);
                  _generateMockShops(defaultLocation);
                  _updateMarkers();
                });

                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Showing results near ${_searchController.text}',
                    ),
                    behavior: SnackBarBehavior.floating,
                  ),
                );

                _searchController.clear();
              }
            },
            child: const Text('Search'),
          ),
        ],
      ),
    );
  }

  void _showShopListModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _ShopListSheet(
        shops: _mockShops,
        itemName: widget.itemName,
        onShopSelected: (shop) {
          Navigator.pop(context);
          _mapController.move(shop['location'] as LatLng, 16.0);
          Future.delayed(const Duration(milliseconds: 300), () {
            _showShopDetails(shop);
          });
        },
      ),
    );
  }

  @override
  void dispose() {
    _locationSubscription?.cancel();
    _mapController.dispose();
    _searchController.dispose();
    super.dispose();
  }
}

class _ShopDetailsSheet extends StatelessWidget {
  final Map<String, dynamic> shop;
  final String itemName;
  final String itemCategory;
  final VoidCallback onGetDirections;

  const _ShopDetailsSheet({
    required this.shop,
    required this.itemName,
    required this.itemCategory,
    required this.onGetDirections,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.6,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [_buildHeader(context), _buildContent(context)],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        color: Color(0xFF4F46E5),
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Row(
        children: [
          const CircleAvatar(
            backgroundColor: Colors.white,
            radius: 24,
            child: Icon(Icons.storefront, color: Color(0xFF4F46E5), size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  shop['name'] as String,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.star, color: Colors.amber, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '${(shop['rating'] as double).toStringAsFixed(1)}',
                      style: const TextStyle(color: Colors.white),
                    ),
                    const SizedBox(width: 12),
                    const Icon(
                      Icons.location_on,
                      color: Colors.white70,
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${shop['distance']} m',
                      style: const TextStyle(color: Colors.white70),
                    ),
                  ],
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.directions, color: Colors.white),
            onPressed: onGetDirections,
          ),
        ],
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Available Item',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildItemCard(),
          const SizedBox(height: 20),
          const Text(
            'Shop Information',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildInfoRow(Icons.access_time, 'Open Now • 9:00 AM - 8:00 PM'),
          const SizedBox(height: 8),
          _buildInfoRow(
            Icons.phone,
            '+977 98${1000000 + (shop['distance'] as int) % 9000000}',
          ),
          const SizedBox(height: 8),
          _buildInfoRow(Icons.shopping_bag, 'Sells $itemCategory items'),
          const SizedBox(height: 24),
          _buildOrderButton(context),
        ],
      ),
    );
  }

  Widget _buildItemCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: Colors.grey.shade200,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.shopping_basket,
              color: Color(0xFF4F46E5),
              size: 30,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  itemName,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Category: $itemCategory',
                  style: TextStyle(color: Colors.grey.shade700, fontSize: 14),
                ),
                const SizedBox(height: 4),
                const Text(
                  'In Stock',
                  style: TextStyle(
                    color: Colors.green,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          Text(
            'Rs. ${50 + (shop['distance'] as int) % 200}',
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: Color(0xFF4F46E5),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Colors.grey.shade700),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: TextStyle(color: Colors.grey.shade800, fontSize: 14),
          ),
        ),
      ],
    );
  }

  Widget _buildOrderButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Order placed for $itemName at ${shop['name']}'),
              behavior: SnackBarBehavior.floating,
              backgroundColor: const Color(0xFF10B981),
            ),
          );
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF4F46E5),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: const Text(
          'Place Order',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}

class _ShopListSheet extends StatelessWidget {
  final List<Map<String, dynamic>> shops;
  final String itemName;
  final Function(Map<String, dynamic>) onShopSelected;

  const _ShopListSheet({
    required this.shops,
    required this.itemName,
    required this.onShopSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(context),
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.zero,
              itemCount: shops.length,
              itemBuilder: (context, index) =>
                  _buildShopItem(context, shops[index]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Color(0xFF4F46E5),
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Row(
        children: [
          const Icon(Icons.storefront, color: Colors.white),
          const SizedBox(width: 12),
          Text(
            'Shops Selling $itemName',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.close, color: Colors.white),
            onPressed: () => Navigator.pop(context),
          ),
        ],
      ),
    );
  }

  Widget _buildShopItem(BuildContext context, Map<String, dynamic> shop) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: const Color(0xFFE0E7FF),
        child: Icon(Icons.storefront, color: const Color(0xFF4F46E5)),
      ),
      title: Text(
        shop['name'] as String,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      subtitle: Row(
        children: [
          const Icon(Icons.star, size: 16, color: Colors.amber),
          const SizedBox(width: 4),
          Text('${(shop['rating'] as double).toStringAsFixed(1)}'),
          const SizedBox(width: 16),
          const Icon(Icons.location_on, size: 16, color: Colors.grey),
          const SizedBox(width: 4),
          Text('${shop['distance']} m'),
        ],
      ),
      trailing: ElevatedButton(
        onPressed: () {
          Navigator.pop(context);
          onShopSelected(shop);
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF4F46E5),
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        child: const Text('View'),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      onTap: () => onShopSelected(shop),
    );
  }
}
