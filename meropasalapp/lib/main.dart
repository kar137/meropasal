import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:meropasalapp/utils/app_colors.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'shop.dart';
import 'welcome.dart'; // Import the new welcome page

void main() async {
  // Ensure Flutter is initialized before doing anything
  WidgetsFlutterBinding.ensureInitialized();

  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(MyRootApp());
}

class MyRootApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'नेपाल पसल प्रबन्धक',
      theme: ThemeData(
        fontFamily: 'Roboto',
        appBarTheme: AppBarTheme(
          backgroundColor: AppColors.MainColor,
          titleTextStyle: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
          foregroundColor: Colors.white,
        ),
      ),
      home: WelcomePage(), // Changed from LoginPage() to WelcomePage()
      debugShowCheckedModeBanner: false,
    );
  }
}
