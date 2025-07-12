import 'package:flutter/material.dart';
import 'map_page.dart';

class LocationSearchModal extends StatefulWidget {
  final String currentLocation;

  const LocationSearchModal({Key? key, required this.currentLocation})
    : super(key: key);

  @override
  State<LocationSearchModal> createState() => _LocationSearchModalState();
}

class _LocationSearchModalState extends State<LocationSearchModal> {
  final TextEditingController searchController = TextEditingController();
  List<String> recentLocations = [
    'Dal Bhat Nepali Kitchen, Kumari Mai Marga, Radisson Hotel Kathmandu, Lazimpath, KTM',
    'Dalima Tours And Travels, Thamel Marg, Thamel, KTM',
    'Dalakshi Marg, Barmutola, KTM',
    'DALIMA INTERNATIONAL PVT.LTD., Campus Gate, Narayangarh, Bharatpur, Chitwan',
    'Dalima Traders Pvt. Ltd., Jorpati Main Road, Magar Gaun, Babar Chowk',
  ];
  List<String> filteredLocations = [];

  @override
  void initState() {
    super.initState();
    searchController.addListener(_filterLocations);
  }

  void _filterLocations() {
    if (searchController.text.isEmpty) {
      setState(() {
        filteredLocations = recentLocations;
      });
      return;
    }

    final query = searchController.text.toLowerCase();
    setState(() {
      filteredLocations = recentLocations
          .where((location) => location.toLowerCase().contains(query))
          .toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Search input
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 24, 16, 16),
            child: Text(
              "Enter your location",
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Color(0xFF111827),
              ),
            ),
          ),

          // Search bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: TextField(
              controller: searchController,
              decoration: InputDecoration(
                hintText: "Search location",
                hintStyle: TextStyle(color: Color(0xFF9CA3AF)),
                prefixIcon: Icon(Icons.location_on, color: Color(0xFF4F46E5)),
                suffixIcon: searchController.text.isNotEmpty
                    ? IconButton(
                        icon: Icon(Icons.close, color: Color(0xFF9CA3AF)),
                        onPressed: () {
                          searchController.clear();
                        },
                      )
                    : null,
                filled: true,
                fillColor: Color(0xFFF3F4F6),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              onSubmitted: (value) {
                if (value.isNotEmpty) {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => MapPage(location: value),
                    ),
                  ).then((result) {
                    if (result != null && result is Map<String, dynamic>) {
                      // Process the returned location data
                    }
                  });
                }
              },
            ),
          ),

          // Current location button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            child: InkWell(
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => MapPage(location: "Current Location"),
                  ),
                ).then((result) {
                  if (result != null && result is Map<String, dynamic>) {
                    // Update with the returned location data
                  }
                });
              },
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  border: Border.all(color: Color(0xFFE5E7EB)),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Icon(Icons.my_location, color: Color(0xFF4F46E5)),
                    SizedBox(width: 12),
                    Text(
                      "Use current location",
                      style: TextStyle(
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF111827),
                      ),
                    ),
                    Spacer(),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 16,
                      color: Color(0xFF9CA3AF),
                    ),
                  ],
                ),
              ),
            ),
          ),

          Divider(height: 1, thickness: 1, color: Color(0xFFE5E7EB)),

          // Recent locations title
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Text(
              "Recent Locations",
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Color(0xFF111827),
              ),
            ),
          ),

          // Location list
          Flexible(
            child: ListView.builder(
              shrinkWrap: true,
              padding: EdgeInsets.zero,
              itemCount: filteredLocations.length,
              itemBuilder: (context, index) {
                return _buildLocationTile(filteredLocations[index]);
              },
            ),
          ),

          // Bottom buttons
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      // Custom address action
                    },
                    icon: Icon(Icons.edit_location_alt),
                    label: Text("Custom Address"),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Color(0xFF4F46E5),
                      side: BorderSide(color: Color(0xFF4F46E5)),
                      padding: EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              MapPage(location: widget.currentLocation),
                        ),
                      ).then((result) {
                        if (result != null && result is Map<String, dynamic>) {
                          // Process the returned location data
                        }
                      });
                    },
                    icon: Icon(Icons.map),
                    label: Text("Set On Map"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color(0xFF4F46E5),
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Bottom safe area for keyboard
          SizedBox(height: MediaQuery.of(context).viewInsets.bottom),
        ],
      ),
    );
  }

  Widget _buildLocationTile(String location) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: Color(0xFFF3F4F6),
        child: Icon(Icons.history, color: Color(0xFF6B7280)),
      ),
      title: Text(
        location,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(fontSize: 14, color: Color(0xFF111827)),
      ),
      trailing: IconButton(
        icon: Icon(Icons.more_vert, color: Color(0xFF6B7280)),
        onPressed: () {},
      ),
      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      onTap: () {
        Navigator.pop(context);
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => MapPage(location: location)),
        ).then((result) {
          if (result != null && result is Map<String, dynamic>) {
            // Process the returned location data
          }
        });
      },
    );
  }

  @override
  void dispose() {
    searchController.removeListener(_filterLocations);
    searchController.dispose();
    super.dispose();
  }
}
