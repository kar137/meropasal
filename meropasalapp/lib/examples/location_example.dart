import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../services/location_service.dart';

/// Example class that demonstrates how to use the LocationService
class LocationExample extends StatefulWidget {
  const LocationExample({Key? key}) : super(key: key);

  @override
  State<LocationExample> createState() => _LocationExampleState();
}

class _LocationExampleState extends State<LocationExample> {
  final LocationService _locationService = LocationService();
  Position? _currentPosition;
  StreamSubscription<Position>? _positionStreamSubscription;
  bool _isLoading = true;
  bool _isStreaming = false;
  String _statusMessage = "Checking permissions...";
  List<Position> _locationHistory = [];

  @override
  void initState() {
    super.initState();
    _initLocationService();
  }

  @override
  void dispose() {
    _stopPositionStream();
    super.dispose();
  }

  Future<void> _initLocationService() async {
    setState(() {
      _isLoading = true;
      _statusMessage = "Checking permissions...";
    });

    try {
      // Check and handle permissions
      bool hasPermission = await _locationService.handlePermission();

      if (hasPermission) {
        setState(() {
          _statusMessage = "Getting current location...";
        });

        // Get current position
        final position = await _locationService.getCurrentPosition();

        setState(() {
          _currentPosition = position;
          _isLoading = false;
          _statusMessage = "Ready";
          _locationHistory.add(position);
        });
      } else {
        setState(() {
          _isLoading = false;
          _statusMessage = "Location permission denied";
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _statusMessage = "Error: ${e.toString()}";
      });
    }
  }

  void _startPositionStream() {
    setState(() {
      _isStreaming = true;
      _statusMessage = "Streaming location updates...";
    });

    _positionStreamSubscription = _locationService
        .getPositionStream(distanceFilter: 5)
        .listen(
          (Position position) {
            setState(() {
              _currentPosition = position;
              _locationHistory.add(position);

              // Keep history limited to last 10 positions
              if (_locationHistory.length > 10) {
                _locationHistory.removeAt(0);
              }
            });
          },
          onError: (e) {
            setState(() {
              _statusMessage = "Stream error: ${e.toString()}";
              _isStreaming = false;
            });
          },
        );
  }

  void _stopPositionStream() {
    if (_positionStreamSubscription != null) {
      _positionStreamSubscription!.cancel();
      _positionStreamSubscription = null;

      setState(() {
        _isStreaming = false;
        _statusMessage = "Stream stopped";
      });
    }
  }

  Future<void> _refreshCurrentPosition() async {
    setState(() {
      _isLoading = true;
      _statusMessage = "Updating location...";
    });

    try {
      final position = await _locationService.getCurrentPosition();

      setState(() {
        _currentPosition = position;
        _locationHistory.add(position);

        // Keep history limited to last 10 positions
        if (_locationHistory.length > 10) {
          _locationHistory.removeAt(0);
        }

        _isLoading = false;
        _statusMessage = "Location updated";
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _statusMessage = "Error updating location: ${e.toString()}";
      });
    }
  }

  String _getFormattedCoordinates(Position position) {
    return "(${position.latitude.toStringAsFixed(5)}, ${position.longitude.toStringAsFixed(5)})";
  }

  String _calculateDistance() {
    if (_locationHistory.length < 2) {
      return "N/A";
    }

    final start = _locationHistory.first;
    final end = _locationHistory.last;

    final distanceInMeters = _locationService.calculateDistanceBetweenPositions(
      start,
      end,
    );

    if (distanceInMeters < 1000) {
      return "${distanceInMeters.toStringAsFixed(1)} m";
    } else {
      return "${(distanceInMeters / 1000).toStringAsFixed(2)} km";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          "Location Example",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        ),
        backgroundColor: Color(0xFF4F46E5),
        elevation: 0,
        iconTheme: IconThemeData(color: Colors.white),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status card
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Status",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    Row(
                      children: [
                        _isLoading
                            ? SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Color(0xFF4F46E5),
                                ),
                              )
                            : Icon(
                                _isStreaming
                                    ? Icons.gps_fixed
                                    : Icons.gps_not_fixed,
                                color: _isStreaming
                                    ? Color(0xFF10B981)
                                    : Color(0xFF6B7280),
                              ),
                        SizedBox(width: 8),
                        Expanded(child: Text(_statusMessage)),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            SizedBox(height: 16),

            // Current position
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Current Position",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    if (_currentPosition != null)
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildInfoRow(
                            "Latitude",
                            _currentPosition!.latitude.toString(),
                          ),
                          _buildInfoRow(
                            "Longitude",
                            _currentPosition!.longitude.toString(),
                          ),
                          _buildInfoRow(
                            "Altitude",
                            "${_currentPosition!.altitude.toStringAsFixed(2)} m",
                          ),
                          _buildInfoRow(
                            "Accuracy",
                            "${_currentPosition!.accuracy.toStringAsFixed(2)} m",
                          ),
                          _buildInfoRow(
                            "Speed",
                            "${_currentPosition!.speed.toStringAsFixed(2)} m/s",
                          ),
                          _buildInfoRow(
                            "Heading",
                            "${_currentPosition!.heading.toStringAsFixed(1)}°",
                          ),
                          if (_locationHistory.length >= 2)
                            _buildInfoRow(
                              "Total Distance",
                              _calculateDistance(),
                            ),
                        ],
                      )
                    else
                      Text("No position data available"),
                  ],
                ),
              ),
            ),

            SizedBox(height: 16),

            // History
            Expanded(
              child: Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Location History",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Expanded(
                        child: _locationHistory.isEmpty
                            ? Center(child: Text("No history yet"))
                            : ListView.builder(
                                itemCount: _locationHistory.length,
                                itemBuilder: (context, index) {
                                  final position =
                                      _locationHistory[_locationHistory.length -
                                          1 -
                                          index];
                                  return Padding(
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 4.0,
                                    ),
                                    child: Row(
                                      children: [
                                        Icon(
                                          Icons.location_on,
                                          size: 16,
                                          color: Color(0xFF6B7280),
                                        ),
                                        SizedBox(width: 8),
                                        Text(
                                          _getFormattedCoordinates(position),
                                        ),
                                        if (index == 0)
                                          Padding(
                                            padding: const EdgeInsets.only(
                                              left: 8.0,
                                            ),
                                            child: Container(
                                              padding: EdgeInsets.symmetric(
                                                horizontal: 8,
                                                vertical: 2,
                                              ),
                                              decoration: BoxDecoration(
                                                color: Color(0xFF10B981),
                                                borderRadius:
                                                    BorderRadius.circular(12),
                                              ),
                                              child: Text(
                                                "Current",
                                                style: TextStyle(
                                                  color: Colors.white,
                                                  fontSize: 12,
                                                ),
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                  );
                                },
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
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Refresh position button
          FloatingActionButton(
            onPressed: _refreshCurrentPosition,
            heroTag: "refreshBtn",
            backgroundColor: Color(0xFF10B981),
            child: Icon(Icons.refresh),
          ),
          SizedBox(height: 16),
          // Start/stop streaming button
          FloatingActionButton(
            onPressed: _isStreaming
                ? _stopPositionStream
                : _startPositionStream,
            heroTag: "streamBtn",
            backgroundColor: Color(0xFF4F46E5),
            child: Icon(_isStreaming ? Icons.stop : Icons.play_arrow),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Text("$label: ", style: TextStyle(fontWeight: FontWeight.w500)),
          Text(value),
        ],
      ),
    );
  }
}
