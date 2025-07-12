import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QR Code Generator',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const QRGeneratorPage(),
    );
  }
}

class QRGeneratorPage extends StatefulWidget {
  const QRGeneratorPage({super.key});

  @override
  _QRGeneratorPageState createState() => _QRGeneratorPageState();
}

class _QRGeneratorPageState extends State<QRGeneratorPage> {
  final TextEditingController _productNameController = TextEditingController();
  final TextEditingController _quantityController = TextEditingController();
  final TextEditingController _rateController = TextEditingController();
  String _qrData = "";

  @override
  void dispose() {
    _productNameController.dispose();
    _quantityController.dispose();
    _rateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('QR Code Generator')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Column(
              children: [
                TextField(
                  controller: _productNameController,
                  decoration: const InputDecoration(
                    labelText: 'Product Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _quantityController,
                  decoration: const InputDecoration(
                    labelText: 'Quantity',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _rateController,
                  decoration: const InputDecoration(
                    labelText: 'Rate',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _qrData =
                      "Product: ${_productNameController.text}, Quantity: ${_quantityController.text}, Rate: ${_rateController.text}";
                });
              },
              child: const Text('Generate QR Code'),
            ),
            const SizedBox(height: 20),
            if (_qrData.isNotEmpty)
              Expanded(
                // Use Expanded to allow the QR code to take up remaining space
                child: Center(
                  // Center the QR code within the expanded area
                  child: QrImageView(
                    data: _qrData,
                    version: QrVersions.auto,
                    size: 200.0,
                    gapless: false,
                    errorStateBuilder: (cxt, err) {
                      return const Center(
                        child: Text(
                          'Uh oh! Something went wrong...',
                          textAlign: TextAlign.center,
                        ),
                      );
                    },
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
