"""
ElasticRev - Dynamic Pricing Optimization API
Main Flask application with REST endpoints
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from models import db, Product, Sale, PriceHistory, ElasticityResult, Scenario, CompetitorPrice
from elasticity import ElasticityCalculator, calculate_revenue_optimization
from scenarios import ScenarioSimulator
from config import *
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func, and_, desc
import os
import traceback
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, Reference
import io


# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize extensions
db.init_app(app)
CORS(app, origins=CORS_ORIGINS)

# Initialize calculators
elasticity_calculator = ElasticityCalculator()
scenario_simulator = ScenarioSimulator()


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        product_count = Product.query.count()
        sales_count = Sale.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'products': product_count,
            'sales': sales_count,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ==================== Products API ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        category = request.args.get('category')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        query = Product.query
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        products = [product.to_dict() for product in pagination.items]
        
        return jsonify({
            'products': products,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product details"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Get sales statistics
        sales_stats = db.session.query(
            func.count(Sale.id).label('total_sales'),
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.revenue).label('total_revenue'),
            func.sum(Sale.profit).label('total_profit'),
            func.avg(Sale.price).label('avg_price')
        ).filter_by(product_id=product_id).first()
        
        # Get latest elasticity
        latest_elasticity = ElasticityResult.query.filter_by(
            product_id=product_id
        ).order_by(ElasticityResult.calculation_date.desc()).first()
        
        result = product.to_dict()
        result['statistics'] = {
            'total_sales': sales_stats.total_sales or 0,
            'total_quantity': float(sales_stats.total_quantity or 0),
            'total_revenue': float(sales_stats.total_revenue or 0),
            'total_profit': float(sales_stats.total_profit or 0),
            'avg_price': float(sales_stats.avg_price or 0)
        }
        
        if latest_elasticity:
            result['elasticity'] = latest_elasticity.to_dict()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/products/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        categories = db.session.query(
            Product.category,
            func.count(Product.id).label('count')
        ).group_by(Product.category).all()
        
        return jsonify({
            'categories': [
                {'name': cat[0], 'count': cat[1]} 
                for cat in categories
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Sales API ====================

@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Get sales data with filtering"""
    try:
        product_id = request.args.get('product_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        
        query = Sale.query
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        if start_date:
            query = query.filter(Sale.date >= datetime.fromisoformat(start_date).date())
        
        if end_date:
            query = query.filter(Sale.date <= datetime.fromisoformat(end_date).date())
        
        query = query.order_by(Sale.date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        sales = [sale.to_dict() for sale in pagination.items]
        
        return jsonify({
            'sales': sales,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/sales/summary', methods=['GET'])
def get_sales_summary():
    """Get sales summary statistics"""
    try:
        product_id = request.args.get('product_id', type=int)
        days = int(request.args.get('days', 30))
        
        date_threshold = datetime.now().date() - timedelta(days=days)
        
        query = Sale.query.filter(Sale.date >= date_threshold)
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        summary = db.session.query(
            func.count(Sale.id).label('total_transactions'),
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.revenue).label('total_revenue'),
            func.sum(Sale.profit).label('total_profit'),
            func.avg(Sale.price).label('avg_price'),
            func.avg(Sale.quantity).label('avg_quantity')
        ).filter(Sale.date >= date_threshold)
        
        if product_id:
            summary = summary.filter_by(product_id=product_id)
        
        result = summary.first()
        
        return jsonify({
            'period_days': days,
            'total_transactions': result.total_transactions or 0,
            'total_quantity': float(result.total_quantity or 0),
            'total_revenue': float(result.total_revenue or 0),
            'total_profit': float(result.total_profit or 0),
            'avg_price': float(result.avg_price or 0),
            'avg_quantity': float(result.avg_quantity or 0),
            'avg_margin': round((result.total_profit / result.total_revenue * 100) if result.total_revenue else 0, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Elasticity API ====================

@app.route('/api/elasticity/calculate', methods=['POST'])
def calculate_elasticity():
    """Calculate price elasticity for a product"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        model_type = data.get('model_type', 'linear_regression')
        
        if not product_id:
            return jsonify({'error': 'product_id is required'}), 400
        
        # Convert dates
        if start_date:
            start_date = datetime.fromisoformat(start_date).date()
        if end_date:
            end_date = datetime.fromisoformat(end_date).date()
        
        result = elasticity_calculator.calculate_elasticity(
            product_id, start_date, end_date, model_type
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 400


@app.route('/api/elasticity/products/<int:product_id>', methods=['GET'])
def get_product_elasticity(product_id):
    """Get elasticity results for a product"""
    try:
        latest = request.args.get('latest', 'true').lower() == 'true'
        
        if latest:
            elasticity = ElasticityResult.query.filter_by(
                product_id=product_id
            ).order_by(ElasticityResult.calculation_date.desc()).first()
            
            if not elasticity:
                return jsonify({'error': 'No elasticity data found'}), 404
            
            return jsonify(elasticity.to_dict())
        else:
            elasticities = ElasticityResult.query.filter_by(
                product_id=product_id
            ).order_by(ElasticityResult.calculation_date.desc()).all()
            
            return jsonify({
                'elasticities': [e.to_dict() for e in elasticities]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/elasticity/curve/<int:product_id>', methods=['GET'])
def get_elasticity_curve(product_id):
    """Get elasticity curve data for visualization"""
    try:
        curve_data = elasticity_calculator.get_elasticity_curve(product_id)
        
        if 'error' in curve_data:
            return jsonify(curve_data), 400
        
        return jsonify(curve_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/elasticity/bulk-calculate', methods=['POST'])
def bulk_calculate_elasticity():
    """Calculate elasticity for multiple products"""
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        model_type = data.get('model_type', 'linear_regression')
        
        if not product_ids:
            # Calculate for all products
            products = Product.query.all()
            product_ids = [p.id for p in products]
        
        results = []
        errors = []
        
        for product_id in product_ids:
            try:
                result = elasticity_calculator.calculate_elasticity(
                    product_id, model_type=model_type
                )
                
                if 'error' not in result:
                    results.append({
                        'product_id': product_id,
                        'success': True,
                        'elasticity': result['elasticity_coefficient'],
                        'type': result['elasticity_type']
                    })
                else:
                    errors.append({
                        'product_id': product_id,
                        'error': result['error']
                    })
            except Exception as e:
                errors.append({
                    'product_id': product_id,
                    'error': str(e)
                })
        
        return jsonify({
            'success': results,
            'errors': errors,
            'total_calculated': len(results),
            'total_errors': len(errors)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Scenarios API ====================

@app.route('/api/scenarios/simulate', methods=['POST'])
def simulate_scenario():
    """Simulate a what-if pricing scenario"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        new_price = data.get('new_price')
        simulation_days = data.get('simulation_days', 30)
        scenario_name = data.get('scenario_name')
        
        if not product_id or not new_price:
            return jsonify({'error': 'product_id and new_price are required'}), 400
        
        result = scenario_simulator.simulate_scenario(
            product_id, new_price, simulation_days, scenario_name
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 400


@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Get all scenarios"""
    try:
        product_id = request.args.get('product_id', type=int)
        limit = int(request.args.get('limit', 20))
        
        query = Scenario.query
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        scenarios = query.order_by(Scenario.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'scenarios': [s.to_dict() for s in scenarios]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/scenarios/<int:scenario_id>', methods=['GET'])
def get_scenario(scenario_id):
    """Get scenario details"""
    try:
        scenario = Scenario.query.get_or_404(scenario_id)
        return jsonify(scenario.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/scenarios/compare', methods=['POST'])
def compare_scenarios():
    """Compare multiple scenarios"""
    try:
        data = request.get_json()
        scenario_ids = data.get('scenario_ids', [])
        
        if not scenario_ids:
            return jsonify({'error': 'scenario_ids are required'}), 400
        
        result = scenario_simulator.compare_scenarios(scenario_ids)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/scenarios/bulk-simulate', methods=['POST'])
def bulk_simulate_scenarios():
    """Simulate multiple scenarios"""
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        price_changes = data.get('price_changes', [-10, -5, 5, 10])  # percentages
        
        if not product_ids:
            return jsonify({'error': 'product_ids are required'}), 400
        
        result = scenario_simulator.bulk_simulate(product_ids, price_changes)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Recommendations API ====================

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get pricing recommendations for all products"""
    try:
        category = request.args.get('category')
        
        query = Product.query
        
        if category:
            query = query.filter_by(category=category)
        
        products = query.all()
        
        recommendations = []
        
        for product in products:
            latest_elasticity = ElasticityResult.query.filter_by(
                product_id=product.id
            ).order_by(ElasticityResult.calculation_date.desc()).first()
            
            if latest_elasticity:
                recommendations.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'category': product.category,
                    'current_price': product.current_price,
                    'optimal_price': latest_elasticity.optimal_price,
                    'recommended_action': latest_elasticity.recommended_action,
                    'expected_revenue_change': latest_elasticity.expected_revenue_change,
                    'elasticity_type': latest_elasticity.elasticity_type,
                    'elasticity_coefficient': latest_elasticity.elasticity_coefficient
                })
        
        # Sort by expected revenue change
        recommendations.sort(key=lambda x: x.get('expected_revenue_change', 0), reverse=True)
        
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/recommendations/<int:product_id>', methods=['GET'])
def get_product_recommendation(product_id):
    """Get pricing recommendation for specific product"""
    try:
        optimization = calculate_revenue_optimization(product_id)
        
        if 'error' in optimization:
            return jsonify(optimization), 400
        
        return jsonify(optimization)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Analytics API ====================

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get dashboard KPIs and analytics"""
    try:
        days = int(request.args.get('days', 30))
        date_threshold = datetime.now().date() - timedelta(days=days)
        
        # Overall metrics
        overall = db.session.query(
            func.sum(Sale.revenue).label('total_revenue'),
            func.sum(Sale.profit).label('total_profit'),
            func.sum(Sale.quantity).label('total_quantity'),
            func.count(func.distinct(Sale.product_id)).label('products_sold')
        ).filter(Sale.date >= date_threshold).first()
        
        # Category performance
        category_perf = db.session.query(
            Product.category,
            func.sum(Sale.revenue).label('revenue'),
            func.sum(Sale.profit).label('profit')
        ).join(Sale).filter(Sale.date >= date_threshold).group_by(
            Product.category
        ).all()
        
        # Elasticity distribution
        elasticity_dist = db.session.query(
            ElasticityResult.elasticity_type,
            func.count(ElasticityResult.id).label('count')
        ).group_by(ElasticityResult.elasticity_type).all()
        
        # Top products by revenue
        top_products = db.session.query(
            Product.id,
            Product.name,
            func.sum(Sale.revenue).label('revenue')
        ).join(Sale).filter(Sale.date >= date_threshold).group_by(
            Product.id, Product.name
        ).order_by(desc('revenue')).limit(10).all()
        
        return jsonify({
            'period_days': days,
            'overall': {
                'total_revenue': float(overall.total_revenue or 0),
                'total_profit': float(overall.total_profit or 0),
                'total_quantity': float(overall.total_quantity or 0),
                'products_sold': overall.products_sold or 0,
                'avg_margin': round((overall.total_profit / overall.total_revenue * 100) if overall.total_revenue else 0, 2)
            },
            'by_category': [
                {
                    'category': cat.category,
                    'revenue': float(cat.revenue),
                    'profit': float(cat.profit)
                }
                for cat in category_perf
            ],
            'elasticity_distribution': [
                {
                    'type': dist.elasticity_type,
                    'count': dist.count
                }
                for dist in elasticity_dist
            ],
            'top_products': [
                {
                    'id': prod.id,
                    'name': prod.name,
                    'revenue': float(prod.revenue)
                }
                for prod in top_products
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Excel Export API ====================

def get_dashboard_analytics_data(days=30):
    """Helper function to get dashboard analytics data for export"""
    date_threshold = datetime.now().date() - timedelta(days=days)
    
    # Overall metrics
    overall = db.session.query(
        func.sum(Sale.revenue).label('total_revenue'),
        func.sum(Sale.profit).label('total_profit'),
        func.count(func.distinct(Sale.product_id)).label('products_sold')
    ).filter(Sale.date >= date_threshold).first()
    
    # Total products and products with elasticity
    total_products = Product.query.count()
    products_with_elasticity = ElasticityResult.query.distinct(ElasticityResult.product_id).count()
    
    return {
        'total_revenue': float(overall.total_revenue or 0),
        'total_profit': float(overall.total_profit or 0),
        'products_sold': overall.products_sold or 0,
        'total_products': total_products,
        'products_with_elasticity': products_with_elasticity
    }

@app.route('/api/export/excel', methods=['GET'])
def export_to_excel():
    """Export comprehensive pricing strategy report to Excel"""
    try:
        product_id = request.args.get('product_id', type=int)
        days = int(request.args.get('days', 30))

        # Create workbook
        wb = Workbook()
        wb.remove(wb.active)

        # ===== SUMMARY SHEET =====
        ws_summary = wb.create_sheet('Executive Summary')
        ws_summary.merge_cells('A1:H1')
        ws_summary['A1'] = 'ElasticRev - Pricing Strategy Report'
        ws_summary['A1'].font = Font(size=18, bold=True, color='FFFFFF')
        ws_summary['A1'].fill = PatternFill(start_color='2E5090', end_color='2E5090', fill_type='solid')
        ws_summary['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws_summary.row_dimensions[1].height = 30

        ws_summary['A3'] = 'Report Generated:'
    ws_summary['B3'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ws_summary['A4'] = 'Analysis Period:'
    ws_summary['B4'] = f'Last {days} days'

    # Get dashboard analytics
    analytics = get_dashboard_analytics_data(days)

    ws_summary['A6'] = 'Key Metrics'
    ws_summary['A6'].font = Font(size=14, bold=True)
    ws_summary['A7'] = 'Total Products:'
    ws_summary['B7'] = analytics.get('total_products', 0)
    ws_summary['A8'] = 'Total Revenue:'
    ws_summary['B8'] = f"${analytics.get('total_revenue', 0):,.2f}"
    ws_summary['A9'] = 'Products Analyzed:'
    ws_summary['B9'] = analytics.get('products_with_elasticity', 0)
    ws_summary['A10'] = 'Active Scenarios:'
    ws_summary['B10'] = Scenario.query.count()

    # Add large stylized message in columns J to M
    ws_summary.merge_cells('J2:M6')
    cell = ws_summary['J2']
    cell.value = '👉 Explore the other tabs below for detailed analysis, recommendations, and scenario results!'
    cell.font = Font(size=24, bold=True, color='2E5090', name='Calibri')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.fill = PatternFill(start_color='F3F6FB', end_color='F3F6FB', fill_type='solid')
    ws_summary.row_dimensions[2].height = 80
        
        # ===== ELASTICITY ANALYSIS SHEET =====
        ws_elasticity = wb.create_sheet('Elasticity Analysis')
        headers = ['Product', 'Category', 'Current Price', 'Elasticity Coefficient', 'Type', 
                  'Optimal Price', 'Expected Revenue Change %', 'Recommendation', 'Confidence']
        
        for col, header in enumerate(headers, 1):
            cell = ws_elasticity.cell(1, col, header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        query = db.session.query(Product, ElasticityResult).join(
            ElasticityResult, Product.id == ElasticityResult.product_id
        ).order_by(Product.category, Product.name)
        
        if product_id:
            query = query.filter(Product.id == product_id)
        
        results = query.all()
        
        for row, (product, elasticity) in enumerate(results, 2):
            ws_elasticity.cell(row, 1, product.name)
            ws_elasticity.cell(row, 2, product.category)
            ws_elasticity.cell(row, 3, f"${product.current_price:.2f}")
            ws_elasticity.cell(row, 4, round(elasticity.elasticity_coefficient, 3))
            ws_elasticity.cell(row, 5, elasticity.elasticity_type)
            ws_elasticity.cell(row, 6, f"${elasticity.optimal_price:.2f}" if elasticity.optimal_price else 'N/A')
            ws_elasticity.cell(row, 7, f"{elasticity.expected_revenue_change:.2f}%" if elasticity.expected_revenue_change else 'N/A')
            ws_elasticity.cell(row, 8, elasticity.recommended_action or 'N/A')
            ws_elasticity.cell(row, 9, f"{elasticity.r_squared:.2f}" if elasticity.r_squared else 'N/A')
        
        # ===== SCENARIOS SHEET =====
        ws_scenarios = wb.create_sheet('Scenarios')
        scenario_headers = ['Scenario Name', 'Product', 'Current Price', 'New Price', 
                           'Price Change %', 'Revenue Change %', 'Profit Change %', 
                           'Demand Change %', 'Recommendation', 'Created']
        
        for col, header in enumerate(scenario_headers, 1):
            cell = ws_scenarios.cell(1, col, header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='70AD47', end_color='70AD47', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        scenarios = Scenario.query.order_by(Scenario.created_at.desc()).limit(50).all()
        
        for row, scenario in enumerate(scenarios, 2):
            scenario_dict = scenario.to_dict()
            ws_scenarios.cell(row, 1, scenario.name)
            ws_scenarios.cell(row, 2, scenario_dict['product_name'])
            ws_scenarios.cell(row, 3, f"${scenario.current_price:.2f}")
            ws_scenarios.cell(row, 4, f"${scenario.new_price:.2f}")
            ws_scenarios.cell(row, 5, f"{scenario.price_change_percent:.2f}%")
            ws_scenarios.cell(row, 6, f"{scenario.revenue_change_percent:.2f}%" if scenario.revenue_change_percent else 'N/A')
            ws_scenarios.cell(row, 7, f"{scenario.profit_change_percent:.2f}%" if scenario.profit_change_percent else 'N/A')
            ws_scenarios.cell(row, 8, f"{scenario.demand_change_percent:.2f}%" if scenario.demand_change_percent else 'N/A')
            rec = scenario_dict.get('recommendation', {})
            ws_scenarios.cell(row, 9, rec.get('action', 'N/A') if rec else 'N/A')
            ws_scenarios.cell(row, 10, scenario.created_at.strftime('%Y-%m-%d') if scenario.created_at else 'N/A')
        
        # ===== RECOMMENDATIONS SHEET =====
        ws_recommendations = wb.create_sheet('Recommendations')
        rec_headers = ['Product', 'Category', 'Current Price', 'Optimal Price', 
                      'Expected Impact', 'Elasticity Type', 'Action']
        
        for col, header in enumerate(rec_headers, 1):
            cell = ws_recommendations.cell(1, col, header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        # Get recommendations from products with elasticity
        recommendations_query = db.session.query(Product, ElasticityResult).join(
            ElasticityResult, Product.id == ElasticityResult.product_id
        ).filter(
            ElasticityResult.expected_revenue_change.isnot(None)
        ).order_by(ElasticityResult.expected_revenue_change.desc()).limit(50).all()
        
        for row, (product, elasticity) in enumerate(recommendations_query, 2):
            ws_recommendations.cell(row, 1, product.name)
            ws_recommendations.cell(row, 2, product.category)
            ws_recommendations.cell(row, 3, f"${product.current_price:.2f}")
            ws_recommendations.cell(row, 4, f"${elasticity.optimal_price:.2f}" if elasticity.optimal_price else 'N/A')
            ws_recommendations.cell(row, 5, f"{elasticity.expected_revenue_change:.2f}%" if elasticity.expected_revenue_change else 'N/A')
            ws_recommendations.cell(row, 6, elasticity.elasticity_type or 'N/A')
            ws_recommendations.cell(row, 7, elasticity.recommended_action or 'N/A')
        
        # ===== SALES DATA SHEET =====
        ws_sales = wb.create_sheet('Sales Performance')
        sales_headers = ['Product', 'Category', 'Total Sales', 'Total Revenue', 
                        'Avg Price', 'Avg Quantity', 'Last Sale Date']
        
        for col, header in enumerate(sales_headers, 1):
            cell = ws_sales.cell(1, col, header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='ED7D31', end_color='ED7D31', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        # Get sales summary
        cutoff_date = datetime.now() - timedelta(days=days)
        sales_query = db.session.query(
            Product.name,
            Product.category,
            db.func.count(Sale.id).label('total_sales'),
            db.func.sum(Sale.revenue).label('total_revenue'),
            db.func.avg(Sale.price).label('avg_price'),
            db.func.avg(Sale.quantity).label('avg_quantity'),
            db.func.max(Sale.date).label('last_sale')
        ).join(Sale, Product.id == Sale.product_id).filter(
            Sale.date >= cutoff_date
        ).group_by(Product.id, Product.name, Product.category).order_by(
            db.func.sum(Sale.revenue).desc()
        ).all()
        
        for row, sale_data in enumerate(sales_query, 2):
            ws_sales.cell(row, 1, sale_data.name)
            ws_sales.cell(row, 2, sale_data.category)
            ws_sales.cell(row, 3, sale_data.total_sales)
            ws_sales.cell(row, 4, f"${sale_data.total_revenue:,.2f}")
            ws_sales.cell(row, 5, f"${sale_data.avg_price:.2f}")
            ws_sales.cell(row, 6, f"{sale_data.avg_quantity:.1f}")
            ws_sales.cell(row, 7, sale_data.last_sale.strftime('%Y-%m-%d') if sale_data.last_sale else 'N/A')
        
        # Auto-size all columns in all sheets
        for ws in wb.worksheets:
            for column in ws.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min((max_length + 2), 50)
                # Skip merged cells
                if hasattr(column[0], 'column_letter'):
                    ws.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f'pricing_strategy_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 400


# ==================== Main ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("=" * 60)
    print("🚀 ElasticRev - Dynamic Pricing Optimization API")
    print("=" * 60)
    print(f"📍 Server running on: http://localhost:5000")
    print(f"📚 API documentation: http://localhost:5000/api/health")
    print("=" * 60)
    
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
