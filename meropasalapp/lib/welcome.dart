import 'package:flutter/material.dart';
import 'login.dart';

class WelcomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFFF9FAFC), // Light background
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo placeholder (optional)
              Container(
                height: 120,
                width: 120,
                decoration: BoxDecoration(
                  color: Color(0x1A4F46E5), // Light indigo with opacity
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.store_rounded,
                  size: 64,
                  color: Color(0xFF4F46E5), // Royal Indigo
                ),
              ),
              SizedBox(height: 40),

              // Welcome message
              Text(
                "मेरो पसलमा स्वागत छ",
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF111827), // Text Primary
                  letterSpacing: 0.5,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 16),

              // Subtitle
              Text(
                "स्थानीय पसलहरूको डिजिटल समाधान।",
                style: TextStyle(
                  fontSize: 16,
                  color: Color(0xFF6B7280), // Subtext/Muted
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 64),

              // Customer Button
              _buildButton(
                context,
                "ग्राहक",
                Color(0xFF4F46E5), // Royal Indigo
                Color(0xFFFFFFFF), // White text
              ),
              SizedBox(height: 16),

              // Shopkeeper Button
              _buildButton(
                context,
                "पसलधारक",
                Color(0xFFFFFFFF), // White
                Color(0xFF1D1F2B), // Deep Charcoal text
                borderColor: Color(0xFFE5E7EB), // Border/Divider
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildButton(
    BuildContext context,
    String text,
    Color bgColor,
    Color textColor, {
    Color? borderColor,
  }) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () {
          final isCustomer = text == "ग्राहक";

          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => LoginPage(isCustomer: isCustomer),
            ),
          );
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: bgColor,
          foregroundColor: textColor,
          elevation: 2,
          padding: EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: borderColor != null
                ? BorderSide(color: borderColor, width: 1)
                : BorderSide.none,
          ),
        ),
        child: Text(
          text,
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
        ),
      ),
    );
  }
}
