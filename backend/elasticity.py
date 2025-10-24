import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, Product, Sale, ElasticityResult
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import statsmodels.api as sm
from scipy import stats


class ElasticityCalculator:
    """Calculate price elasticity of demand for products"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def calculate_elasticity(self, product_id, start_date=None, end_date=None, model_type='linear_regression'):
        """
        Calculate price elasticity coefficient for a product
        
        Args:
            product_id: Product ID
            start_date: Start of analysis period
            end_date: End of analysis period
            model_type: 'linear_regression' or 'gradient_boosting'
            
        Returns:
            dict: Elasticity results
        """
        try:
            # Fetch sales data
            query = Sale.query.filter_by(product_id=product_id)

            if start_date:
                query = query.filter(Sale.date >= start_date)
            if end_date:
                query = query.filter(Sale.date <= end_date)

            sales_data = query.all()

            if len(sales_data) < 10:
                return {
                    'error': 'Insufficient data for elasticity calculation',
                    'sample_size': len(sales_data)
                }

            # Prepare data
            df = pd.DataFrame([{
                'date': sale.date,
                'price': sale.price,
                'quantity': sale.quantity,
                'revenue': sale.revenue,
                'discount_percent': sale.discount_percent,
                'competitor_price': sale.competitor_price,
                'is_holiday': int(sale.is_holiday),
                'promotion_active': int(sale.promotion_active)
            } for sale in sales_data])

            # Filter out rows with non-positive price/quantity which break log transforms
            df = df[(df['price'] > 0) & (df['quantity'] > 0)].copy()

            if df.empty or len(df) < 10:
                return {
                    'error': 'Insufficient valid sales data (positive price and quantity required)',
                    'sample_size': len(df)
                }

            # Calculate log transformations for elasticity
            df['log_price'] = np.log(df['price'])
            df['log_quantity'] = np.log(df['quantity'])

            # Prepare features
            X = df[['log_price']].values
            y = df['log_quantity'].values

            # Add additional features for gradient boosting
            if model_type == 'gradient_boosting':
                features = ['log_price', 'discount_percent', 'is_holiday', 'promotion_active']
                if df['competitor_price'].notna().sum() > 0:
                    # Use price fallback when competitor price missing
                    df['log_competitor_price'] = np.log(df['competitor_price'].fillna(df['price']))
                    features.append('log_competitor_price')

                X = df[features].fillna(0).values

            # Calculate elasticity
            if model_type == 'linear_regression':
                result = self._calculate_linear_elasticity(X, y, df)
            else:
                result = self._calculate_gradient_boosting_elasticity(X, y, df)

            # Determine elasticity type
            elasticity_type = self._classify_elasticity(result.get('elasticity_coefficient', 0.0))
            result['elasticity_type'] = elasticity_type

            # Generate recommendations
            product = Product.query.get(product_id)
            result['recommendations'] = self._generate_recommendations(
                product, result.get('elasticity_coefficient', 0.0), df
            )

            # Store results in database
            self._save_results(product_id, result, start_date, end_date, model_type, len(sales_data))

            return result
        except Exception as e:
            tb = traceback.format_exc()
            print('Elasticity calculation error:', e)
            print(tb)
            return {'error': str(e), 'trace': tb}
    
    def _calculate_linear_elasticity(self, X, y, df):
        """Calculate elasticity using linear regression"""
        # Fit OLS model
        X_with_const = sm.add_constant(X)
        model = sm.OLS(y, X_with_const).fit()
        
        elasticity = model.params[1]  # Coefficient of log_price
        
        # Calculate confidence interval
        conf_int = model.conf_int(alpha=0.05)
        
        return {
            'elasticity_coefficient': float(elasticity),
            'r_squared': float(model.rsquared),
            'p_value': float(model.pvalues[1]),
            'confidence_interval_lower': float(conf_int[1][0]),
            'confidence_interval_upper': float(conf_int[1][1]),
            'standard_error': float(model.bse[1]),
            'model_type': 'linear_regression'
        }
    
    def _calculate_gradient_boosting_elasticity(self, X, y, df):
        """Calculate elasticity using gradient boosting"""
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        
        # Fit model
        model.fit(X, y)
        
        # Calculate elasticity at mean price
        mean_price = df['log_price'].mean()
        
        # Compute partial derivative numerically
        delta = 0.01
        X_base = X.mean(axis=0).reshape(1, -1)
        X_base[0, 0] = mean_price
        
        X_plus = X_base.copy()
        X_plus[0, 0] += delta
        
        y_base = model.predict(X_base)[0]
        y_plus = model.predict(X_plus)[0]
        
        elasticity = (y_plus - y_base) / delta
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        # Bootstrap for confidence intervals
        elasticities = []
        for _ in range(100):
            indices = np.random.choice(len(X), len(X), replace=True)
            X_boot = X[indices]
            y_boot = y[indices]
            
            boot_model = GradientBoostingRegressor(
                n_estimators=50, learning_rate=0.1, max_depth=3, random_state=None
            )
            boot_model.fit(X_boot, y_boot)
            
            y_base_boot = boot_model.predict(X_base)[0]
            y_plus_boot = boot_model.predict(X_plus)[0]
            
            boot_elasticity = (y_plus_boot - y_base_boot) / delta
            elasticities.append(boot_elasticity)
        
        conf_lower = np.percentile(elasticities, 2.5)
        conf_upper = np.percentile(elasticities, 97.5)
        
        return {
            'elasticity_coefficient': float(elasticity),
            'r_squared': float(cv_scores.mean()),
            'confidence_interval_lower': float(conf_lower),
            'confidence_interval_upper': float(conf_upper),
            'feature_importance': model.feature_importances_.tolist(),
            'model_type': 'gradient_boosting'
        }
    
    def _classify_elasticity(self, coefficient):
        """Classify elasticity type"""
        abs_coef = abs(coefficient)
        
        if abs_coef > 2:
            return 'highly_elastic'
        elif abs_coef > 1:
            return 'elastic'
        elif abs_coef >= 0.9 and abs_coef <= 1.1:
            return 'unit_elastic'
        else:
            return 'inelastic'
    
    def _generate_recommendations(self, product, elasticity, df):
        """Generate pricing recommendations based on elasticity"""
        current_price = product.current_price
        unit_cost = product.unit_cost
        current_margin = (current_price - unit_cost) / current_price
        
        avg_quantity = df['quantity'].mean()
        current_revenue = current_price * avg_quantity
        
        recommendations = {
            'current_price': current_price,
            'current_margin': round(current_margin * 100, 2)
        }
        
        # Strategy based on elasticity
        if abs(elasticity) > 1:
            # Elastic demand - price decrease can increase revenue
            suggested_price = current_price * 0.95  # 5% decrease
            predicted_quantity = avg_quantity * (1 + abs(elasticity) * 0.05)
            
            recommendations['strategy'] = 'Price Decrease'
            recommendations['suggested_price'] = round(suggested_price, 2)
            recommendations['reasoning'] = 'Demand is elastic. Price reduction will increase quantity more than proportionally.'
            
        else:
            # Inelastic demand - price increase won't hurt volume much
            suggested_price = current_price * 1.05  # 5% increase
            predicted_quantity = avg_quantity * (1 - abs(elasticity) * 0.05)
            
            recommendations['strategy'] = 'Price Increase'
            recommendations['suggested_price'] = round(suggested_price, 2)
            recommendations['reasoning'] = 'Demand is inelastic. Price increase will boost revenue without significant volume loss.'
        
        predicted_revenue = suggested_price * predicted_quantity
        revenue_change = ((predicted_revenue - current_revenue) / current_revenue) * 100
        
        recommendations['predicted_revenue_change'] = round(revenue_change, 2)
        recommendations['predicted_quantity'] = round(predicted_quantity, 0)
        
        # Optimal price calculation (maximize revenue)
        if elasticity < -1:
            # For elastic goods, optimal price is lower
            optimal_price = unit_cost / (1 + 1/abs(elasticity))
        else:
            # For inelastic goods, optimal price is higher
            optimal_price = unit_cost * (1 + 1/abs(elasticity))
        
        optimal_price = max(unit_cost * 1.1, min(optimal_price, current_price * 1.5))
        recommendations['optimal_price'] = round(optimal_price, 2)
        
        return recommendations
    
    def _save_results(self, product_id, result, start_date, end_date, model_type, sample_size):
        """Save elasticity results to database"""
        try:
            elasticity_result = ElasticityResult(
                product_id=product_id,
                elasticity_coefficient=result['elasticity_coefficient'],
                elasticity_type=result['elasticity_type'],
                r_squared=result.get('r_squared'),
                sample_size=sample_size,
                model_type=model_type,
                confidence_interval_lower=result.get('confidence_interval_lower'),
                confidence_interval_upper=result.get('confidence_interval_upper'),
                period_start=start_date,
                period_end=end_date,
                recommended_action=result['recommendations'].get('strategy'),
                optimal_price=result['recommendations'].get('optimal_price'),
                expected_revenue_change=result['recommendations'].get('predicted_revenue_change')
            )
            
            db.session.add(elasticity_result)
            db.session.commit()
            
            result['id'] = elasticity_result.id
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving elasticity results: {e}")
    
    def get_elasticity_curve(self, product_id, price_range=None):
        """
        Generate elasticity curve data for visualization
        
        Args:
            product_id: Product ID
            price_range: Tuple of (min_price, max_price), defaults to ±30% of current
            
        Returns:
            dict: Curve data points
        """
        product = Product.query.get(product_id)
        if not product:
            return {'error': 'Product not found'}
        
        # Get latest elasticity
        latest_elasticity = ElasticityResult.query.filter_by(
            product_id=product_id
        ).order_by(ElasticityResult.calculation_date.desc()).first()
        
        if not latest_elasticity:
            return {'error': 'No elasticity data available'}
        
        elasticity = latest_elasticity.elasticity_coefficient
        current_price = product.current_price
        
        # Get average quantity
        avg_quantity = db.session.query(func.avg(Sale.quantity)).filter_by(
            product_id=product_id
        ).scalar() or 100
        
        # Generate price points
        if price_range:
            min_price, max_price = price_range
        else:
            min_price = current_price * 0.7
            max_price = current_price * 1.3
        
        prices = np.linspace(min_price, max_price, 50)
        
        # Calculate demand at each price point using elasticity
        quantities = []
        revenues = []
        profits = []
        
        for price in prices:
            # Q = Q0 * (P / P0) ^ elasticity
            quantity = avg_quantity * ((price / current_price) ** elasticity)
            revenue = price * quantity
            profit = (price - product.unit_cost) * quantity
            
            quantities.append(float(quantity))
            revenues.append(float(revenue))
            profits.append(float(profit))
        
        return {
            'prices': prices.tolist(),
            'quantities': quantities,
            'revenues': revenues,
            'profits': profits,
            'current_price': current_price,
            'current_quantity': float(avg_quantity),
            'elasticity': elasticity,
            'optimal_price': float(latest_elasticity.optimal_price) if latest_elasticity.optimal_price else current_price
        }
    
    def calculate_cross_elasticity(self, product_id_1, product_id_2):
        """
        Calculate cross-price elasticity between two products
        
        Cross elasticity = % change in quantity of product 1 / % change in price of product 2
        
        Positive = substitutes, Negative = complements
        """
        # Get sales data for both products on same dates
        dates_p1 = db.session.query(Sale.date).filter_by(product_id=product_id_1).all()
        dates_p2 = db.session.query(Sale.date).filter_by(product_id=product_id_2).all()
        
        common_dates = set([d[0] for d in dates_p1]).intersection([d[0] for d in dates_p2])
        
        if len(common_dates) < 10:
            return {'error': 'Insufficient overlapping data'}
        
        sales_p1 = Sale.query.filter(
            Sale.product_id == product_id_1,
            Sale.date.in_(common_dates)
        ).order_by(Sale.date).all()
        
        sales_p2 = Sale.query.filter(
            Sale.product_id == product_id_2,
            Sale.date.in_(common_dates)
        ).order_by(Sale.date).all()
        
        df1 = pd.DataFrame([{'date': s.date, 'quantity': s.quantity, 'price': s.price} for s in sales_p1])
        df2 = pd.DataFrame([{'date': s.date, 'quantity': s.quantity, 'price': s.price} for s in sales_p2])
        
        df = pd.merge(df1, df2, on='date', suffixes=('_1', '_2'))
        
        # Calculate cross elasticity
        df['log_quantity_1'] = np.log(df['quantity_1'])
        df['log_price_2'] = np.log(df['price_2'])
        
        X = df[['log_price_2']].values
        y = df['log_quantity_1'].values
        
        X_with_const = sm.add_constant(X)
        model = sm.OLS(y, X_with_const).fit()
        
        cross_elasticity = model.params[1]
        
        # Determine relationship
        if cross_elasticity > 0.3:
            relationship = 'substitutes'
        elif cross_elasticity < -0.3:
            relationship = 'complements'
        else:
            relationship = 'independent'
        
        return {
            'cross_elasticity': float(cross_elasticity),
            'relationship': relationship,
            'r_squared': float(model.rsquared),
            'p_value': float(model.pvalues[1]),
            'sample_size': len(df)
        }


def calculate_revenue_optimization(product_id, cost_constraint=None):
    """
    Find optimal price that maximizes revenue
    
    Args:
        product_id: Product ID
        cost_constraint: Minimum margin required
        
    Returns:
        dict: Optimal pricing strategy
    """
    calculator = ElasticityCalculator()
    product = Product.query.get(product_id)
    
    if not product:
        return {'error': 'Product not found'}
    
    # Get elasticity
    latest_elasticity = ElasticityResult.query.filter_by(
        product_id=product_id
    ).order_by(ElasticityResult.calculation_date.desc()).first()
    
    if not latest_elasticity:
        return {'error': 'Calculate elasticity first'}
    
    elasticity = latest_elasticity.elasticity_coefficient
    current_price = product.current_price
    unit_cost = product.unit_cost
    
    # Get current average quantity
    avg_quantity = db.session.query(func.avg(Sale.quantity)).filter_by(
        product_id=product_id
    ).scalar() or 100
    
    # Revenue maximization: dR/dP = 0
    # R = P * Q = P * Q0 * (P/P0)^e
    # Optimal price: P* = P0 * (e / (e + 1))
    
    if elasticity >= -1:
        # Inelastic demand - increase price
        optimal_price = current_price * 1.2
    else:
        # Elastic demand - use formula
        optimal_price = current_price * (elasticity / (elasticity + 1))
    
    # Apply cost constraint
    if cost_constraint:
        min_price = unit_cost / (1 - cost_constraint)
        optimal_price = max(optimal_price, min_price)
    
    # Ensure price is within reasonable bounds
    optimal_price = max(unit_cost * 1.1, min(optimal_price, current_price * 2))
    
    # Calculate predicted outcomes
    predicted_quantity = avg_quantity * ((optimal_price / current_price) ** elasticity)
    predicted_revenue = optimal_price * predicted_quantity
    current_revenue = current_price * avg_quantity
    
    predicted_profit = (optimal_price - unit_cost) * predicted_quantity
    current_profit = (current_price - unit_cost) * avg_quantity
    
    return {
        'current_price': current_price,
        'optimal_price': round(optimal_price, 2),
        'price_change_percent': round(((optimal_price - current_price) / current_price) * 100, 2),
        'current_quantity': round(avg_quantity, 0),
        'predicted_quantity': round(predicted_quantity, 0),
        'quantity_change_percent': round(((predicted_quantity - avg_quantity) / avg_quantity) * 100, 2),
        'current_revenue': round(current_revenue, 2),
        'predicted_revenue': round(predicted_revenue, 2),
        'revenue_change_percent': round(((predicted_revenue - current_revenue) / current_revenue) * 100, 2),
        'current_profit': round(current_profit, 2),
        'predicted_profit': round(predicted_profit, 2),
        'profit_change_percent': round(((predicted_profit - current_profit) / current_profit) * 100, 2),
        'elasticity_used': elasticity
    }
