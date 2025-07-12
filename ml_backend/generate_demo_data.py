#!/usr/bin/env python3
"""
Demo Data Generator for Testing CSV Sync System
This script creates sample Flutter CSV files to test the sync system
"""
import os
import pandas as pd
from datetime import datetime, timedelta
import random

def create_demo_flutter_data():
    """Create demo CSV files in the Flutter app directory"""
    
    # Get Flutter data path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    flutter_dir = os.path.join(os.path.dirname(current_dir), 'meropasalapp')
    
    print(f"Creating demo data in: {flutter_dir}")
    
    # Create sample customers
    customers_data = [
        {
            'customer_id': 101,
            'customer_name': 'Demo Customer 1',
            'gender': 'Male',
            'age': 28,
            'city': 'Kathmandu',
            'preferred_categories': 'Electronics, Food',
            'avg_monthly_spending': 2500.0,
            'visits_per_month': 8
        },
        {
            'customer_id': 102,
            'customer_name': 'Demo Customer 2',
            'gender': 'Female',
            'age': 35,
            'city': 'Pokhara',
            'preferred_categories': 'Clothing, Books',
            'avg_monthly_spending': 1800.0,
            'visits_per_month': 5
        },
        {
            'customer_id': 103,
            'customer_name': 'Demo Customer 3',
            'gender': 'Other',
            'age': 42,
            'city': 'Lalitpur',
            'preferred_categories': 'Home, Garden',
            'avg_monthly_spending': 3200.0,
            'visits_per_month': 12
        }
    ]
    
    # Create sample products
    products_data = [
        {
            'product_id': 201,
            'product_name': 'Demo Smartphone',
            'category': 'Electronics',
            'brand': 'TechBrand',
            'standard_price': 25000.0
        },
        {
            'product_id': 202,
            'product_name': 'Demo T-Shirt',
            'category': 'Clothing',
            'brand': 'FashionBrand',
            'standard_price': 1200.0
        },
        {
            'product_id': 203,
            'product_name': 'Demo Coffee Mug',
            'category': 'Home',
            'brand': 'HomeBrand',
            'standard_price': 450.0
        }
    ]
    
    # Create sample shops
    shops_data = [
        {
            'shop_id': 301,
            'city': 'Kathmandu',
            'district': 'Kathmandu'
        },
        {
            'shop_id': 302,
            'city': 'Pokhara',
            'district': 'Kaski'
        },
        {
            'shop_id': 303,
            'city': 'Lalitpur',
            'district': 'Lalitpur'
        }
    ]
    
    # Create sample transactions
    transactions_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(10):  # Create 10 new transactions
        transaction_id = f"T{2000 + i}"
        customer_id = random.choice([101, 102, 103])
        product_id = random.choice([201, 202, 203])
        shop_id = random.choice([301, 302, 303])
        
        # Get product price
        product = next(p for p in products_data if p['product_id'] == product_id)
        base_price = product['standard_price']
        actual_price = base_price * random.uniform(0.8, 1.2)  # ±20% variation
        
        transaction_date = base_date + timedelta(days=random.randint(0, 30))
        
        transactions_data.append({
            'transaction_id': transaction_id,
            'customer_id': customer_id,
            'product_id': product_id,
            'shop_id': shop_id,
            'quantity': random.randint(1, 3),
            'actual_price': round(actual_price, 2),
            'transaction_date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': random.choice(['Cash', 'Card', 'Digital'])
        })
    
    # Save CSV files
    customers_df = pd.DataFrame(customers_data)
    products_df = pd.DataFrame(products_data)
    shops_df = pd.DataFrame(shops_data)
    transactions_df = pd.DataFrame(transactions_data)
    
    customers_df.to_csv(os.path.join(flutter_dir, 'customers.csv'), index=False)
    products_df.to_csv(os.path.join(flutter_dir, 'products.csv'), index=False)
    shops_df.to_csv(os.path.join(flutter_dir, 'shops.csv'), index=False)
    transactions_df.to_csv(os.path.join(flutter_dir, 'transactions.csv'), index=False)
    
    print(f"✅ Created {len(customers_data)} customers")
    print(f"✅ Created {len(products_data)} products")
    print(f"✅ Created {len(shops_data)} shops")
    print(f"✅ Created {len(transactions_data)} transactions")
    print("\nDemo data created successfully!")
    print("Now you can run: python sync_data.py")

if __name__ == "__main__":
    create_demo_flutter_data()
