#!/usr/bin/env python3
"""
Quick setup script for local development
Tests the database initialization and data loading
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, initialize_database
from models import Product, Sale, db

def test_setup():
    """Test database initialization"""
    print("=" * 60)
    print("🧪 ElasticRev - Local Setup Test")
    print("=" * 60)
    print()
    
    # Initialize database
    print("1️⃣  Initializing database...")
    with app.app_context():
        initialize_database()
        print("   ✓ Database initialized")
        print()
        
        # Check data
        product_count = Product.query.count()
        sales_count = Sale.query.count()
        
        print("2️⃣  Checking data...")
        print(f"   Products: {product_count}")
        print(f"   Sales Transactions: {sales_count:,}")
        print()
        
        if product_count > 0 and sales_count > 0:
            print("✅ Setup successful! All data loaded.")
            print()
            print("Next steps:")
            print("  1. Backend: python app.py")
            print("  2. Frontend: npm run dev")
            print("  3. Open: http://localhost:3000")
            return True
        else:
            print("❌ Setup failed! No data found.")
            return False

if __name__ == '__main__':
    success = test_setup()
    sys.exit(0 if success else 1)

