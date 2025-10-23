"""
Generate realistic synthetic sales data for Dynamic Pricing Optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)
NUM_PRODUCTS = 50

# Product categories and their characteristics
CATEGORIES = {
    'Electronics': {
        'subcategories': ['Smartphones', 'Laptops', 'Headphones', 'Tablets', 'Smartwatches'],
        'price_range': (50, 2000),
        'cost_margin': 0.35,  # 35% margin
        'elasticity_range': (-1.8, -0.8),  # More elastic
        'base_demand': (50, 200),
        'seasonality': {'Winter': 1.3, 'Spring': 0.9, 'Summer': 0.8, 'Fall': 1.4}
    },
    'Clothing': {
        'subcategories': ['Shirts', 'Pants', 'Dresses', 'Jackets', 'Shoes'],
        'price_range': (20, 200),
        'cost_margin': 0.50,
        'elasticity_range': (-2.5, -1.2),  # Highly elastic
        'base_demand': (100, 300),
        'seasonality': {'Winter': 1.2, 'Spring': 1.1, 'Summer': 0.7, 'Fall': 1.3}
    },
    'Home & Kitchen': {
        'subcategories': ['Cookware', 'Furniture', 'Décor', 'Appliances', 'Bedding'],
        'price_range': (30, 500),
        'cost_margin': 0.45,
        'elasticity_range': (-1.5, -0.9),
        'base_demand': (80, 250),
        'seasonality': {'Winter': 1.0, 'Spring': 1.2, 'Summer': 0.9, 'Fall': 1.0}
    },
    'Groceries': {
        'subcategories': ['Dairy', 'Snacks', 'Beverages', 'Frozen', 'Bakery'],
        'price_range': (2, 50),
        'cost_margin': 0.25,
        'elasticity_range': (-0.8, -0.3),  # Inelastic
        'base_demand': (200, 500),
        'seasonality': {'Winter': 1.0, 'Spring': 1.0, 'Summer': 1.1, 'Fall': 1.0}
    },
    'Beauty & Personal Care': {
        'subcategories': ['Skincare', 'Makeup', 'Haircare', 'Fragrances', 'Bath'],
        'price_range': (10, 150),
        'cost_margin': 0.55,
        'elasticity_range': (-1.3, -0.7),
        'base_demand': (60, 180),
        'seasonality': {'Winter': 1.1, 'Spring': 1.0, 'Summer': 0.9, 'Fall': 1.1}
    },
    'Sports & Outdoors': {
        'subcategories': ['Fitness', 'Camping', 'Cycling', 'Sports Equipment', 'Outdoor Clothing'],
        'price_range': (25, 400),
        'cost_margin': 0.40,
        'elasticity_range': (-1.6, -0.9),
        'base_demand': (70, 220),
        'seasonality': {'Winter': 0.8, 'Spring': 1.2, 'Summer': 1.4, 'Fall': 1.0}
    }
}

BRANDS = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE', 'Premium', 'Value', 'Elite']

COMPETITORS = ['CompetitorX', 'CompetitorY', 'CompetitorZ', 'MarketLeader']


def get_season(date):
    """Determine season from date"""
    month = date.month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'


def is_holiday(date):
    """Check if date is a major holiday"""
    holidays = [
        (1, 1),   # New Year
        (2, 14),  # Valentine's
        (7, 4),   # July 4th
        (10, 31), # Halloween
        (11, 24), # Thanksgiving (approx)
        (12, 25), # Christmas
        (11, 25), # Black Friday
        (12, 26)  # Boxing Day
    ]
    return (date.month, date.day) in holidays


def generate_products():
    """Generate product catalog"""
    products = []
    
    for i in range(NUM_PRODUCTS):
        category = random.choice(list(CATEGORIES.keys()))
        cat_data = CATEGORIES[category]
        
        subcategory = random.choice(cat_data['subcategories'])
        brand = random.choice(BRANDS)
        
        # Generate price
        base_price = random.uniform(*cat_data['price_range'])
        unit_cost = base_price * (1 - cat_data['cost_margin'])
        
        # Price elasticity (true elasticity for simulation)
        elasticity = random.uniform(*cat_data['elasticity_range'])
        
        # Base demand
        base_demand = random.uniform(*cat_data['base_demand'])
        
        products.append({
            'sku': f'SKU{i+1:04d}',
            'name': f'{brand} {subcategory} {i+1}',
            'category': category,
            'subcategory': subcategory,
            'brand': brand,
            'unit_cost': round(unit_cost, 2),
            'current_price': round(base_price, 2),
            'true_elasticity': elasticity,  # For simulation only
            'base_demand': base_demand,     # For simulation only
            'currency': 'USD'
        })
    
    return pd.DataFrame(products)


def generate_sales_data(products_df):
    """Generate historical sales data"""
    sales_data = []
    
    date_range = pd.date_range(START_DATE, END_DATE, freq='D')
    
    for _, product in products_df.iterrows():
        product_id = _ + 1
        category = product['category']
        cat_data = CATEGORIES[category]
        
        base_price = product['current_price']
        unit_cost = product['unit_cost']
        elasticity = product['true_elasticity']
        base_demand = product['base_demand']
        
        for date in date_range:
            # Seasonal adjustment
            season = get_season(date)
            seasonal_factor = cat_data['seasonality'][season]
            
            # Day of week effect (weekends have higher sales)
            day_of_week = date.strftime('%A')
            weekend_factor = 1.2 if day_of_week in ['Saturday', 'Sunday'] else 1.0
            
            # Holiday effect
            holiday = is_holiday(date)
            holiday_factor = 1.3 if holiday else 1.0
            
            # Random promotion (10% chance)
            promotion = random.random() < 0.1
            promotion_factor = 1.4 if promotion else 1.0
            
            # Price variation (±10% from base price)
            price_variation = random.uniform(0.9, 1.1)
            price = base_price * price_variation
            
            # Discount for promotions
            discount_percent = 0
            if promotion:
                discount_percent = random.uniform(10, 25)
                price = price * (1 - discount_percent / 100)
            
            # Calculate demand using elasticity
            # Q = Q0 * (P / P0) ^ elasticity
            price_ratio = price / base_price
            quantity_factor = price_ratio ** elasticity
            
            # Combine all factors
            expected_quantity = (base_demand * seasonal_factor * weekend_factor * 
                               holiday_factor * promotion_factor * quantity_factor)
            
            # Add noise
            noise = np.random.normal(1, 0.15)  # 15% standard deviation
            quantity = max(0, int(expected_quantity * noise))
            
            # Skip days with zero demand (random stockouts or no sales)
            if random.random() < 0.05:  # 5% chance of no sales
                continue
            
            # Competitor pricing
            competitor_price = base_price * random.uniform(0.85, 1.15)
            
            # Calculate metrics
            revenue = price * quantity
            cost = unit_cost * quantity
            profit = revenue - cost
            
            sales_data.append({
                'product_id': product_id,
                'sku': product['sku'],
                'date': date.date(),
                'quantity': quantity,
                'price': round(price, 2),
                'revenue': round(revenue, 2),
                'cost': round(cost, 2),
                'profit': round(profit, 2),
                'discount_percent': round(discount_percent, 2),
                'competitor_price': round(competitor_price, 2),
                'season': season,
                'day_of_week': day_of_week,
                'is_holiday': holiday,
                'promotion_active': promotion
            })
    
    return pd.DataFrame(sales_data)


def generate_competitor_data(products_df):
    """Generate competitor pricing data"""
    competitor_data = []
    
    date_range = pd.date_range(START_DATE, END_DATE, freq='W')  # Weekly
    
    for _, product in products_df.iterrows():
        product_id = _ + 1
        base_price = product['current_price']
        
        for date in date_range:
            for competitor in COMPETITORS:
                # Competitor prices vary around our base price
                comp_price = base_price * random.uniform(0.80, 1.20)
                
                competitor_data.append({
                    'product_id': product_id,
                    'sku': product['sku'],
                    'competitor_name': competitor,
                    'competitor_price': round(comp_price, 2),
                    'date': date.date(),
                    'url': f'https://{competitor.lower()}.com/product/{product["sku"].lower()}'
                })
    
    return pd.DataFrame(competitor_data)


def main():
    """Generate all data files"""
    print("🏭 Generating Dynamic Pricing Data...")
    
    # Create data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = script_dir
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate products
    print("📦 Generating products...")
    products_df = generate_products()
    
    # Remove simulation-only columns before saving
    products_export = products_df.drop(columns=['true_elasticity', 'base_demand'])
    products_export.to_csv(os.path.join(data_dir, 'products.csv'), index=False)
    print(f"   ✓ Created {len(products_df)} products")
    
    # Generate sales data
    print("💰 Generating sales data (this may take a minute)...")
    sales_df = generate_sales_data(products_df)
    sales_df.to_csv(os.path.join(data_dir, 'sales_data.csv'), index=False)
    print(f"   ✓ Created {len(sales_df):,} sales transactions")
    
    # Generate competitor data
    print("🏪 Generating competitor pricing data...")
    competitors_df = generate_competitor_data(products_df)
    competitors_df.to_csv(os.path.join(data_dir, 'competitors.csv'), index=False)
    print(f"   ✓ Created {len(competitors_df):,} competitor price points")
    
    # Generate summary statistics
    print("\n📊 Data Summary:")
    print(f"   Date Range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"   Products: {len(products_df)}")
    print(f"   Categories: {len(CATEGORIES)}")
    print(f"   Sales Transactions: {len(sales_df):,}")
    print(f"   Total Revenue: ${sales_df['revenue'].sum():,.2f}")
    print(f"   Total Profit: ${sales_df['profit'].sum():,.2f}")
    print(f"   Average Daily Sales per Product: {len(sales_df) / len(products_df) / len(pd.date_range(START_DATE, END_DATE)):.1f}")
    
    print("\n✨ Data generation complete!")
    print(f"📁 Files saved in: {data_dir}")
    print("\nFiles created:")
    print("   - products.csv")
    print("   - sales_data.csv")
    print("   - competitors.csv")


if __name__ == '__main__':
    main()
