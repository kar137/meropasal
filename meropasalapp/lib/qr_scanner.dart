import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class QrScannerPage extends StatefulWidget {
  @override
  _QrScannerPageState createState() => _QrScannerPageState();
}

class _QrScannerPageState extends State<QrScannerPage> {
  MobileScannerController cameraController = MobileScannerController();
  bool isFlashOn = false;
  bool isFrontCamera = false;

  @override
  void dispose() {
    cameraController.dispose();
    super.dispose();
  }

  void _showScanSuccessDialog(String barcode) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Center(
            child: Icon(Icons.check_circle, color: Colors.green, size: 48.0),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              const Text(
                "स्क्यान सफल भयो!",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10.0),
              Text(
                "स्क्यान गरिएको डाटा: $barcode",
                textAlign: TextAlign.center,
              ),
            ],
          ),
          actions: <Widget>[
            TextButton(
              child: const Text("ठीक छ"),
              onPressed: () {
                Navigator.of(context).pop();
                cameraController.stop();
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  void _toggleFlash() async {
    await cameraController.toggleTorch();
    setState(() {
      isFlashOn = !isFlashOn;
    });
  }

  void _switchCamera() async {
    await cameraController.switchCamera();
    setState(() {
      isFrontCamera = !isFrontCamera;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('QR स्क्यानर'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: Stack(
        children: <Widget>[
          MobileScanner(
            controller: cameraController,
            onDetect: (capture) {
              final List<Barcode> barcodes = capture.barcodes;
              if (barcodes.isNotEmpty) {
                final String barcode =
                    barcodes.first.rawValue ?? "कुनै डाटा फेला परेन";
                _showScanSuccessDialog(barcode);
              }
            },
          ),
          // Overlay with scanning frame
          Center(
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.blue, width: 2),
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          // Instructions
          Positioned(
            top: 100,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.7),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'QR कोडलाई फ्रेम भित्र राख्नुहोस्',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),
          ),
          // Controls at bottom
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              padding: const EdgeInsets.all(16.0),
              color: Colors.black.withOpacity(0.7),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  IconButton(
                    color: Colors.white,
                    icon: Icon(
                      isFlashOn ? Icons.flash_on : Icons.flash_off,
                      color: isFlashOn ? Colors.yellow : Colors.grey,
                    ),
                    iconSize: 32.0,
                    onPressed: _toggleFlash,
                  ),
                  IconButton(
                    color: Colors.white,
                    icon: Icon(
                      isFrontCamera ? Icons.camera_front : Icons.camera_rear,
                      color: Colors.white,
                    ),
                    iconSize: 32.0,
                    onPressed: _switchCamera,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
