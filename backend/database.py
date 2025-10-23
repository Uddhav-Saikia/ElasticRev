"""
Database initialization and utility functions
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from models import db, Product, Sale, PriceHistory, ElasticityResult, Scenario, CompetitorPrice
from config import SQLALCHEMY_DATABASE_URI, DATABASE_PATH
import pandas as pd
from datetime import datetime


def init_database(app=None):
    """Initialize database and create tables"""
    if app is None:
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
    
    with app.app_context():
        # Drop all tables and recreate (for development)
        print("🗄️  Resetting database...")
        db.drop_all()
        print("🗄️  Creating database schema...")
        db.create_all()
        print("✓ Database tables created")
        
        return app


def load_data_from_csv(app):
    """Load data from CSV files into database"""
    with app.app_context():
        data_dir = Path(__file__).resolve().parent.parent / 'data'
        
        # Check if data files exist
        products_file = data_dir / 'products.csv'
        sales_file = data_dir / 'sales_data.csv'
        competitors_file = data_dir / 'competitors.csv'
        
        if not products_file.exists():
            print("⚠️  Data files not found. Run generate_data.py first.")
            return
        
        # Load products
        print("📦 Loading products...")
        products_df = pd.read_csv(products_file)
        
        for _, row in products_df.iterrows():
            product = Product(
                sku=row['sku'],
                name=row['name'],
                category=row['category'],
                subcategory=row['subcategory'],
                brand=row['brand'],
                unit_cost=row['unit_cost'],
                current_price=row['current_price'],
                currency=row['currency']
            )
            db.session.add(product)
        
        db.session.commit()
        print(f"✓ Loaded {len(products_df)} products")
        
        # Load sales
        if sales_file.exists():
            print("💰 Loading sales data...")
            sales_df = pd.read_csv(sales_file)
            
            # Convert date column
            sales_df['date'] = pd.to_datetime(sales_df['date']).dt.date
            
            batch_size = 1000
            for i in range(0, len(sales_df), batch_size):
                batch = sales_df.iloc[i:i+batch_size]
                
                for _, row in batch.iterrows():
                    sale = Sale(
                        product_id=row['product_id'],
                        date=row['date'],
                        quantity=row['quantity'],
                        price=row['price'],
                        revenue=row['revenue'],
                        cost=row['cost'],
                        profit=row['profit'],
                        discount_percent=row['discount_percent'],
                        competitor_price=row['competitor_price'],
                        season=row['season'],
                        day_of_week=row['day_of_week'],
                        is_holiday=row['is_holiday'],
                        promotion_active=row['promotion_active']
                    )
                    db.session.add(sale)
                
                db.session.commit()
                print(f"   Loaded {min(i+batch_size, len(sales_df))}/{len(sales_df)} sales...")
            
            print(f"✓ Loaded {len(sales_df):,} sales transactions")
        
        # Load competitor data
        if competitors_file.exists():
            print("🏪 Loading competitor data...")
            competitors_df = pd.read_csv(competitors_file)
            
            competitors_df['date'] = pd.to_datetime(competitors_df['date']).dt.date
            
            batch_size = 1000
            for i in range(0, len(competitors_df), batch_size):
                batch = competitors_df.iloc[i:i+batch_size]
                
                for _, row in batch.iterrows():
                    comp_price = CompetitorPrice(
                        product_id=row['product_id'],
                        competitor_name=row['competitor_name'],
                        competitor_price=row['competitor_price'],
                        date=row['date'],
                        url=row.get('url', '')
                    )
                    db.session.add(comp_price)
                
                db.session.commit()
                print(f"   Loaded {min(i+batch_size, len(competitors_df))}/{len(competitors_df)} competitor prices...")
            
            print(f"✓ Loaded {len(competitors_df):,} competitor price points")
        
        print("\n✨ Database initialization complete!")


def reset_database(app):
    """Reset database (drop and recreate all tables)"""
    with app.app_context():
        print("⚠️  Resetting database...")
        db.drop_all()
        db.create_all()
        print("✓ Database reset complete")


if __name__ == '__main__':
    print("=" * 60)
    print("ElasticRev - Database Initialization")
    print("=" * 60)
    print()
    
    # Initialize database
    app = init_database()
    
    # Load data from CSV
    load_data_from_csv(app)
    
    # Print summary
    with app.app_context():
        product_count = Product.query.count()
        sales_count = Sale.query.count()
        competitor_count = CompetitorPrice.query.count()
        
        print("\n" + "=" * 60)
        print("Database Summary")
        print("=" * 60)
        print(f"Products: {product_count}")
        print(f"Sales Transactions: {sales_count:,}")
        print(f"Competitor Prices: {competitor_count:,}")
        print(f"Database Location: {DATABASE_PATH}")
        print("=" * 60)
