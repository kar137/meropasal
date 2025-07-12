import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import '../services/location_service.dart';
import '../utils/map_utils.dart';

class MapPage extends StatefulWidget {
  final String location;

  const MapPage({Key? key, required this.location}) : super(key: key);

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  final LocationService _locationService = LocationService();
  final MapController _mapController = MapController();

  // Default location (centered on Nepal)
  LatLng _initialLocation = LatLng(27.7172, 85.3240); // Default to Kathmandu

  bool _isLoading = true;
  bool _locationEnabled = false;
  Position? _currentPosition;
  StreamSubscription<Position>? _positionStreamSubscription;

  // Shop markers
  final List<Marker> _shopMarkers = [];

  @override
  void initState() {
    super.initState();
    _initializeMap();
  }

  Future<void> _initializeMap() async {
    try {
      // Initialize map settings
      await MapUtils.initializeMapSettings();
      // Set up location service
      _setupLocationService();
    } catch (e) {
      MapUtils.handleMapError(context, e.toString());
    }
  }

  @override
  void dispose() {
    _positionStreamSubscription?.cancel();
    super.dispose();
  }

  Future<void> _setupLocationService() async {
    try {
      // Check location permissions
      bool hasPermission = await _locationService.handlePermission();

      if (hasPermission) {
        // Get initial position
        Position position = await _locationService.getCurrentPosition();
        _updatePosition(position);

        // Start listening for position updates
        _startPositionStream();

        setState(() {
          _locationEnabled = true;
          _isLoading = false;
        });
      } else {
        setState(() {
          _isLoading = false;
          _locationEnabled = false;
        });
        _showPermissionDeniedDialog();
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _locationEnabled = false;
      });
      _showErrorSnackBar("Location error: ${e.toString()}");
    }
  }

  void _startPositionStream() {
    _positionStreamSubscription = _locationService
        .getPositionStream(distanceFilter: 5)
        .listen(
          _updatePosition,
          onError: (e) =>
              _showErrorSnackBar("Location stream error: ${e.toString()}"),
        );
  }

  void _updatePosition(Position position) {
    setState(() {
      _currentPosition = position;

      // Update location
      _initialLocation = LatLng(position.latitude, position.longitude);

      // Add shop markers around user's position
      _addShopMarkers();
    });

    // Move map to new position
    _animateToCurrentLocation();
  }

  void _animateToCurrentLocation() {
    if (_currentPosition != null) {
      _mapController.move(
        LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
        16.0,
      );
    }
  }

  void _showPermissionDeniedDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Location Permission Required'),
          content: Text(
            'This app needs location permission to show your current location on the map.',
          ),
          actions: [
            TextButton(
              child: Text('Cancel'),
              onPressed: () => Navigator.of(context).pop(),
            ),
            TextButton(
              child: Text('Settings'),
              onPressed: () async {
                Navigator.of(context).pop();
                await _locationService.openAppSettings();
              },
            ),
          ],
        );
      },
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        backgroundColor: Colors.red,
      ),
    );
  }

  void _zoomIn() {
    final currentZoom = _mapController.zoom;
    _mapController.move(_mapController.center, currentZoom + 1);
  }

  void _zoomOut() {
    final currentZoom = _mapController.zoom;
    _mapController.move(_mapController.center, currentZoom - 1);
  }

  // Add mock shops for testing
  void _addShopMarkers() {
    // Clear existing markers
    _shopMarkers.clear();

    // Create sample shop locations around the user's location
    if (_currentPosition != null) {
      final userLat = _currentPosition!.latitude;
      final userLng = _currentPosition!.longitude;

      // Add some nearby shop markers
      _shopMarkers.addAll([
        _createShopMarker(
          LatLng(userLat + 0.003, userLng + 0.002),
          "Grocery Shop",
          "Grocery",
        ),
        _createShopMarker(
          LatLng(userLat - 0.002, userLng + 0.004),
          "Electronics Store",
          "Electronics",
        ),
        _createShopMarker(
          LatLng(userLat + 0.004, userLng - 0.003),
          "Fashion Outlet",
          "Fashion",
        ),
        _createShopMarker(
          LatLng(userLat - 0.003, userLng - 0.002),
          "Pharmacy",
          "Pharmacy",
        ),
      ]);
    }
  }

  Marker _createShopMarker(LatLng location, String name, String category) {
    return Marker(
      width: 50.0,
      height: 50.0,
      point: location,
      builder: (context) => GestureDetector(
        onTap: () => _showShopDetails(name, category, location),
        child: Column(
          children: [
            Container(
              padding: EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 4)],
              ),
              child: Icon(
                _getIconForCategory(category),
                color: Color(0xFF4F46E5),
                size: 24,
              ),
            ),
            Container(
              padding: EdgeInsets.symmetric(horizontal: 4, vertical: 2),
              decoration: BoxDecoration(
                color: Color(0xFF4F46E5),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                name,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.w500,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getIconForCategory(String category) {
    switch (category.toLowerCase()) {
      case 'grocery':
        return Icons.shopping_cart;
      case 'electronics':
        return Icons.devices;
      case 'fashion':
        return Icons.shopping_bag;
      case 'pharmacy':
        return Icons.local_pharmacy;
      default:
        return Icons.store;
    }
  }

  void _showShopDetails(String name, String category, LatLng location) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  name,
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  _getIconForCategory(category),
                  size: 16,
                  color: Color(0xFF6B7280),
                ),
                SizedBox(width: 8),
                Text(
                  category,
                  style: TextStyle(fontSize: 16, color: Color(0xFF6B7280)),
                ),
              ],
            ),
            SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.location_on, size: 16, color: Color(0xFF6B7280)),
                SizedBox(width: 8),
                Text(
                  "${location.latitude.toStringAsFixed(5)}, ${location.longitude.toStringAsFixed(5)}",
                  style: TextStyle(fontSize: 16, color: Color(0xFF6B7280)),
                ),
              ],
            ),
            SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFF4F46E5),
                  padding: EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text("Shop selected: $name"),
                      backgroundColor: Color(0xFF10B981),
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                },
                child: Text(
                  "Select Shop",
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          "Location",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        ),
        backgroundColor: Color(0xFF4F46E5),
        elevation: 0,
        iconTheme: IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: Icon(Icons.my_location),
            onPressed: _animateToCurrentLocation,
          ),
        ],
      ),
      body: Stack(
        children: [
          // Map or loading/error state
          _isLoading
              ? Center(
                  child: CircularProgressIndicator(color: Color(0xFF4F46E5)),
                )
              : !_locationEnabled
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.location_disabled,
                        size: 64,
                        color: Colors.grey,
                      ),
                      SizedBox(height: 16),
                      Text(
                        'Location services disabled',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _setupLocationService,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Color(0xFF4F46E5),
                          foregroundColor: Colors.white,
                        ),
                        child: Text('Enable Location'),
                      ),
                    ],
                  ),
                )
              : FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    center: _initialLocation,
                    zoom: 16.0,
                    onTap: (_, point) {
                      // Optional: Handle map tap
                    },
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.meropasal.app',
                    ),
                    // Current location marker
                    MarkerLayer(
                      markers: [
                        Marker(
                          width: 40.0,
                          height: 40.0,
                          point: _initialLocation,
                          builder: (ctx) => Container(
                            child: Icon(
                              Icons.location_on,
                              color: Colors.blue,
                              size: 40.0,
                            ),
                          ),
                        ),
                      ],
                    ),
                    // Shop markers
                    MarkerLayer(markers: _shopMarkers),
                  ],
                ),

          // Zoom controls
          if (!_isLoading && _locationEnabled)
            Positioned(
              right: 16,
              bottom: 100,
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 4,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    IconButton(icon: Icon(Icons.add), onPressed: _zoomIn),
                    Divider(height: 1, thickness: 1, color: Color(0xFFE5E7EB)),
                    IconButton(icon: Icon(Icons.remove), onPressed: _zoomOut),
                  ],
                ),
              ),
            ),

          // Bottom action bar
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: Offset(0, -5),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    "Your Current Location",
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF111827),
                    ),
                  ),
                  SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        Icons.location_on_outlined,
                        color: Color(0xFF6B7280),
                        size: 20,
                      ),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _currentPosition != null
                              ? "${widget.location} (${_currentPosition!.latitude.toStringAsFixed(5)}, ${_currentPosition!.longitude.toStringAsFixed(5)})"
                              : widget.location,
                          style: TextStyle(
                            color: Color(0xFF6B7280),
                            fontSize: 14,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 2,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        // Return location data to previous screen
                        if (_currentPosition != null) {
                          Navigator.pop(context, {
                            'address': widget.location,
                            'latitude': _currentPosition!.latitude,
                            'longitude': _currentPosition!.longitude,
                          });
                        } else {
                          Navigator.pop(context);
                        }

                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Location confirmed'),
                            behavior: SnackBarBehavior.floating,
                            backgroundColor: Color(0xFF10B981),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color(0xFF4F46E5),
                        foregroundColor: Colors.white,
                        padding: EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        "Confirm Location",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
