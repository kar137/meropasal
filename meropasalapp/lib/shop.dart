import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'screens/dashboard_page.dart';
import 'dart:math';
import 'login.dart'; // Import your login page

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'पसले',
      theme: ThemeData(
        primarySwatch: Colors.green,
        primaryColor: Color(0xFF1E88E5),
        fontFamily: 'Roboto',
      ),
      home: LoginPage(), // Show login page first
      debugShowCheckedModeBanner: false,
    );
  }
}

class Product {
  final String id;
  final String name;
  final String category;
  final double price;
  final String unit;
  int quantity;

  Product({
    required this.id,
    required this.name,
    required this.category,
    required this.price,
    required this.unit,
    this.quantity = 0,
  });

  static String generateProductId(String productName) {
    return 'PRD${productName.hashCode.abs().toString().substring(0, 6)}';
  }
}

class Shop {
  final String id;
  final String name;
  final String address;
  final String phone;
  final String type;

  Shop({
    required this.id,
    required this.name,
    required this.address,
    required this.phone,
    required this.type,
  });

  static String generateShopId(String shopName) {
    return 'SHP${shopName.hashCode.abs().toString().substring(0, 6)}';
  }
}

class SaleRecord {
  final String shopId;
  final String productId;
  final String transactionType; // 'SALE' or 'PURCHASE'
  final int quantity;
  final double unitPrice;
  final double totalAmount;
  final DateTime transactionTime;
  final String paymentMethod;

  SaleRecord({
    required this.shopId,
    required this.productId,
    required this.transactionType,
    required this.quantity,
    required this.unitPrice,
    required this.transactionTime,
    required this.paymentMethod,
  }) : totalAmount = unitPrice * quantity;

  static String generateTransactionId() {
    return 'TXN${DateTime.now().millisecondsSinceEpoch}';
  }

  // Add missing getters for dashboard_page.dart compatibility
  String get productName =>
      productId; // You may want to map productId to name if needed
  DateTime get time => transactionTime;
  String get type => transactionType.toLowerCase() == 'sale' ? 'sell' : 'buy';
}

class ShopHomePage extends StatefulWidget {
  @override
  _ShopHomePageState createState() => _ShopHomePageState();
}

class _ShopHomePageState extends State<ShopHomePage>
    with TickerProviderStateMixin {
  final TextEditingController _searchController = TextEditingController();
  String _selectedCategory = 'सबै';
  List<Product> _filteredProducts = [];
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  final List<String> _categories = [
    'सबै',
    'खानेकुरा',
    'नास्ता / स्न्याक्स',
    'पेय पदार्थ',
    'मसला',
    'घरेलु सामान',
  ];

  late final List<Product> _products;
  final List<SaleRecord> _sales = [];
  late stt.SpeechToText _speech;
  bool _isListening = false;
  bool _isDialogOpen = false;
  int _selectedNavbarIndex = 0;

  // Current shop information
  late Shop _currentShop;

  @override
  void initState() {
    super.initState();

    // Initialize shop
    _currentShop = Shop(
      id: Shop.generateShopId('सबित्रा किराना तथा चिया पसल'),
      name: 'सबित्रा किराना तथा चिया पसल',
      address: 'काठमाडौं, नेपाल',
      phone: '९८४५६७८९०१',
      type: 'किराना',
    );

    _products = [
      // खानेकुरा
      Product(
        id: 'PRD001',
        name: 'बास्मती चामल',
        category: 'खानेकुरा',
        price: 180,
        unit: 'केजी',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD002',
        name: 'दाल',
        category: 'खानेकुरा',
        price: 150,
        unit: 'केजी',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD003',
        name: 'तोरीको तेल',
        category: 'खानेकुरा',
        price: 320,
        unit: 'लिटर',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD004',
        name: 'नुन',
        category: 'खानेकुरा',
        price: 20,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD005',
        name: 'चिनी',
        category: 'खानेकुरा',
        price: 100,
        unit: 'केजी',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD006',
        name: 'पीठो',
        category: 'खानेकुरा',
        price: 85,
        unit: 'केजी',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD007',
        name: 'गुन्द्रुक',
        category: 'खानेकुरा',
        price: 95,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD008',
        name: 'गहुँ',
        category: 'खानेकुरा',
        price: 90,
        unit: 'केजी',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD009',
        name: 'मकै',
        category: 'खानेकुरा',
        price: 80,
        unit: 'केजी',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD010',
        name: 'कोदो',
        category: 'खानेकुरा',
        price: 100,
        unit: 'केजी',
        quantity: _rand(),
      ),

      // मसला
      Product(
        id: 'PRD011',
        name: 'जीरा',
        category: 'मसला',
        price: 200,
        unit: 'केजी',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD012',
        name: 'गरम मसला',
        category: 'मसला',
        price: 120,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD013',
        name: 'हल्दी पाउडर',
        category: 'मसला',
        price: 90,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD014',
        name: 'धनियाँ पाउडर',
        category: 'मसला',
        price: 80,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD015',
        name: 'अदुवा पाउडर',
        category: 'मसला',
        price: 100,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD016',
        name: 'लसुन पाउडर',
        category: 'मसला',
        price: 110,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),

      // नास्ता / स्न्याक्स
      Product(
        id: 'PRD017',
        name: 'चाउचाउ',
        category: 'नास्ता / स्न्याक्स',
        price: 25,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD018',
        name: 'कुरकुरे',
        category: 'नास्ता / स्न्याक्स',
        price: 20,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD019',
        name: 'बिस्कुट',
        category: 'नास्ता / स्न्याक्स',
        price: 30,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD020',
        name: 'पापड',
        category: 'नास्ता / स्न्याक्स',
        price: 15,
        unit: 'पिस',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD021',
        name: 'सेल रोटी मिक्स',
        category: 'नास्ता / स्न्याक्स',
        price: 125,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD022',
        name: 'भुजा',
        category: 'नास्ता / स्न्याक्स',
        price: 40,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD023',
        name: 'मकै भुटेको',
        category: 'नास्ता / स्न्याक्स',
        price: 30,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),

      // पेय पदार्थ
      Product(
        id: 'PRD024',
        name: 'कोकाकोला',
        category: 'पेय पदार्थ',
        price: 60,
        unit: 'बोतल',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD025',
        name: 'फ्रूटी',
        category: 'पेय पदार्थ',
        price: 25,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD026',
        name: 'रियल ज्यूस',
        category: 'पेय पदार्थ',
        price: 90,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD027',
        name: 'मिनरल वाटर',
        category: 'पेय पदार्थ',
        price: 20,
        unit: 'बोतल',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD028',
        name: 'नेपाली चिया',
        category: 'पेय पदार्थ',
        price: 45,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD029',
        name: 'इन्स्टेन्ट कफी',
        category: 'पेय पदार्थ',
        price: 120,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),

      // घरेलु सामान
      Product(
        id: 'PRD030',
        name: 'मह',
        category: 'घरेलु सामान',
        price: 850,
        unit: 'बोतल',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD031',
        name: 'अचार',
        category: 'घरेलु सामान',
        price: 280,
        unit: 'बोतल',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD032',
        name: 'घ्यु',
        category: 'घरेलु सामान',
        price: 1200,
        unit: 'लिटर',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD033',
        name: 'सावुन',
        category: 'घरेलु सामान',
        price: 25,
        unit: 'पिस',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD034',
        name: 'टुथपेस्ट',
        category: 'घरेलु सामान',
        price: 90,
        unit: 'वटा',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD035',
        name: 'ब्रस',
        category: 'घरेलु सामान',
        price: 40,
        unit: 'वटा',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD036',
        name: 'डिटर्जेन्ट पाउडर',
        category: 'घरेलु सामान',
        price: 90,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD037',
        name: 'डिटर्जेन्ट बार',
        category: 'घरेलु सामान',
        price: 25,
        unit: 'पिस',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD038',
        name: 'फिनाइल',
        category: 'घरेलु सामान',
        price: 100,
        unit: 'बोतल',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD039',
        name: 'झाडु',
        category: 'घरेलु सामान',
        price: 80,
        unit: 'वटा',
        quantity: _rand(),
      ),

      // खाना पकाउने सामग्री
      Product(
        id: 'PRD040',
        name: 'ग्यास सिलिन्डर',
        category: 'खाना पकाउने सामग्री',
        price: 1800,
        unit: 'वटा',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD041',
        name: 'कुकर',
        category: 'खाना पकाउने सामग्री',
        price: 1200,
        unit: 'वटा',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD042',
        name: 'भाँडा माझ्ने साबुन',
        category: 'खाना पकाउने सामग्री',
        price: 25,
        unit: 'पिस',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD043',
        name: 'भाँडा माझ्ने लिक्विड',
        category: 'खाना पकाउने सामग्री',
        price: 120,
        unit: 'बोतल',
        quantity: _rand(),
      ),

      // बच्चाको सामग्री
      Product(
        id: 'PRD044',
        name: 'पाम्पर्स',
        category: 'बच्चाको सामग्री',
        price: 300,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD045',
        name: 'बेबी लोसन',
        category: 'बच्चाको सामग्री',
        price: 250,
        unit: 'बोतल',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD046',
        name: 'बेबी पाउडर',
        category: 'बच्चाको सामग्री',
        price: 180,
        unit: 'बोतल',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD047',
        name: 'बेबी साबुन',
        category: 'बच्चाको सामग्री',
        price: 60,
        unit: 'पिस',
        quantity: _rand(),
      ),

      // अन्य
      Product(
        id: 'PRD048',
        name: 'मोमबत्ती',
        category: 'अन्य',
        price: 20,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
      Product(
        id: 'PRD049',
        name: 'म्याच बक्स',
        category: 'अन्य',
        price: 10,
        unit: 'प्याकेट',
        quantity: _rand(),
      ),
    ];

    _filteredProducts = _products;
    _animationController = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(_animationController);
    _animationController.forward();

    _speech = stt.SpeechToText();
  }

  static int _rand() => 5 + Random().nextInt(24); // 5 to 28

  @override
  void dispose() {
    _animationController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _filterProducts() {
    setState(() {
      _filteredProducts = _products.where((product) {
        final matchesSearch = product.name.toLowerCase().contains(
          _searchController.text.toLowerCase(),
        );
        final matchesCategory =
            _selectedCategory == 'सबै' || product.category == _selectedCategory;
        return matchesSearch && matchesCategory;
      }).toList();
    });
  }

  void _buyProduct(Product product) {
    setState(() {
      if (product.quantity < 20) {
        product.quantity++;
        _sales.add(
          SaleRecord(
            shopId: _currentShop.id,
            productId: product.id,
            transactionType: 'PURCHASE',
            quantity: 1,
            unitPrice: product.price,
            transactionTime: DateTime.now(),
            paymentMethod: 'CASH',
          ),
        );
      }
    });
    _showSnackBar(
      '${product.name} किनियो! जम्मा: ${product.quantity}',
      Colors.green,
    );
  }

  void _sellProduct(Product product) {
    setState(() {
      if (product.quantity > 0) {
        product.quantity--;
        _sales.add(
          SaleRecord(
            shopId: _currentShop.id,
            productId: product.id,
            transactionType: 'SALE',
            quantity: 1,
            unitPrice: product.price,
            transactionTime: DateTime.now(),
            paymentMethod: 'CASH',
          ),
        );
      }
    });
    _showSnackBar(
      '${product.name} बेचियो! जम्मा: ${product.quantity}',
      Colors.orange,
    );
  }

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        duration: Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case 'खानेकुरा':
        return Colors.teal;
      case 'नास्ता / स्न्याक्स':
        return Colors.deepOrange;
      case 'पेय पदार्थ':
        return Colors.blue;
      case 'मसला':
        return Colors.green;
      case 'घरेलु सामान':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'खानेकुरा':
        return Icons.fastfood;
      case 'नास्ता / स्न्याक्स':
        return Icons.fastfood;
      case 'पेय पदार्थ':
        return Icons.local_drink;
      case 'मसला':
        return Icons.spa;
      case 'घरेलु सामान':
        return Icons.home;
      default:
        return Icons.inventory_2;
    }
  }

  // --- MIC FUNCTION WITH POPUP ---
  void _showListeningDialog() {
    if (!_isDialogOpen) {
      _isDialogOpen = true;
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => WillPopScope(
          onWillPop: () async => false,
          child: AlertDialog(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  decoration: BoxDecoration(
                    color: Colors.blueGrey.shade50,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.blueGrey.shade100,
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  padding: EdgeInsets.all(22),
                  child: Icon(Icons.mic_rounded, color: Colors.red, size: 60),
                ),
                SizedBox(height: 14),
                Text(
                  "आवाज सुन्दैछ...\nकृपया बोल्नुहोस्!",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 16),
                Text(
                  "Voice is listening...",
                  style: TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ),
        ),
      ).then((_) {
        _isDialogOpen = false;
      });
    }
  }

  void _closeListeningDialog() {
    if (_isDialogOpen) {
      Navigator.of(context, rootNavigator: true).pop();
      _isDialogOpen = false;
    }
  }

  void _listenVoice() async {
    if (!_isListening) {
      bool available = await _speech.initialize(
        onStatus: (val) {
          if (val == 'done' || val == 'notListening') {
            setState(() => _isListening = false);
            _closeListeningDialog();
          }
        },
        onError: (val) {
          setState(() => _isListening = false);
          _closeListeningDialog();
          _showSnackBar('Mic error: ${val.errorMsg}', Colors.red);
        },
      );
      if (available) {
        setState(() => _isListening = true);
        _showListeningDialog();
        await _speech.listen(
          localeId: 'ne_NP',
          onResult: (val) {
            setState(() {
              _searchController.text = val.recognizedWords;
              _filterProducts();
            });
          },
        );
      } else {
        _showSnackBar('Speech recognition unavailable!', Colors.red);
      }
    } else {
      setState(() => _isListening = false);
      await _speech.stop();
      _closeListeningDialog();
    }
  }

  // --- END MIC FUNCTION WITH POPUP ---

  // --- Cool Bottom Navbar ---
  Widget _buildBottomNavbar() {
    return ClipRRect(
      borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
      child: BottomNavigationBar(
        backgroundColor: Colors.white,
        selectedItemColor: Color(0xFF1E88E5),
        unselectedItemColor: Colors.grey[500],
        currentIndex: _selectedNavbarIndex,
        elevation: 14,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
        selectedLabelStyle: TextStyle(fontWeight: FontWeight.bold),
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_rounded, size: 28),
            label: "गृहपृष्ठ",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_rounded, size: 28),
            label: "प्रोफाइल",
          ),

          BottomNavigationBarItem(
            icon: Icon(Icons.info_rounded, size: 28),
            label: "हाम्रो बारेमा",
          ),
        ],
        onTap: (index) {
          setState(() {
            _selectedNavbarIndex = index;
          });
          if (index == 1) {
            _showProfileDialog();
          } else if (index == 2) {
            _showAboutUsDialog();
          }
          // index==0 is home, do nothing (just stay here)
        },
      ),
    );
  }

  void _showProfileDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: Row(
          children: [
            Icon(Icons.person_rounded, color: Color(0xFF1E88E5)),
            SizedBox(width: 10),
            Text('प्रोफाइल', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircleAvatar(
                radius: 36,
                backgroundColor: Color(0xFF1E88E5),
                child: Icon(Icons.person, size: 48, color: Colors.white),
              ),
              SizedBox(height: 14),
              Text(
                'Ram Bahadur',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              SizedBox(height: 6),
              Text(
                'rambahadur@gmail.com',
                style: TextStyle(color: Colors.grey[700], fontSize: 14),
              ),
              SizedBox(height: 12),
              Divider(),
              ListTile(
                leading: Icon(Icons.store, color: Color(0xFF43A047)),
                title: Text('पसलको नाम:'),
                subtitle: Text(_currentShop.name),
              ),
              ListTile(
                leading: Icon(Icons.phone, color: Color(0xFF43A047)),
                title: Text('फोन:'),
                subtitle: Text(_currentShop.phone),
              ),
              ListTile(
                leading: Icon(Icons.location_on, color: Color(0xFF43A047)),
                title: Text('ठेगाना:'),
                subtitle: Text(_currentShop.address),
              ),
              ListTile(
                leading: Icon(Icons.category, color: Color(0xFF43A047)),
                title: Text('पसलको प्रकार:'),
                subtitle: Text(_currentShop.type),
              ),
              ListTile(
                leading: Icon(
                  Icons.confirmation_number,
                  color: Color(0xFF43A047),
                ),
                title: Text('पसल ID:'),
                subtitle: Text(_currentShop.id),
              ),
              ListTile(
                leading: Icon(Icons.sync, color: Color(0xFF43A047)),
                title: Text('अन्तिम Sync:'),
                subtitle: Text(
                  '${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}-${DateTime.now().day.toString().padLeft(2, '0')} ${DateTime.now().hour.toString().padLeft(2, '0')}:${DateTime.now().minute.toString().padLeft(2, '0')}',
                  style: TextStyle(fontSize: 13),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('ठिक छ'),
          ),
        ],
      ),
    );
  }

  void _showAboutUsDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: Row(
          children: [
            Icon(Icons.info_rounded, color: Color(0xFF1E88E5)),
            SizedBox(width: 10),
            Text(
              'हाम्रो बारेमा',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'पसले एप्लिकेशनले तपाईंलाई दैनिक पसलको कामकाजलाई सजिलो बनाउँछ। यसले उत्पादनहरू थप्न, किनमेल र बिक्री रेकर्ड गर्न, र विश्लेषण गर्न मद्दत गर्दछ।',
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 12),
              Text(
                'सहयोग र सुझावका लागि हामीलाई सम्पर्क गर्नुहोस्:',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text('Email: support@pasal.com'),
            ],
          ),
        ),
      ),
    );
  }

  // Fix: Add missing id for Product in _showAddProductDialog
  void _showAddProductDialog() {
    final nameController = TextEditingController();
    final priceController = TextEditingController();
    final unitController = TextEditingController();
    String selectedCategory = _categories[1]; // Default to first real category

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text('नयाँ उत्पादन थप्नुहोस्'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: InputDecoration(labelText: 'उत्पादन नाम'),
              ),
              SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: selectedCategory,
                decoration: InputDecoration(labelText: 'कोटि'),
                items: _categories
                    .where((cat) => cat != 'सबै')
                    .map(
                      (cat) => DropdownMenuItem(value: cat, child: Text(cat)),
                    )
                    .toList(),
                onChanged: (value) => setState(() => selectedCategory = value!),
              ),
              SizedBox(height: 12),
              TextField(
                controller: priceController,
                decoration: InputDecoration(labelText: 'मूल्य (रू)'),
                keyboardType: TextInputType.number,
              ),
              SizedBox(height: 12),
              TextField(
                controller: unitController,
                decoration: InputDecoration(
                  labelText: 'इकाई (केजी, वटा, लिटर)',
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('रद्द गर्नुहोस्'),
            ),
            ElevatedButton(
              onPressed: () {
                if (nameController.text.isNotEmpty &&
                    priceController.text.isNotEmpty &&
                    unitController.text.isNotEmpty) {
                  final newProduct = Product(
                    id: Product.generateProductId(nameController.text),
                    name: nameController.text,
                    category: selectedCategory,
                    price: double.parse(priceController.text),
                    unit: unitController.text,
                    quantity: _rand(),
                  );
                  setState(() {
                    _products.add(newProduct);
                    _filterProducts();
                  });
                  Navigator.pop(context);
                  _showSnackBar('उत्पादन सफलतापूर्वक थपियो!', Colors.green);
                }
              },
              child: Text('थप्नुहोस्'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFFF5F5F5),
      appBar: AppBar(
        title: Text(
          'पसले',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        backgroundColor: Color(0xFF1E88E5),
        elevation: 8,
        actions: [
          IconButton(
            icon: Icon(Icons.dashboard, color: Colors.white),
            tooltip: "ड्यासबोर्ड",
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      DashboardPage(products: _products, sales: _sales),
                ),
              );
            },
          ),
          IconButton(
            icon: Icon(Icons.analytics, color: Colors.white),
            tooltip: "विश्लेषण",
            onPressed: () => _showAnalytics(),
          ),
        ],
      ),
      body: Stack(
        children: [
          FadeTransition(
            opacity: _fadeAnimation,
            child: Column(
              children: [
                // Search and Filter Section
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.withOpacity(0.2),
                        spreadRadius: 2,
                        blurRadius: 8,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: 'उत्पादन खोज्नुहोस्...',
                          prefixIcon: Icon(
                            Icons.search,
                            color: Color(0xFF1E88E5),
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(25),
                            borderSide: BorderSide.none,
                          ),
                          filled: true,
                          fillColor: Color(0xFFF0F0F0),
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 15,
                          ),
                        ),
                        onChanged: (value) => _filterProducts(),
                      ),
                      SizedBox(height: 12),
                      Container(
                        height: 45,
                        child: ListView.builder(
                          scrollDirection: Axis.horizontal,
                          itemCount: _categories.length,
                          itemBuilder: (context, index) {
                            final category = _categories[index];
                            final isSelected = _selectedCategory == category;
                            return Padding(
                              padding: EdgeInsets.only(right: 8),
                              child: FilterChip(
                                label: Text(
                                  category,
                                  style: TextStyle(
                                    color: isSelected
                                        ? Colors.white
                                        : Color(0xFF1E88E5),
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                selected: isSelected,
                                onSelected: (selected) {
                                  setState(() {
                                    _selectedCategory = category;
                                    _filterProducts();
                                  });
                                },
                                backgroundColor: Colors.white,
                                selectedColor: Color(0xFF1E88E5),
                                elevation: isSelected ? 4 : 2,
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                // Products List
                Expanded(
                  child: ListView.builder(
                    padding: EdgeInsets.all(16),
                    itemCount: _filteredProducts.length,
                    itemBuilder: (context, index) {
                      final product = _filteredProducts[index];
                      return Container(
                        margin: EdgeInsets.only(bottom: 12),
                        child: Card(
                          elevation: 6,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(15),
                          ),
                          child: Container(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(15),
                              gradient: LinearGradient(
                                colors: [Colors.white, Color(0xFFFAFAFA)],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                            ),
                            child: Padding(
                              padding: EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Container(
                                        padding: EdgeInsets.all(8),
                                        decoration: BoxDecoration(
                                          color: _getCategoryColor(
                                            product.category,
                                          ).withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(
                                            8,
                                          ),
                                        ),
                                        child: Icon(
                                          _getCategoryIcon(product.category),
                                          color: _getCategoryColor(
                                            product.category,
                                          ),
                                          size: 24,
                                        ),
                                      ),
                                      SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              product.name,
                                              style: TextStyle(
                                                fontSize: 18,
                                                fontWeight: FontWeight.bold,
                                                color: Color(0xFF2C2C2C),
                                              ),
                                            ),
                                            Text(
                                              product.category,
                                              style: TextStyle(
                                                fontSize: 14,
                                                color: _getCategoryColor(
                                                  product.category,
                                                ),
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      Container(
                                        padding: EdgeInsets.symmetric(
                                          horizontal: 12,
                                          vertical: 6,
                                        ),
                                        decoration: BoxDecoration(
                                          color: product.quantity > 0
                                              ? Colors.green.withOpacity(0.1)
                                              : Colors.red.withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(
                                            20,
                                          ),
                                        ),
                                        child: Text(
                                          'स्टक: ${product.quantity}',
                                          style: TextStyle(
                                            color: product.quantity > 0
                                                ? Colors.green[700]
                                                : Colors.red[700],
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  SizedBox(height: 12),
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            'रू ${product.price.toStringAsFixed(0)}',
                                            style: TextStyle(
                                              fontSize: 20,
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF1E88E5),
                                            ),
                                          ),
                                          Text(
                                            'प्रति ${product.unit}',
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: Colors.grey[600],
                                            ),
                                          ),
                                        ],
                                      ),
                                      Row(
                                        children: [
                                          ElevatedButton(
                                            onPressed: () =>
                                                _buyProduct(product),
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor: Colors.red,
                                              foregroundColor: Colors.white,
                                              shape: RoundedRectangleBorder(
                                                borderRadius:
                                                    BorderRadius.circular(20),
                                              ),
                                              padding: EdgeInsets.symmetric(
                                                horizontal: 16,
                                                vertical: 8,
                                              ),
                                              elevation: 3,
                                            ),
                                            child: Row(
                                              mainAxisSize: MainAxisSize.min,
                                              children: [
                                                Icon(
                                                  Icons.add_shopping_cart,
                                                  size: 16,
                                                ),
                                                SizedBox(width: 4),
                                                Text(
                                                  'किनियो',
                                                  style: TextStyle(
                                                    fontSize: 15,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                          SizedBox(width: 8),
                                          ElevatedButton(
                                            onPressed: product.quantity > 0
                                                ? () => _sellProduct(product)
                                                : null,
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor: Colors.green,
                                              foregroundColor: Colors.white,
                                              shape: RoundedRectangleBorder(
                                                borderRadius:
                                                    BorderRadius.circular(20),
                                              ),
                                              padding: EdgeInsets.symmetric(
                                                horizontal: 16,
                                                vertical: 8,
                                              ),
                                              elevation: 3,
                                            ),
                                            child: Row(
                                              mainAxisSize: MainAxisSize.min,
                                              children: [
                                                Icon(Icons.sell, size: 16),
                                                SizedBox(width: 4),
                                                Text(
                                                  'बेचियो',
                                                  style: TextStyle(
                                                    fontSize: 15,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
          // Voice search button (bottom left)
          Align(
            alignment: Alignment.bottomLeft,
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: SizedBox(
                width: 72,
                height: 72,
                child: FloatingActionButton(
                  heroTag: 'voiceFab',
                  backgroundColor: _isListening ? Colors.red : Colors.blueGrey,
                  onPressed: _listenVoice,
                  child: Icon(
                    _isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                    color: Colors.white,
                    size: 40, // bigger icon
                  ),
                  tooltip: "आवाज खोज",
                ),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddProductDialog(),
        backgroundColor: Color(0xFF1E88E5),
        icon: Icon(Icons.add, color: Colors.white),
        label: Text(
          'नयाँ उत्पादन थप्नुहोस्',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        elevation: 8,
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      bottomNavigationBar:
          _buildBottomNavbar(), // <-- Add cool bottom navbar here
    );
  }

  void _showAnalytics() {
    final totalProducts = _products.length;
    final totalStock = _products.fold(
      0,
      (sum, product) => sum + product.quantity,
    );
    final totalValue = _products.fold(
      0.0,
      (sum, product) => sum + (product.quantity * product.price),
    );
    final lowStockItems = _products
        .where((product) => product.quantity <= 2)
        .length;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'पसल विश्लेषण',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildAnalyticsRow('कुल उत्पादन:', totalProducts.toString()),
            _buildAnalyticsRow('कुल स्टक:', totalStock.toString()),
            _buildAnalyticsRow(
              'स्टक मूल्य:',
              'रू ${totalValue.toStringAsFixed(0)}',
            ),
            _buildAnalyticsRow('कम स्टक चेतावनी:', lowStockItems.toString()),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('बन्द गर्नुहोस्'),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyticsRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(value, style: TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
