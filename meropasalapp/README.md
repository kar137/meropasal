# MeroPasal App

A Flutter e-commerce application with real-time location tracking capabilities.

## Features

- Beautiful welcome screen with user role selection (customer/shopkeeper)
- Modern, minimal UI/UX design with consistent color palette and spacing
- Comprehensive login system with role-based navigation
- Customer homepage with Pathao-like category grid
- Featured stores and special offers sections
- Order history tracking for customers
- Real-time location tracking and map integration

## Location Services

The app includes a comprehensive location service that provides:

1. **Permission Handling**
   - Permission request and checks
   - Handling for denied/permanently denied permissions
   - Settings navigation helpers

2. **Real-time Location**
   - Stream of location updates with customizable accuracy and interval
   - Current position fetching with options
   - Background tracking capabilities

3. **Distance Calculation**
   - Haversine formula for accurate distance calculation
   - Helper methods for working with coordinates and positions
   - Bearing calculation between points

4. **Usage Example**
   - See `lib/examples/location_example.dart` for a complete example

## Google Maps Integration

The app uses Google Maps to display user location and allow for location selection.

## Getting Started

### Prerequisites

- Flutter SDK (3.8+)
- Android Studio / VS Code
- Google Maps API Key (for map functionality)

### Setting Up Maps

1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Update the API key in:
   - Android: `android/app/src/main/AndroidManifest.xml`
   - iOS: `ios/Runner/AppDelegate.swift`

### Running the App

```bash
flutter pub get
flutter run
```
