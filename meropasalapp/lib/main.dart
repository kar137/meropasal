import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'shop.dart';
import 'welcome.dart'; // Import the new welcome page

void main() {
  runApp(MyRootApp());
}

class MyRootApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'नेपाल पसल प्रबन्धक',
      theme: ThemeData(
        primarySwatch: Colors.green,
        primaryColor: Color(0xFF1E88E5),
        fontFamily: 'Roboto',
      ),
      home: WelcomePage(), // Changed from LoginPage() to WelcomePage()
      debugShowCheckedModeBanner: false,
    );
  }
}
