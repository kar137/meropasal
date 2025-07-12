import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'location_example.dart';

void main() async {
  // Ensure Flutter is initialized before doing anything
  WidgetsFlutterBinding.ensureInitialized();

  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(const LocationExampleApp());
}

class LocationExampleApp extends StatelessWidget {
  const LocationExampleApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MeroPasal Location',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        primaryColor: const Color(0xFF1E88E5),
        fontFamily: 'Roboto',
      ),
      home: const LocationExample(
        title: 'Location Example',
        isSearchResults:
            true, // Set to true to show shop markers instead of vehicles
      ),
      debugShowCheckedModeBanner: false,
    );
  }
}
