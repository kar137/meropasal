// user_profile.dart

import 'package:flutter/material.dart';
import 'user.dart';
import '../kyc_verification.dart';

class UserProfileScreen extends StatelessWidget {
  final User user;

  const UserProfileScreen({super.key, required this.user});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(user.shopName),
        backgroundColor: theme.colorScheme.primaryContainer,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            CircleAvatar(
              radius: 60,
              backgroundImage: user.profileImageUrl.isNotEmpty
                  ? NetworkImage(user.profileImageUrl)
                  : null,
              child: user.profileImageUrl.isEmpty
                  ? const Icon(Icons.person, size: 60)
                  : null,
            ),
            const SizedBox(height: 20),
            Text(
              user.name,
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              user.description,
              style: theme.textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ListTile(
              leading: const Icon(Icons.store),
              title: Text(user.shopName),
            ),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: Text(user.location),
            ),
            ListTile(
              leading: const Icon(Icons.phone),
              title: Text(user.contact),
            ),
            ListTile(leading: const Icon(Icons.email), title: Text(user.email)),
            ListTile(leading: const Icon(Icons.web), title: Text(user.website)),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const KycVerificationPage(),
                  ),
                );
              },
              icon: const Icon(Icons.verified_user),
              label: const Text("Complete KYC Verification"),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
