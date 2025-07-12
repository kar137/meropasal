import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class KycVerificationPage extends StatefulWidget {
  final Function(bool)? onDocumentsUploaded;

  const KycVerificationPage({Key? key, this.onDocumentsUploaded})
    : super(key: key);

  @override
  State<KycVerificationPage> createState() => _KycVerificationPageState();
}

class _KycVerificationPageState extends State<KycVerificationPage> {
  final _formKey = GlobalKey<FormState>();
  final _shopNameController = TextEditingController();
  final _ownerNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();

  File? _identityDocument;
  File? _businessProof;
  File? _shopPhoto;

  final _imagePicker = ImagePicker();

  Future<void> _pickImage(ImageSource source, String type) async {
    try {
      final pickedFile = await _imagePicker.pickImage(
        source: source,
        imageQuality: 80,
      );

      if (pickedFile != null) {
        setState(() {
          if (type == 'identity') {
            _identityDocument = File(pickedFile.path);
          } else if (type == 'business') {
            _businessProof = File(pickedFile.path);
          } else if (type == 'shop') {
            _shopPhoto = File(pickedFile.path);
          }
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error selecting image: $e')));
    }
  }

  void _showImageSourceDialog(String type) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Image Source'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Camera'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera, type);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Gallery'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery, type);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImageUploadCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required File? imageFile,
    required Function() onTap,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: imageFile != null ? Color(0xFF10B981) : Color(0xFFE5E7EB),
          width: 1,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              if (imageFile == null) ...[
                Container(
                  height: 80,
                  width: 80,
                  decoration: BoxDecoration(
                    color: Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, size: 40, color: Color(0xFF6B7280)),
                ),
              ] else ...[
                Container(
                  height: 120,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    image: DecorationImage(
                      image: FileImage(imageFile),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 12),
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF111827),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: Color(0xFF6B7280)),
              ),
              const SizedBox(height: 8),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: imageFile != null
                      ? Color(0xFFD1FAE5)
                      : Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  imageFile != null ? 'Selected' : 'Upload',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: imageFile != null
                        ? Color(0xFF047857)
                        : Color(0xFF6B7280),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _submitKyc() {
    if (_formKey.currentState!.validate()) {
      if (_identityDocument == null ||
          _businessProof == null ||
          _shopPhoto == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please upload all required documents'),
            backgroundColor: Color(0xFFEF4444),
          ),
        );
        return;
      }

      // Show loading dialog
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => const Center(
          child: CircularProgressIndicator(color: Color(0xFF4F46E5)),
        ),
      );

      // Simulate API call
      Future.delayed(const Duration(seconds: 2), () {
        Navigator.pop(context); // Close loading dialog

        // Show success dialog
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            title: const Text(
              "KYC Submitted",
              style: TextStyle(
                color: Color(0xFF10B981),
                fontWeight: FontWeight.w600,
              ),
            ),
            content: const Text(
              "Your KYC documents have been submitted for verification. We'll notify you once the verification is complete.",
              style: TextStyle(color: Color(0xFF111827)),
            ),
            actions: [
              ElevatedButton(
                onPressed: () {
                  // Call the callback to notify that documents were uploaded
                  if (widget.onDocumentsUploaded != null) {
                    widget.onDocumentsUploaded!(true);
                  }

                  Navigator.pop(context);
                  Navigator.pop(context); // Return to shop home page
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text("OK"),
              ),
            ],
          ),
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("KYC Verification"),
        backgroundColor: const Color(0xFF4F46E5),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Info card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, color: Color(0xFF3B82F6)),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        "Complete KYC verification to start selling on our platform. This helps us ensure the authenticity of businesses.",
                        style: TextStyle(color: Color(0xFF1E3A8A), height: 1.5),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Basic information section
              const Text(
                "Basic Information",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF111827),
                ),
              ),
              const SizedBox(height: 16),

              // Shop name
              TextFormField(
                controller: _shopNameController,
                decoration: InputDecoration(
                  labelText: "Shop Name",
                  hintText: "Enter your shop name",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: Icon(Icons.storefront),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return "Shop name is required";
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Owner name
              TextFormField(
                controller: _ownerNameController,
                decoration: InputDecoration(
                  labelText: "Owner Name",
                  hintText: "Enter owner's full name",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: Icon(Icons.person),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return "Owner name is required";
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Phone number
              TextFormField(
                controller: _phoneController,
                decoration: InputDecoration(
                  labelText: "Phone Number",
                  hintText: "Enter business phone number",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: Icon(Icons.phone),
                ),
                keyboardType: TextInputType.phone,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return "Phone number is required";
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Address
              TextFormField(
                controller: _addressController,
                decoration: InputDecoration(
                  labelText: "Business Address",
                  hintText: "Enter your business address",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  prefixIcon: Icon(Icons.location_on),
                ),
                maxLines: 2,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return "Business address is required";
                  }
                  return null;
                },
              ),

              const SizedBox(height: 32),

              // Document upload section
              const Text(
                "Document Upload",
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF111827),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                "Please upload clear photos of the following documents",
                style: TextStyle(color: Color(0xFF6B7280)),
              ),
              const SizedBox(height: 16),

              // Document upload cards
              _buildImageUploadCard(
                title: "Identity Document",
                subtitle: "Citizenship, License or Passport",
                icon: Icons.assignment_ind,
                imageFile: _identityDocument,
                onTap: () => _showImageSourceDialog('identity'),
              ),
              const SizedBox(height: 16),

              _buildImageUploadCard(
                title: "Business Registration",
                subtitle: "PAN, VAT, or Business Registration Certificate",
                icon: Icons.business,
                imageFile: _businessProof,
                onTap: () => _showImageSourceDialog('business'),
              ),
              const SizedBox(height: 16),

              _buildImageUploadCard(
                title: "Shop Photo",
                subtitle: "Clear photo of your shop front",
                icon: Icons.storefront,
                imageFile: _shopPhoto,
                onTap: () => _showImageSourceDialog('shop'),
              ),

              const SizedBox(height: 32),

              // Submit button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _submitKyc,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF4F46E5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    "Submit KYC Documents",
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                  ),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _shopNameController.dispose();
    _ownerNameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    super.dispose();
  }
}
