import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';

class LocationExample extends StatefulWidget {
  final String title;
  final bool isSearchResults;

  const LocationExample({
    Key? key,
    this.title = "Location Example",
    this.isSearchResults = false,
  }) : super(key: key);

  @override
  State<LocationExample> createState() => _LocationExampleState();
}

class _LocationExampleState extends State<LocationExample> {
  // Use late initialization for MapController to ensure it's created in initState
  late final MapController _mapController;
  Position? _currentPosition;
  bool _isLoading = true;
  String _currentAddress = "Kalanki Chowk, Kathmandu";
  String _destinationAddress = "Deerwalk Institute, Sifal, KTM";
  String _rideTime = "8 min away";
  double _rideCost = 118.0;
  bool _isSurgePricing = true;

  // For search results
  final List<Map<String, dynamic>> _nearbyShops = [
    {
      'name': 'Fresh Mart',
      'address': 'Maitidevi Temple, Kathmandu',
      'rating': 4.5,
      'distance': '1.2 km',
      'position': LatLng(27.710, 85.335),
    },
    {
      'name': 'Organic Corner',
      'address': 'Guhyeshwari, Kathmandu',
      'rating': 4.2,
      'distance': '1.8 km',
      'position': LatLng(27.718, 85.350),
    },
    {
      'name': 'Daily Needs',
      'address': 'Baluwatar, Kathmandu',
      'rating': 4.7,
      'distance': '2.3 km',
      'position': LatLng(27.729, 85.332),
    },
    {
      'name': 'City Shop',
      'address': 'Basantapur, Kathmandu',
      'rating': 4.1,
      'distance': '3.0 km',
      'position': LatLng(27.705, 85.318),
    },
  ];

  // Sample route points (simulating a route between points)
  final List<LatLng> _routePoints = [
    LatLng(27.710, 85.315), // Starting point
    LatLng(27.711, 85.320),
    LatLng(27.712, 85.325),
    LatLng(27.714, 85.330),
    LatLng(27.715, 85.335),
    LatLng(27.717, 85.338), // Ending point
  ];

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation({bool useRealLocation = false}) async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Location services are disabled. Please enable them in settings.',
            ),
            behavior: SnackBarBehavior.floating,
            backgroundColor: Colors.red,
          ),
        );
        setState(() {
          _isLoading = false;
        });
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Location permissions are denied'),
              behavior: SnackBarBehavior.floating,
              backgroundColor: Colors.red,
            ),
          );
          setState(() {
            _isLoading = false;
          });
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Location permissions are permanently denied. Please enable from settings.',
            ),
            behavior: SnackBarBehavior.floating,
            backgroundColor: Colors.red,
            action: SnackBarAction(
              label: 'SETTINGS',
              onPressed: () => Geolocator.openAppSettings(),
            ),
          ),
        );
        setState(() {
          _isLoading = false;
        });
        return;
      }

      Position position;

      if (useRealLocation) {
        // Get actual device location
        try {
          position = await Geolocator.getCurrentPosition(
            desiredAccuracy: LocationAccuracy.high,
            timeLimit: Duration(seconds: 5),
          );
        } catch (e) {
          print("Error getting real location: $e");
          // Fallback to demo location if real location fails
          position = Position(
            latitude: 27.712,
            longitude: 85.322,
            timestamp: DateTime.now(),
            accuracy: 10,
            altitude: 0,
            heading: 0,
            speed: 0,
            speedAccuracy: 0,
            altitudeAccuracy: 0,
            headingAccuracy: 0,
          );
        }
      } else {
        // For demo purposes, using a fixed location in Kathmandu
        position = Position(
          latitude: 27.712,
          longitude: 85.322,
          timestamp: DateTime.now(),
          accuracy: 10,
          altitude: 0,
          heading: 0,
          speed: 0,
          speedAccuracy: 0,
          altitudeAccuracy: 0,
          headingAccuracy: 0,
        );
      }

      setState(() {
        _currentPosition = position;
        _isLoading = false;
      });
    } catch (e) {
      print("Error getting location: $e");
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to get location: $e'),
          behavior: SnackBarBehavior.floating,
          backgroundColor: Colors.red,
        ),
      );
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final center = _currentPosition != null
        ? LatLng(_currentPosition!.latitude, _currentPosition!.longitude)
        : LatLng(27.712, 85.322); // Default to Kathmandu

    return Scaffold(
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Stack(
              children: [
                // Map
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(center: center, zoom: 15.0),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.example.meropasalapp',
                    ),
                    // Route polyline
                    PolylineLayer(
                      polylines: [
                        Polyline(
                          points: _routePoints,
                          color: Colors.red,
                          strokeWidth: 4.0,
                        ),
                      ],
                    ),
                    // Markers layer
                    MarkerLayer(markers: _buildMarkers()),
                  ],
                ),

                // My Location button
                Positioned(
                  bottom: widget.isSearchResults ? 350 : 300,
                  right: 16,
                  child: FloatingActionButton(
                    backgroundColor: Colors.white,
                    child: Icon(Icons.my_location, color: Colors.black87),
                    onPressed: () {
                      _getCurrentLocation(useRealLocation: true);
                      if (_currentPosition != null) {
                        _mapController.move(
                          LatLng(
                            _currentPosition!.latitude,
                            _currentPosition!.longitude,
                          ),
                          16.0,
                        );
                        setState(() {
                          _currentAddress = "My Current Location";
                        });
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Using your current location'),
                            behavior: SnackBarBehavior.floating,
                          ),
                        );
                      }
                    },
                  ),
                ),

                // Back button and search bar
                Positioned(
                  top: 40,
                  left: 10,
                  right: 10,
                  child: Row(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black12,
                              blurRadius: 4,
                              offset: Offset(0, 2),
                            ),
                          ],
                        ),
                        child: IconButton(
                          icon: Icon(Icons.arrow_back, color: Colors.black),
                          onPressed: () => Navigator.of(context).pop(),
                        ),
                      ),
                      SizedBox(width: 10),
                      Expanded(
                        child: GestureDetector(
                          onTap: _showLocationSearchDialog,
                          child: Container(
                            padding: EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(24),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black12,
                                  blurRadius: 4,
                                  offset: Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.search,
                                  color: Colors.grey,
                                  size: 20,
                                ),
                                SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    _currentAddress,
                                    style: TextStyle(fontSize: 16),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Bottom sheet
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  child: widget.isSearchResults
                      ? _buildSearchResultsBottomSheet()
                      : _buildRideDetailsBottomSheet(),
                ),
              ],
            ),
    );
  }

  List<Marker> _buildMarkers() {
    final markers = <Marker>[];

    // Current position marker
    if (_currentPosition != null) {
      markers.add(
        Marker(
          width: 40,
          height: 40,
          point: LatLng(
            _currentPosition!.latitude,
            _currentPosition!.longitude,
          ),
          builder: (context) => Container(
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.5),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.my_location, color: Colors.blue, size: 30),
          ),
        ),
      );
    }

    // Add shop markers or vehicle markers
    if (widget.isSearchResults) {
      // Shop markers for search results
      for (final shop in _nearbyShops) {
        markers.add(
          Marker(
            width: 50,
            height: 50,
            point: shop['position'],
            builder: (context) => Container(
              child: Icon(Icons.store, color: Colors.red, size: 30),
            ),
          ),
        );
      }
    } else {
      // Bike markers for ride sharing
      for (var i = 0; i < 8; i++) {
        // Random positions for bikes near the route
        final lat = 27.712 + (i * 0.002) * (i % 2 == 0 ? 1 : -1);
        final lng = 85.330 + (i * 0.003) * (i % 2 == 0 ? -1 : 1);

        markers.add(
          Marker(
            width: 35,
            height: 35,
            point: LatLng(lat, lng),
            builder: (context) => Container(
              child: Icon(Icons.motorcycle, color: Colors.red, size: 25),
            ),
          ),
        );
      }
    }

    // Destination marker
    markers.add(
      Marker(
        width: 50,
        height: 50,
        point: _routePoints.last,
        builder: (context) => Container(
          child: Icon(Icons.location_on, color: Colors.red, size: 40),
        ),
      ),
    );

    return markers;
  }

  Widget _buildRideDetailsBottomSheet() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: Offset(0, -5),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Destination info
          Container(
            padding: EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Icon(Icons.access_time, size: 20, color: Colors.grey),
                SizedBox(width: 10),
                Text(
                  "Pickup in 8 min",
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                Spacer(),
                Text(
                  _destinationAddress,
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                Icon(Icons.chevron_right, color: Colors.grey),
              ],
            ),
          ),

          // Info banner
          if (_isSurgePricing)
            Container(
              padding: EdgeInsets.all(10),
              color: Colors.grey.shade100,
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.grey, size: 20),
                  SizedBox(width: 10),
                  Text(
                    "Surge applied for chosen pickup",
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),

          // Divider
          Container(
            height: 5,
            width: 40,
            margin: EdgeInsets.symmetric(vertical: 10),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(10),
            ),
          ),

          // Ride Details
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Ride Details",
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 16),

                // Pickup button
                Container(
                  padding: EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.alarm, color: Colors.red),
                          SizedBox(width: 8),
                          Text("Pickup now"),
                        ],
                      ),
                      Icon(Icons.keyboard_arrow_down),
                    ],
                  ),
                ),

                SizedBox(height: 16),

                // Vehicle option
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.red),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Image.network(
                        'https://cdn-icons-png.flaticon.com/512/2972/2972185.png',
                        width: 50,
                        height: 50,
                      ),
                      SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  "Bike",
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                SizedBox(width: 8),
                                Icon(Icons.person, size: 16),
                                Text(" 1"),
                              ],
                            ),
                            Text(
                              "$_rideTime",
                              style: TextStyle(color: Colors.grey[600]),
                            ),
                            Text(
                              "Quick and affordable ride",
                              style: TextStyle(color: Colors.grey[600]),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        "₹${_rideCost.toStringAsFixed(0)}",
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 16),

                // Payment options
                Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(8),
                            bottomLeft: Radius.circular(8),
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.money, color: Colors.green),
                            SizedBox(width: 8),
                            Text("Cash Payment"),
                          ],
                        ),
                      ),
                    ),
                    Expanded(
                      child: Container(
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.only(
                            topRight: Radius.circular(8),
                            bottomRight: Radius.circular(8),
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.discount, color: Colors.green),
                                SizedBox(width: 8),
                                Text("Discount"),
                              ],
                            ),
                            Icon(Icons.keyboard_arrow_down),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 20),

                // Action button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                    ),
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            "Bike selected! Your ride is on the way.",
                          ),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    },
                    child: Text(
                      "Choose bike",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchResultsBottomSheet() {
    return Container(
      height: MediaQuery.of(context).size.height * 0.5,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: Offset(0, -5),
          ),
        ],
      ),
      child: Column(
        children: [
          // Handle bar
          Container(
            height: 5,
            width: 40,
            margin: EdgeInsets.symmetric(vertical: 10),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(10),
            ),
          ),

          // Title
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  "Nearby Shops",
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    "Filter",
                    style: TextStyle(fontWeight: FontWeight.w500),
                  ),
                ),
              ],
            ),
          ),

          // Shop list
          Expanded(
            child: ListView.builder(
              itemCount: _nearbyShops.length,
              itemBuilder: (context, index) {
                final shop = _nearbyShops[index];
                return _buildShopCard(shop);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShopCard(Map<String, dynamic> shop) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(Icons.store, color: Colors.red, size: 30),
            ),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    shop['name'],
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 4),
                  Text(
                    shop['address'],
                    style: TextStyle(color: Colors.grey[600], fontSize: 14),
                  ),
                  SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.star, color: Colors.amber, size: 16),
                      SizedBox(width: 4),
                      Text(
                        "${shop['rating']}",
                        style: TextStyle(fontWeight: FontWeight.w500),
                      ),
                      SizedBox(width: 12),
                      Icon(Icons.location_on, color: Colors.grey, size: 16),
                      SizedBox(width: 4),
                      Text(
                        shop['distance'],
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                minimumSize: Size(80, 40),
              ),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text("Selected shop: ${shop['name']}"),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              },
              child: Text("Select"),
            ),
          ],
        ),
      ),
    );
  }

  // Method to show location search dialog
  void _showLocationSearchDialog() {
    final TextEditingController searchController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Search Location'),
        content: TextField(
          controller: searchController,
          decoration: InputDecoration(
            hintText: 'Enter a location',
            prefixIcon: Icon(Icons.search),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
          ),
          onSubmitted: (value) {
            if (value.isNotEmpty) {
              _searchLocation(value);
              Navigator.pop(context);
            }
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              if (searchController.text.isNotEmpty) {
                _searchLocation(searchController.text);
                Navigator.pop(context);
              }
            },
            child: Text('Search'),
          ),
        ],
      ),
    );
  }

  // Method to search for location
  void _searchLocation(String query) {
    // In a real app, you would use a geocoding service here
    // For now, we'll simulate finding a location
    setState(() {
      _currentAddress = query;

      // Simulate changing the map position (would be based on geocoding in a real app)
      // This is a simplified example moving the map to a nearby location
      if (_currentPosition != null) {
        // Move map slightly based on the search query hash to simulate different locations
        final double latOffset = query.hashCode % 100 * 0.0001;
        final double lonOffset = query.hashCode % 50 * 0.0001;

        _mapController.move(
          LatLng(
            _currentPosition!.latitude + latOffset,
            _currentPosition!.longitude + lonOffset,
          ),
          15.0,
        );
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Location set to: $query'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    });
  }

  @override
  void dispose() {
    // Clean up the controller when the widget is disposed
    try {
      _mapController.dispose();
    } catch (e) {
      print('Error disposing MapController: $e');
    }
    super.dispose();
  }
}
