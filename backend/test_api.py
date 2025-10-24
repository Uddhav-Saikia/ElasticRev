#!/usr/bin/env python
"""Quick test of API endpoints"""

from app import app
from flask import json

with app.test_client() as client:
    # Test health endpoint
    print("Testing /api/health...")
    response = client.get('/api/health')
    print(f'  Status: {response.status_code}')
    data = response.get_json()
    if data:
        print(f'  Keys: {list(data.keys())}')
    
    # Test products endpoint
    print("\nTesting /api/products...")
    response = client.get('/api/products?per_page=2')
    print(f'  Status: {response.status_code}')
    data = response.get_json()
    if data:
        print(f'  Keys: {list(data.keys())}')
        if 'products' in data:
            print(f'  Product count: {len(data["products"])}')
            if data['products']:
                print(f'  First product keys: {list(data["products"][0].keys())[:5]}...')
    
    # Test elasticity/products endpoint
    print("\nTesting /api/elasticity/products/1...")
    response = client.get('/api/elasticity/products/1?latest=true')
    print(f'  Status: {response.status_code}')
    if response.status_code == 200:
        data = response.get_json()
        print(f'  Has elasticity data: {data is not None}')
    else:
        print(f'  Response: {response.get_json()}')
    
    # Test diagnostics endpoint
    print("\nTesting /api/diagnostics/data-quality...")
    response = client.get('/api/diagnostics/data-quality')
    print(f'  Status: {response.status_code}')
    data = response.get_json()
    if data:
        print(f'  Status: {data.get("status")}')
        print(f'  Total products: {data.get("total_products")}')
        print(f'  Total sales: {data.get("total_sales")}')
