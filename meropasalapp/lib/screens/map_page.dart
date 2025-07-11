import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import '../services/location_service.dart';

class MapPage extends StatefulWidget {
  final String location;

  const MapPage({Key? key, required this.location}) : super(key: key);

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  final LocationService _locationService = LocationService();
  final Completer<GoogleMapController> _controller =
      Completer<GoogleMapController>();

  // Default location (centered on Nepal)
  CameraPosition _initialCameraPosition = CameraPosition(
    target: LatLng(27.7172, 85.3240), // Default to Kathmandu
    zoom: 14.0,
  );

  Set<Marker> _markers = {};
  bool _isLoading = true;
  bool _locationEnabled = false;
  Position? _currentPosition;
  StreamSubscription<Position>? _positionStreamSubscription;

  @override
  void initState() {
    super.initState();
    _setupLocationService();
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

      // Update camera position
      _initialCameraPosition = CameraPosition(
        target: LatLng(position.latitude, position.longitude),
        zoom: 16.0,
      );

      // Update marker
      _markers = {
        Marker(
          markerId: MarkerId('currentLocation'),
          position: LatLng(position.latitude, position.longitude),
          infoWindow: InfoWindow(title: widget.location),
        ),
      };
    });

    // Move camera to new position
    _animateToCurrentLocation();
  }

  Future<void> _animateToCurrentLocation() async {
    if (_currentPosition != null && _controller.isCompleted) {
      final GoogleMapController controller = await _controller.future;
      controller.animateCamera(
        CameraUpdate.newCameraPosition(
          CameraPosition(
            target: LatLng(
              _currentPosition!.latitude,
              _currentPosition!.longitude,
            ),
            zoom: 16.0,
          ),
        ),
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

  void _zoomIn() async {
    if (_controller.isCompleted) {
      final controller = await _controller.future;
      controller.animateCamera(CameraUpdate.zoomIn());
    }
  }

  void _zoomOut() async {
    if (_controller.isCompleted) {
      final controller = await _controller.future;
      controller.animateCamera(CameraUpdate.zoomOut());
    }
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
              : GoogleMap(
                  mapType: MapType.normal,
                  initialCameraPosition: _initialCameraPosition,
                  markers: _markers,
                  myLocationEnabled: true,
                  myLocationButtonEnabled: false,
                  zoomControlsEnabled: false,
                  compassEnabled: true,
                  onMapCreated: (GoogleMapController controller) {
                    _controller.complete(controller);
                  },
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
