import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

/// A comprehensive service for handling location-related functionality
///
/// This service provides methods for:
/// - Checking and requesting location permissions
/// - Getting the current position
/// - Streaming position updates
/// - Calculating distance between coordinates
class LocationService {
  // Singleton instance
  static final LocationService _instance = LocationService._internal();

  // Stream controller for broadcasting location updates
  final StreamController<Position> _locationStreamController =
      StreamController<Position>.broadcast();

  // Current position cache
  Position? _lastKnownPosition;

  // Stream subscription for location updates
  StreamSubscription<Position>? _positionStreamSubscription;

  // Factory constructor to return the singleton instance
  factory LocationService() {
    return _instance;
  }

  // Private constructor
  LocationService._internal();

  /// Checks if location services are enabled on the device
  ///
  /// Returns a [Future<bool>] that completes with true if location services
  /// are enabled, or false otherwise.
  Future<bool> isLocationServiceEnabled() async {
    return await Geolocator.isLocationServiceEnabled();
  }

  /// Checks the current permission status
  ///
  /// Returns a [Future<LocationPermission>] that completes with the current
  /// permission status.
  Future<LocationPermission> checkPermission() async {
    return await Geolocator.checkPermission();
  }

  /// Requests location permission from the user
  ///
  /// Returns a [Future<LocationPermission>] that completes with the new
  /// permission status after the request.
  Future<LocationPermission> requestPermission() async {
    return await Geolocator.requestPermission();
  }

  /// Handles the permission flow, checking and requesting as needed
  ///
  /// Returns a [Future<bool>] that completes with true if the permission
  /// was granted, or false otherwise.
  Future<bool> handlePermission() async {
    // Check if location services are enabled
    final serviceEnabled = await isLocationServiceEnabled();
    if (!serviceEnabled) {
      return false;
    }

    // Check the current permission status
    var permission = await checkPermission();

    // If denied, request permission
    if (permission == LocationPermission.denied) {
      permission = await requestPermission();
      if (permission == LocationPermission.denied) {
        return false;
      }
    }

    // If permanently denied, we can't request permission again
    if (permission == LocationPermission.deniedForever) {
      return false;
    }

    return true;
  }

  /// Opens the app settings if permission is permanently denied
  ///
  /// This can be called when the user needs to manually enable location
  /// permissions from settings.
  Future<bool> openAppSettings() async {
    return await Geolocator.openAppSettings();
  }

  /// Opens the location settings on the device
  ///
  /// This can be called when location services are disabled and need to be
  /// enabled by the user.
  Future<bool> openLocationSettings() async {
    return await Geolocator.openLocationSettings();
  }

  /// Gets the current position of the device
  ///
  /// Parameters:
  /// - [accuracy]: The desired accuracy of the location data
  /// - [timeLimit]: The maximum time to wait for a location update
  /// - [forceAndroidLocationManager]: Whether to use the Android LocationManager
  ///   instead of the fused location provider
  ///
  /// Returns a [Future<Position>] that completes with the current position
  Future<Position> getCurrentPosition({
    LocationAccuracy accuracy = LocationAccuracy.high,
    Duration? timeLimit,
    bool forceAndroidLocationManager = false,
  }) async {
    final hasPermission = await handlePermission();
    if (!hasPermission) {
      throw LocationServiceException("Location permission denied");
    }

    try {
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: accuracy,
        timeLimit: timeLimit,
        forceAndroidLocationManager: forceAndroidLocationManager,
      );

      _lastKnownPosition = position;
      return position;
    } catch (e) {
      throw LocationServiceException("Failed to get current position: $e");
    }
  }

  /// Gets the last known position without making a new location request
  ///
  /// Returns a [Future<Position?>] that completes with the last known position,
  /// or null if no position is available.
  Future<Position?> getLastKnownPosition() async {
    if (_lastKnownPosition != null) {
      return _lastKnownPosition;
    }

    try {
      final position = await Geolocator.getLastKnownPosition();
      _lastKnownPosition = position;
      return position;
    } catch (e) {
      return null;
    }
  }

  /// Starts streaming position updates
  ///
  /// Parameters:
  /// - [accuracy]: The desired accuracy of the location data
  /// - [distanceFilter]: The minimum distance in meters the device must move
  ///   before a new location update is generated
  /// - [timeInterval]: The minimum time interval between location updates
  ///
  /// Returns a [Stream<Position>] that emits position updates
  Stream<Position> getPositionStream({
    LocationAccuracy accuracy = LocationAccuracy.high,
    int distanceFilter = 10,
    int timeInterval = 5000,
  }) {
    // Ensure we have only one active stream
    stopPositionStream();

    // Create the location options
    final locationSettings = LocationSettings(
      accuracy: accuracy,
      distanceFilter: distanceFilter,
      timeLimit: Duration(milliseconds: timeInterval),
    );

    // Start the position stream and listen to it
    _positionStreamSubscription =
        Geolocator.getPositionStream(locationSettings: locationSettings).listen(
          (Position position) {
            _lastKnownPosition = position;
            _locationStreamController.add(position);
          },
          onError: (error) {
            _locationStreamController.addError(error);
          },
        );

    return _locationStreamController.stream;
  }

  /// Stops streaming position updates
  void stopPositionStream() {
    _positionStreamSubscription?.cancel();
    _positionStreamSubscription = null;
  }

  /// Calculates the distance between two coordinates using the Haversine formula
  ///
  /// Parameters:
  /// - [startLatitude]: The latitude of the starting point
  /// - [startLongitude]: The longitude of the starting point
  /// - [endLatitude]: The latitude of the ending point
  /// - [endLongitude]: The longitude of the ending point
  ///
  /// Returns the distance in meters between the two coordinates
  double calculateDistance({
    required double startLatitude,
    required double startLongitude,
    required double endLatitude,
    required double endLongitude,
  }) {
    return Geolocator.distanceBetween(
      startLatitude,
      startLongitude,
      endLatitude,
      endLongitude,
    );
  }

  /// Calculates the distance between two positions
  ///
  /// Parameters:
  /// - [start]: The starting position
  /// - [end]: The ending position
  ///
  /// Returns the distance in meters between the two positions
  double calculateDistanceBetweenPositions(Position start, Position end) {
    return calculateDistance(
      startLatitude: start.latitude,
      startLongitude: start.longitude,
      endLatitude: end.latitude,
      endLongitude: end.longitude,
    );
  }

  /// Calculates the bearing between two coordinates
  ///
  /// Parameters:
  /// - [startLatitude]: The latitude of the starting point
  /// - [startLongitude]: The longitude of the starting point
  /// - [endLatitude]: The latitude of the ending point
  /// - [endLongitude]: The longitude of the ending point
  ///
  /// Returns the bearing in degrees (0-360) between the two coordinates
  double calculateBearing({
    required double startLatitude,
    required double startLongitude,
    required double endLatitude,
    required double endLongitude,
  }) {
    // Convert to radians
    final startLat = startLatitude * math.pi / 180;
    final startLng = startLongitude * math.pi / 180;
    final endLat = endLatitude * math.pi / 180;
    final endLng = endLongitude * math.pi / 180;

    // Calculate bearing
    final y = math.sin(endLng - startLng) * math.cos(endLat);
    final x =
        math.cos(startLat) * math.sin(endLat) -
        math.sin(startLat) * math.cos(endLat) * math.cos(endLng - startLng);
    final bearing = math.atan2(y, x);

    // Convert to degrees
    var bearingDegrees = (bearing * 180 / math.pi + 360) % 360;

    return bearingDegrees;
  }

  /// Disposes the location service, cleaning up resources
  void dispose() {
    stopPositionStream();
    _locationStreamController.close();
  }
}

/// Custom exception for location service errors
class LocationServiceException implements Exception {
  final String message;

  LocationServiceException(this.message);

  @override
  String toString() => 'LocationServiceException: $message';
}

/// A widget that helps handle location permissions
///
/// This widget will check location permissions and show appropriate UI
/// based on the permission status.
class LocationPermissionHandler extends StatefulWidget {
  final Widget child;
  final Widget Function(BuildContext, VoidCallback) permissionDeniedBuilder;
  final Widget Function(BuildContext, VoidCallback) serviceDisabledBuilder;

  const LocationPermissionHandler({
    Key? key,
    required this.child,
    required this.permissionDeniedBuilder,
    required this.serviceDisabledBuilder,
  }) : super(key: key);

  @override
  State<LocationPermissionHandler> createState() =>
      _LocationPermissionHandlerState();
}

class _LocationPermissionHandlerState extends State<LocationPermissionHandler> {
  final LocationService _locationService = LocationService();
  bool _permissionsChecked = false;
  bool _hasPermission = false;
  bool _serviceEnabled = false;

  @override
  void initState() {
    super.initState();
    _checkLocationPermissions();
  }

  Future<void> _checkLocationPermissions() async {
    try {
      _serviceEnabled = await _locationService.isLocationServiceEnabled();
      if (_serviceEnabled) {
        _hasPermission = await _locationService.handlePermission();
      }
    } finally {
      if (mounted) {
        setState(() {
          _permissionsChecked = true;
        });
      }
    }
  }

  Future<void> _requestPermission() async {
    try {
      _hasPermission = await _locationService.handlePermission();
      if (mounted) {
        setState(() {});
      }
    } catch (e) {
      // Handle error
    }
  }

  Future<void> _openLocationSettings() async {
    try {
      await _locationService.openLocationSettings();
      // After returning from settings, check again
      if (mounted) {
        _checkLocationPermissions();
      }
    } catch (e) {
      // Handle error
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_permissionsChecked) {
      return Center(child: CircularProgressIndicator());
    }

    if (!_serviceEnabled) {
      return widget.serviceDisabledBuilder(context, _openLocationSettings);
    }

    if (!_hasPermission) {
      return widget.permissionDeniedBuilder(context, _requestPermission);
    }

    return widget.child;
  }
}
