import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

import 'user.dart';
import 'user_profile.dart';

void main() => runApp(const PasaleApp());

class PasaleApp extends StatefulWidget {
  const PasaleApp({super.key});
  @override
  State<PasaleApp> createState() => _PasaleAppState();
}

class _PasaleAppState extends State<PasaleApp> {
  bool isDark = false;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pasale',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        colorSchemeSeed: Colors.deepPurple,
        useMaterial3: true,
        fontFamily: 'Poppins',
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        colorSchemeSeed: Colors.deepPurple,
        useMaterial3: true,
        fontFamily: 'Poppins',
      ),
      themeMode: isDark ? ThemeMode.dark : ThemeMode.light,
      home: HomeScreen(
        isDark: isDark,
        onThemeSwitch: () => setState(() => isDark = !isDark),
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  final bool isDark;
  final VoidCallback onThemeSwitch;
  const HomeScreen({
    super.key,
    required this.isDark,
    required this.onThemeSwitch,
  });
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String selectedAction = 'किन्यो';
  int quantity = 1;
  int selectedCategoryIdx = 0;
  List<CategoryCard> categories = [
    CategoryCard(name: 'चामल', icon: Icons.rice_bowl, color: Colors.amber),
    CategoryCard(name: 'दाल', icon: Icons.soup_kitchen, color: Colors.orange),
    CategoryCard(name: 'तेल', icon: Icons.oil_barrel, color: Colors.yellow),
    CategoryCard(name: 'नुन', icon: Icons.spa, color: Colors.blue),
  ];
  List<ActionHistory> history = [];

  late stt.SpeechToText _speech;
  bool _isListening = false;
  String _voiceInput = '';

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
  }

  /// ✅ Step 1: Start listening when mic button pressed
  void _startListening() async {
    bool available = await _speech.initialize(
      onStatus: (status) {
        print('Speech status: $status');
        if (status == 'done' || status == 'notListening') {
          setState(() => _isListening = false);
        }
      },
      onError: (error) {
        print('Speech error: $error');
        setState(() => _isListening = false);
      },
    );

    if (available) {
      setState(() => _isListening = true);
      _speech.listen(
        onResult: (result) {
          if (result.finalResult) {
            _handleVoiceInput(result.recognizedWords);
          }
        },
        pauseFor: Duration(seconds: 2),
        listenFor: Duration(seconds: 5),
        partialResults: false,
        cancelOnError: true,
      );
    } else {
      print('Speech Recognition unavailable');
    }
  }

  /// ✅ Optional: Stop listening manually
  void _stopListening() async {
    await _speech.stop();
    setState(() => _isListening = false);
  }

  void _handleVoiceInput(String input) {
    String action = selectedAction;
    int qty = quantity;
    int catIdx = selectedCategoryIdx;
    final buyWords = ['किन्यो', 'किन्न', 'buy'];
    final sellWords = ['बेच्यो', 'बेच्न', 'sell'];
    final numbers = RegExp(r'\d+');

    if (buyWords.any((w) => input.contains(w))) action = 'किन्यो';
    if (sellWords.any((w) => input.contains(w))) action = 'बेच्यो';
    final numberMatch = numbers.firstMatch(input);
    if (numberMatch != null) qty = int.parse(numberMatch.group(0)!);

    for (var i = 0; i < categories.length; i++) {
      if (input.contains(categories[i].name)) {
        catIdx = i;
        break;
      }
    }

    if (!categories.any((c) => input.contains(c.name)) &&
        input.trim().isNotEmpty) {
      setState(() {
        categories.add(
          CategoryCard(
            name: input.trim(),
            icon: Icons.category,
            color: Colors.purple,
          ),
        );
        catIdx = categories.length - 1;
      });
    }

    setState(() {
      selectedAction = action;
      quantity = qty;
      selectedCategoryIdx = catIdx;
      _voiceInput = input;
    });

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text("🎤 पहिचान: $input")));
  }

  void _handleConfirm() {
    if (categories.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Category थप्नुहोस्!")));
      return;
    }

    setState(() {
      history.insert(
        0,
        ActionHistory(
          action: selectedAction,
          category: categories[selectedCategoryIdx].name,
          quantity: quantity,
          date: DateTime.now(),
          color: categories[selectedCategoryIdx].color,
          icon: categories[selectedCategoryIdx].icon,
        ),
      );
      quantity = 1;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '✅ $selectedAction: ${categories[selectedCategoryIdx].name} - Qty: $quantity',
        ),
        duration: const Duration(seconds: 2),
        action: SnackBarAction(
          label: "Undo",
          onPressed: () {
            setState(() {
              history.removeAt(0);
            });
          },
        ),
      ),
    );

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => UserProfileScreen(
          user: User(
            id: 'user123',
            name: 'Diya Shakya',
            shopName: 'Pasale Store',
            location: 'Kathmandu, Nepal',
            contact: '+977-9800000000',
            email: 'diya@example.com',
            website: 'https://pasalestore.com',
            description:
                'Welcome to Pasale Store, your trusted shop in Kathmandu.',
            profileImageUrl: '',
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final color = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: color.primaryContainer,
        elevation: 0,
        title: Row(
          children: [
            const Icon(Icons.storefront, size: 32),
            const SizedBox(width: 10),
            Text(
              "Pasale",
              style: Theme.of(
                context,
              ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: AnimatedSwitcher(
              duration: const Duration(milliseconds: 400),
              child: widget.isDark
                  ? Icon(
                      Icons.light_mode,
                      key: const ValueKey('light'),
                      color: Colors.yellow,
                    )
                  : Icon(
                      Icons.dark_mode,
                      key: const ValueKey('dark'),
                      color: Colors.deepPurple,
                    ),
            ),
            onPressed: widget.onThemeSwitch,
            tooltip: "Switch Theme",
          ),
        ],
      ),
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 16),

              // Quantity Selector
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(
                    icon: const Icon(Icons.remove_circle_outline),
                    iconSize: 36,
                    onPressed: () => setState(() {
                      if (quantity > 1) quantity--;
                    }),
                  ),
                  const SizedBox(width: 20),
                  Text(
                    quantity.toString(),
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(width: 20),
                  IconButton(
                    icon: const Icon(Icons.add_circle_outline),
                    iconSize: 36,
                    onPressed: () => setState(() {
                      quantity++;
                    }),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // ✅ Mic Button
              Center(
                child: ElevatedButton.icon(
                  icon: Icon(_isListening ? Icons.mic_off : Icons.mic),
                  label: Text(
                    _isListening ? 'Stop Listening' : 'Start Voice Input',
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(180, 50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: _isListening ? _stopListening : _startListening,
                ),
              ),

              const SizedBox(height: 16),

              Center(
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.check),
                  label: const Text('Confirm'),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(160, 52),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onPressed: _handleConfirm,
                ),
              ),

              const SizedBox(height: 30),

              if (history.isNotEmpty)
                Text("इतिहास", style: Theme.of(context).textTheme.titleLarge),
              ...history.map(
                (h) => ListTile(
                  leading: Icon(h.icon, color: h.color),
                  title: Text('${h.action} ${h.category}'),
                  trailing: Text('Qty: ${h.quantity}'),
                  subtitle: Text(h.date.toLocal().toString().split(' ')[0]),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class CategoryCard {
  final String name;
  final IconData icon;
  final Color color;

  CategoryCard({required this.name, required this.icon, required this.color});
}

class ActionHistory {
  final String action;
  final String category;
  final int quantity;
  final DateTime date;
  final Color color;
  final IconData icon;

  ActionHistory({
    required this.action,
    required this.category,
    required this.quantity,
    required this.date,
    required this.color,
    required this.icon,
  });
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final Color selectedColor;
  final VoidCallback onTap;

  const _ActionButton({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.selectedColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final textColor = isSelected ? Colors.white : Colors.black87;
    final bgColor = isSelected ? selectedColor : Colors.transparent;
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: selectedColor),
        ),
        child: Row(
          children: [
            Icon(icon, color: textColor),
            const SizedBox(width: 10),
            Text(
              label,
              style: TextStyle(color: textColor, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
