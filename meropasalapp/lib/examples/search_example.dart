import 'package:flutter/material.dart';
import 'package:meropasalapp/screens/search_page.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MeroPasal App',
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        primaryColor: Color(0xFF4F46E5),
        colorScheme: ColorScheme.fromSwatch(
          primarySwatch: Colors.indigo,
          accentColor: Colors.red,
        ),
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: SearchPage(category: 'Vegetables'),
      debugShowCheckedModeBanner: false,
    );
  }
}
