import 'package:flutter/material.dart';
import 'search_page.dart';
import 'location_search_modal.dart';
import 'location_map_page.dart';
import '../qr_scanner.dart';

class CustomerHomePage extends StatefulWidget {
  const CustomerHomePage({Key? key}) : super(key: key);

  @override
  State<CustomerHomePage> createState() => _CustomerHomePageState();
}

class _CustomerHomePageState extends State<CustomerHomePage> {
  int _selectedIndex = 0;

  // Show location search modal
  void _showLocationSearchModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.85,
        child: LocationSearchModal(currentLocation: "Kalanki Chowk, Kathmandu"),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFFF9FAFC),
      appBar: AppBar(
        backgroundColor: Color(0xFF4F46E5),
        elevation: 0,
        title: Text(
          "मेरो पसल",
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        actions: [
          Container(
            margin: EdgeInsets.only(right: 16),
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white24,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.star, color: Colors.amber, size: 18),
                SizedBox(width: 4),
                Text(
                  "250 PTS",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          CircleAvatar(
            backgroundColor: Colors.white,
            radius: 18,
            child: Text(
              "G",
              style: TextStyle(
                color: Color(0xFF4F46E5),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          SizedBox(width: 16),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Location Bar
            GestureDetector(
              onTap: () {
                _showLocationSearchModal();
              },
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 4,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Icon(Icons.location_on_outlined, color: Color(0xFF6B7280)),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        "Kalanki Chowk, Kathmandu",
                        style: TextStyle(
                          color: Color(0xFF111827),
                          fontSize: 15,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Icon(Icons.keyboard_arrow_right, color: Color(0xFF6B7280)),
                  ],
                ),
              ),
            ),
            SizedBox(height: 16),

            // Service Categories
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Grid of service categories
                  GridView.count(
                    shrinkWrap: true,
                    physics: NeverScrollableScrollPhysics(),
                    crossAxisCount: 3,
                    childAspectRatio: 1.1,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    children: [
                      _buildCategoryItem(
                        "Grocery",
                        Icons.shopping_basket,
                        Color(0xFFFEF2F2),
                      ),
                      _buildCategoryItem(
                        "Electronics",
                        Icons.electrical_services,
                        Color(0xFFF0F9FF),
                      ),
                      _buildCategoryItem(
                        "Fashion",
                        Icons.checkroom,
                        Color(0xFFFDF2F8),
                      ),
                      _buildCategoryItem(
                        "Pharmacy",
                        Icons.local_pharmacy,
                        Color(0xFFECFDF5),
                      ),
                      _buildCategoryItem(
                        "Books",
                        Icons.menu_book,
                        Color(0xFFFFFBEB),
                      ),
                      _buildCategoryItem(
                        "Food",
                        Icons.restaurant,
                        Color(0xFFFFF7ED),
                      ),
                      _buildCategoryItem(
                        "Furniture",
                        Icons.chair,
                        Color(0xFFF8FAFC),
                      ),
                      _buildCategoryItem(
                        "Services",
                        Icons.miscellaneous_services,
                        Color(0xFFF3F4F6),
                      ),
                      _buildCategoryItem(
                        "History",
                        Icons.history,
                        Color(0xFFEFF6FF),
                      ),
                    ],
                  ),

                  SizedBox(height: 24),

                  // Featured Stores Section
                  Text(
                    "Featured Stores",
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF111827),
                    ),
                  ),
                  SizedBox(height: 16),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _buildFeaturedStoreCard(
                          "ABC Grocery Store",
                          "4.8",
                          "Groceries & Daily Needs",
                          "2.3 km",
                        ),
                        _buildFeaturedStoreCard(
                          "XYZ Electronics",
                          "4.5",
                          "Electronics & Gadgets",
                          "3.5 km",
                        ),
                        _buildFeaturedStoreCard(
                          "Fashion Hub",
                          "4.7",
                          "Clothing & Accessories",
                          "1.8 km",
                        ),
                      ],
                    ),
                  ),

                  SizedBox(height: 24),

                  // Special Offers
                  Text(
                    "Special Offers",
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF111827),
                    ),
                  ),
                  SizedBox(height: 16),
                  _buildSpecialOfferCard(),
                  SizedBox(height: 16),
                  _buildSpecialOfferCard(isSecond: true),
                  SizedBox(height: 24),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          if (index == 2) {
            // Navigate to QR Scanner
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => QrScannerPage()),
            );
          } else {
            setState(() {
              _selectedIndex = index;
            });
          }
        },
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        selectedItemColor: Color(0xFF4F46E5),
        unselectedItemColor: Color(0xFF6B7280),
        selectedLabelStyle: TextStyle(
          fontWeight: FontWeight.w500,
          fontSize: 12,
        ),
        unselectedLabelStyle: TextStyle(
          fontWeight: FontWeight.w500,
          fontSize: 12,
        ),
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_bag_outlined),
            activeIcon: Icon(Icons.shopping_bag),
            label: 'Orders',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.qr_code_scanner),
            activeIcon: Icon(Icons.qr_code_scanner),
            label: 'QR Scanner',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_outlined),
            activeIcon: Icon(Icons.history),
            label: 'History',
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryItem(String title, IconData icon, Color bgColor) {
    return GestureDetector(
      onTap: () {
        // Handle category tap
        if (title == "History") {
          // Navigate to history page
          // Navigator.push(context, MaterialPageRoute(builder: (context) => HistoryPage()));
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Opening $title...'),
              behavior: SnackBarBehavior.floating,
              backgroundColor: Color(0xFF4F46E5),
            ),
          );
        } else {
          // Navigate to search page with the category
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SearchPage(category: title),
            ),
          );
        }
      },
      child: Container(
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 4,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: Icon(icon, color: Color(0xFF4F46E5), size: 28),
            ),
            SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Color(0xFF111827),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeaturedStoreCard(
    String name,
    String rating,
    String type,
    String distance,
  ) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => LocationMapPage(
              itemName: "Store Location",
              shopName: name,
              itemCategory: type,
            ),
          ),
        );
      },
      child: Container(
        width: 220,
        margin: EdgeInsets.only(right: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Store image
            Container(
              height: 120,
              decoration: BoxDecoration(
                color: Color(0xFFE5E7EB),
                borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
              ),
              child: Center(
                child: Icon(
                  Icons.storefront,
                  size: 40,
                  color: Color(0xFF6B7280),
                ),
              ),
            ),
            Padding(
              padding: EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Flexible(
                        child: Text(
                          name,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF111827),
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Color(0xFF10B981),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.star, color: Colors.white, size: 12),
                            SizedBox(width: 2),
                            Text(
                              rating,
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 4),
                  Text(
                    type,
                    style: TextStyle(fontSize: 13, color: Color(0xFF6B7280)),
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 6),
                  Row(
                    children: [
                      Icon(
                        Icons.location_on,
                        size: 14,
                        color: Color(0xFF6B7280),
                      ),
                      SizedBox(width: 2),
                      Text(
                        distance,
                        style: TextStyle(
                          fontSize: 13,
                          color: Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSpecialOfferCard({bool isSecond = false}) {
    return Container(
      width: double.infinity,
      height: 140,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isSecond
              ? [Color(0xFFFEF3C7), Color(0xFFFEF9C3)]
              : [Color(0xFFDCFCE7), Color(0xFFD1FAE5)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Stack(
        children: [
          Positioned(
            right: 0,
            bottom: 0,
            top: 0,
            child: Container(
              width: 120,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.only(
                  topRight: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                ),
              ),
              child: Center(
                child: Icon(
                  isSecond ? Icons.local_offer : Icons.discount,
                  size: 60,
                  color: Colors.white.withOpacity(0.5),
                ),
              ),
            ),
          ),
          Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    isSecond ? "FESTIVAL OFFER" : "NEW USER OFFER",
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isSecond ? Color(0xFFF59E0B) : Color(0xFF10B981),
                    ),
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  isSecond
                      ? "Get 15% off on Dashain"
                      : "20% off on first order",
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF111827),
                  ),
                ),
                SizedBox(height: 6),
                Text(
                  isSecond
                      ? "Valid until October 15, 2025"
                      : "Use code: FIRST20 at checkout",
                  style: TextStyle(fontSize: 14, color: Color(0xFF4B5563)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class HistoryPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Order History'),
        backgroundColor: Color(0xFF4F46E5),
      ),
      body: ListView.builder(
        padding: EdgeInsets.all(16),
        itemCount: 5,
        itemBuilder: (context, index) {
          return _buildHistoryItem(
            context,
            date: "July ${12 - index}, 2025",
            storeName:
                "Store ${['ABC Grocery', 'XYZ Electronics', 'Daily Needs', 'Quick Mart', 'City Shop'][index]}",
            amount: "Rs. ${(index + 1) * 550}",
            items: "${index + 2} items",
            status: index == 0
                ? "Delivered"
                : (index == 1 ? "Processing" : "Completed"),
          );
        },
      ),
    );
  }

  Widget _buildHistoryItem(
    BuildContext context, {
    required String date,
    required String storeName,
    required String amount,
    required String items,
    required String status,
  }) {
    Color statusColor;
    if (status == "Delivered") {
      statusColor = Color(0xFF10B981);
    } else if (status == "Processing") {
      statusColor = Color(0xFFF59E0B);
    } else {
      statusColor = Color(0xFF4F46E5);
    }

    return Container(
      margin: EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  date,
                  style: TextStyle(fontSize: 14, color: Color(0xFF6B7280)),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    status,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                ),
              ],
            ),
            Divider(height: 20),
            Row(
              children: [
                Container(
                  padding: EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Color(0xFFF3F4F6),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(Icons.shopping_bag, color: Color(0xFF4F46E5)),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        storeName,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF111827),
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        "$items • $amount",
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 16,
                  color: Color(0xFF6B7280),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
