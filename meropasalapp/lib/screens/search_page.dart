import 'package:flutter/material.dart';
import 'location_map_page.dart';

class SearchPage extends StatefulWidget {
  final String category;

  const SearchPage({Key? key, required this.category}) : super(key: key);

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  final TextEditingController _searchController = TextEditingController();
  bool _isSearching = false;
  List<Map<String, dynamic>> _searchResults = [];
  final List<Map<String, dynamic>> _allItems = [
    {
      'name': 'Fresh Tomatoes',
      'price': 'Rs. 120/kg',
      'shop': 'Fresh Mart',
      'rating': 4.5,
      'image': 'https://images.unsplash.com/photo-1546094096-0df4bcaaa337',
      'category': 'Vegetables',
    },
    {
      'name': 'Organic Potatoes',
      'price': 'Rs. 80/kg',
      'shop': 'Organic Corner',
      'rating': 4.2,
      'image': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655',
      'category': 'Vegetables',
    },
    {
      'name': 'Fresh Apples',
      'price': 'Rs. 250/kg',
      'shop': 'Fresh Mart',
      'rating': 4.7,
      'image': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6',
      'category': 'Fruits',
    },
    {
      'name': 'Chicken Breast',
      'price': 'Rs. 450/kg',
      'shop': 'Meat House',
      'rating': 4.3,
      'image': 'https://images.unsplash.com/photo-1604503468506-a8da13d3e804',
      'category': 'Meat',
    },
    {
      'name': 'Whole Wheat Bread',
      'price': 'Rs. 85/piece',
      'shop': 'Bakery Corner',
      'rating': 4.4,
      'image': 'https://images.unsplash.com/photo-1509440159596-0249088772ff',
      'category': 'Bakery',
    },
    {
      'name': 'Fresh Milk',
      'price': 'Rs. 120/liter',
      'shop': 'Dairy Farm',
      'rating': 4.6,
      'image': 'https://images.unsplash.com/photo-1563636619-e9143da7973b',
      'category': 'Dairy',
    },
    {
      'name': 'Local Rice',
      'price': 'Rs. 95/kg',
      'shop': 'Grains Market',
      'rating': 4.1,
      'image': 'https://images.unsplash.com/photo-1586201375761-83865001e31c',
      'category': 'Grocery',
    },
    {
      'name': 'Fresh Orange Juice',
      'price': 'Rs. 150/liter',
      'shop': 'Juice Bar',
      'rating': 4.8,
      'image': 'https://images.unsplash.com/photo-1613478223719-2ab802602423',
      'category': 'Drinks',
    },
    {
      'name': 'Spicy Potato Chips',
      'price': 'Rs. 70/pack',
      'shop': 'Snack Corner',
      'rating': 4.0,
      'image': 'https://images.unsplash.com/photo-1613919113640-25732ec5e61f',
      'category': 'Snacks',
    },
  ];

  @override
  void initState() {
    super.initState();
    _filterItemsByCategory();
  }

  void _filterItemsByCategory() {
    if (widget.category.toLowerCase() == 'all') {
      _searchResults = List.from(_allItems);
    } else {
      _searchResults = _allItems
          .where(
            (item) =>
                item['category'].toLowerCase() == widget.category.toLowerCase(),
          )
          .toList();
    }
  }

  void _performSearch(String query) {
    if (query.isEmpty) {
      _filterItemsByCategory();
    } else {
      final filteredResults = _allItems.where((item) {
        final nameMatch = item['name'].toLowerCase().contains(
          query.toLowerCase(),
        );
        final shopMatch = item['shop'].toLowerCase().contains(
          query.toLowerCase(),
        );
        final categoryMatch = item['category'].toLowerCase().contains(
          query.toLowerCase(),
        );
        final categoryFilterMatch =
            widget.category.toLowerCase() == 'all' ||
            item['category'].toLowerCase() == widget.category.toLowerCase();

        return (nameMatch || shopMatch || categoryMatch) && categoryFilterMatch;
      }).toList();

      setState(() {
        _searchResults = filteredResults;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Color(0xFF4F46E5),
        elevation: 0,
        title: _isSearching
            ? TextField(
                controller: _searchController,
                style: TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Search ${widget.category}...',
                  hintStyle: TextStyle(color: Colors.white70),
                  border: InputBorder.none,
                ),
                onChanged: _performSearch,
                autofocus: true,
              )
            : Text(
                widget.category,
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
        iconTheme: IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: Icon(_isSearching ? Icons.close : Icons.search),
            onPressed: () {
              setState(() {
                if (_isSearching) {
                  _isSearching = false;
                  _searchController.clear();
                  _filterItemsByCategory();
                } else {
                  _isSearching = true;
                }
              });
            },
          ),
          IconButton(
            icon: Icon(Icons.filter_list),
            onPressed: () {
              // Show filter options
              _showFilterOptions(context);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Search results count
          Container(
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            color: Colors.white,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${_searchResults.length} items found',
                  style: TextStyle(
                    color: Color(0xFF6B7280),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Row(
                  children: [
                    Text(
                      'Sort by:',
                      style: TextStyle(color: Color(0xFF6B7280)),
                    ),
                    SizedBox(width: 4),
                    DropdownButton<String>(
                      value: 'Popularity',
                      underline: Container(),
                      icon: Icon(
                        Icons.arrow_drop_down,
                        color: Color(0xFF4F46E5),
                      ),
                      items:
                          [
                            'Popularity',
                            'Price: Low to High',
                            'Price: High to Low',
                            'Rating',
                          ].map<DropdownMenuItem<String>>((String value) {
                            return DropdownMenuItem<String>(
                              value: value,
                              child: Text(
                                value,
                                style: TextStyle(
                                  color: Color(0xFF111827),
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            );
                          }).toList(),
                      onChanged: (String? newValue) {
                        // Implement sorting logic
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Search results list
          Expanded(
            child: _searchResults.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.search_off, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text(
                          'No items found',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                            color: Colors.grey,
                          ),
                        ),
                        SizedBox(height: 8),
                        Text(
                          'Try different search terms',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: EdgeInsets.all(16),
                    itemCount: _searchResults.length,
                    itemBuilder: (context, index) {
                      final item = _searchResults[index];
                      return _buildItemCard(item);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildItemCard(Map<String, dynamic> item) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Color(0xFFE5E7EB)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Item image
          Container(
            height: 180,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
              image: DecorationImage(
                image: NetworkImage('${item['image']}?w=500&q=80'),
                fit: BoxFit.cover,
              ),
            ),
          ),

          // Item details
          Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      item['name'],
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF111827),
                      ),
                    ),
                    Text(
                      item['price'],
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF4F46E5),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.store, size: 16, color: Color(0xFF6B7280)),
                    SizedBox(width: 4),
                    Text(
                      item['shop'],
                      style: TextStyle(color: Color(0xFF6B7280)),
                    ),
                    SizedBox(width: 12),
                    Icon(Icons.star, size: 16, color: Colors.amber),
                    SizedBox(width: 4),
                    Text(
                      item['rating'].toString(),
                      style: TextStyle(color: Color(0xFF6B7280)),
                    ),
                  ],
                ),
                SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () {
                          // Navigate to location page to see nearby shops
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => LocationMapPage(
                                itemName: item['name'],
                                shopName: item['shop'],
                                itemCategory: item['category'],
                              ),
                            ),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Color(0xFF4F46E5),
                          foregroundColor: Colors.white,
                          padding: EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: Text('Find Nearby Shops'),
                      ),
                    ),
                    SizedBox(width: 12),
                    IconButton(
                      onPressed: () {
                        // Favorite logic
                      },
                      icon: Icon(Icons.favorite_border),
                      style: IconButton.styleFrom(
                        backgroundColor: Colors.grey[100],
                        foregroundColor: Colors.grey[700],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showFilterOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Padding(
              padding: EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Filter Options',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF111827),
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            Divider(height: 1, thickness: 1, color: Color(0xFFE5E7EB)),

            // Filter options
            Expanded(
              child: ListView(
                padding: EdgeInsets.all(16),
                children: [
                  _buildFilterSection('Categories', [
                    'All',
                    'Vegetables',
                    'Fruits',
                    'Meat',
                    'Dairy',
                    'Bakery',
                    'Grocery',
                    'Drinks',
                    'Snacks',
                  ]),
                  _buildFilterSection('Shop', [
                    'All Shops',
                    'Fresh Mart',
                    'Organic Corner',
                    'Meat House',
                    'Bakery Corner',
                    'Dairy Farm',
                    'Grains Market',
                    'Juice Bar',
                    'Snack Corner',
                  ]),
                  _buildFilterSection('Rating', [
                    'Any',
                    '4★ & above',
                    '3★ & above',
                  ]),
                  _buildPriceRangeFilter(),
                ],
              ),
            ),

            // Apply button
            Padding(
              padding: EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    // Apply filters
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFF4F46E5),
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    'Apply Filters',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterSection(String title, List<String> options) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF111827),
          ),
        ),
        SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: options.map((option) {
            final isSelected =
                option == 'All' ||
                (title == 'Categories' &&
                    option.toLowerCase() == widget.category.toLowerCase());
            return FilterChip(
              label: Text(option),
              selected: isSelected,
              onSelected: (selected) {
                // Apply filter logic
              },
              backgroundColor: Colors.white,
              selectedColor: Color(0xFFE0E7FF),
              checkmarkColor: Color(0xFF4F46E5),
              labelStyle: TextStyle(
                color: isSelected ? Color(0xFF4F46E5) : Color(0xFF6B7280),
                fontWeight: isSelected ? FontWeight.w500 : FontWeight.normal,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
                side: BorderSide(
                  color: isSelected ? Color(0xFF4F46E5) : Color(0xFFD1D5DB),
                ),
              ),
            );
          }).toList(),
        ),
        SizedBox(height: 24),
      ],
    );
  }

  Widget _buildPriceRangeFilter() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Price Range',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF111827),
          ),
        ),
        SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                decoration: InputDecoration(
                  labelText: 'Min',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 12,
                  ),
                ),
                keyboardType: TextInputType.number,
              ),
            ),
            SizedBox(width: 16),
            Expanded(
              child: TextFormField(
                decoration: InputDecoration(
                  labelText: 'Max',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 12,
                  ),
                ),
                keyboardType: TextInputType.number,
              ),
            ),
          ],
        ),
        SizedBox(height: 24),
      ],
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
}
