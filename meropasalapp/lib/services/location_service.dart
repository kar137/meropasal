import 'dart:async';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

class LocationService {
  static final LocationService _instance = LocationService._internal();

  // Stream controller for location updates
  final _locationController = StreamController<Position>.broadcast();
  StreamSubscription<Position>? _positionStreamSubscription;

  // Singleton factory constructor
  factory LocationService() {
    return _instance;
  }

  LocationService._internal();

  // Stream getter
  Stream<Position> get locationStream => _locationController.stream;

  // Initialize location service and start listening to location updates
  Future<void> initialize() async {
    try {
      final permission = await _checkAndRequestPermission();
      if (permission) {
        await _startLocationUpdates();
      }
    } catch (e) {
      _locationController.addError(e);
    }
  }

  // Check and request location permission
  Future<bool> _checkAndRequestPermission() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location services are disabled.');
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied.');
      }
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception(
        'Location permissions are permanently denied. Please enable them in your device settings.',
      );
    }

    return permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse;
  }

  // Start location updates
  Future<void> _startLocationUpdates() async {
    // Cancel any existing subscription
    await _positionStreamSubscription?.cancel();

    // Get current position immediately
    try {
      final position = await getCurrentPosition();
      _locationController.add(position);
    } catch (e) {
      _locationController.addError(e);
    }

    // Start listening to location changes
    _positionStreamSubscription =
        Geolocator.getPositionStream(
          locationSettings: const LocationSettings(
            accuracy: LocationAccuracy.high,
            distanceFilter: 10, // Update every 10 meters
          ),
        ).listen(
          (position) => _locationController.add(position),
          onError: (error) => _locationController.addError(error),
        );
  }

  // Get current position once
  Future<Position> getCurrentPosition() async {
    final permission = await _checkAndRequestPermission();
    if (!permission) {
      throw Exception('Location permission not granted');
    }

    return await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );
  }

  // Calculate distance between two points
  double calculateDistance(LatLng point1, LatLng point2) {
    return Geolocator.distanceBetween(
      point1.latitude,
      point1.longitude,
      point2.latitude,
      point2.longitude,
    );
  }

  // Format distance for display
  String formatDistance(double distance) {
    if (distance < 1000) {
      return '${distance.toStringAsFixed(0)} m';
    } else {
      return '${(distance / 1000).toStringAsFixed(1)} km';
    }
  }

  // Handle permission (alias for _checkAndRequestPermission)
  Future<bool> handlePermission() async {
    return await _checkAndRequestPermission();
  }

  // Get position stream with custom settings
  Stream<Position> getPositionStream({int distanceFilter = 10}) {
    const LocationSettings locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10,
    );

    return Geolocator.getPositionStream(locationSettings: locationSettings);
  }

  // Open app settings
  Future<bool> openAppSettings() async {
    return await Geolocator.openAppSettings();
  }

  // Clean up resources
  void dispose() {
    _positionStreamSubscription?.cancel();
    _locationController.close();
  }
}
