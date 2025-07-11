import 'package:flutter/material.dart';

import 'homepage.dart';
import 'user_profile.dart';
import 'logs_screen.dart';
import 'custom_bottom_navbar.dart';
import 'user.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  late final List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    _pages = [
      HomeScreen(
        isDark: false,
        onThemeSwitch: () {
          // You can expand theme logic here or lift state up
        },
      ),
      UserProfileScreen(
        user: User(
          id: 'shop001',
          name: 'Shop Owner',
          shopName: 'My Shop',
          location: 'Kathmandu, Nepal',
          contact: '+977-9800000000',
          email: 'contact@myshop.com',
          website: 'https://myshop.com',
          description: 'This is my shop profile',
          profileImageUrl: '',
        ),
      ),
      const LogsScreen(),
    ];
  }

  void _onNavTap(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_selectedIndex],
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: _selectedIndex,
        onTap: _onNavTap,
      ),
    );
  }
}
