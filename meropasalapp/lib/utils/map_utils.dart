import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';

class MapUtils {
  /// Initialize the map configuration
  static Future<void> initializeMapSettings() async {
    // No specific initialization needed for OpenStreetMap
    // This method is kept for compatibility and potential future use
  }

  /// Get default location (centered on Nepal)
  static LatLng getDefaultLocation() {
    return LatLng(27.7172, 85.3240); // Default to Kathmandu
  }

  /// Handle map loading errors
  static void handleMapError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Map error: $message'),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
