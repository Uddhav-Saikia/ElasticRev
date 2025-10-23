import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models import db, Product, Sale, Scenario, ElasticityResult
from sqlalchemy import func


class ScenarioSimulator:
    """Simulate what-if pricing scenarios"""
    
    def __init__(self):
        self.confidence_level = 0.95
    
    def simulate_scenario(self, product_id, new_price, simulation_days=30, scenario_name=None):
        """
        Simulate impact of price change on demand, revenue, and profit
        
        Args:
            product_id: Product ID
            new_price: Proposed new price
            simulation_days: Number of days to simulate
            scenario_name: Optional name for the scenario
            
        Returns:
            dict: Simulation results
        """
        product = Product.query.get(product_id)
        if not product:
            return {'error': 'Product not found'}
        
        # Get latest elasticity
        elasticity_result = ElasticityResult.query.filter_by(
            product_id=product_id
        ).order_by(ElasticityResult.calculation_date.desc()).first()
        
        if not elasticity_result:
            return {'error': 'No elasticity data available. Calculate elasticity first.'}
        
        elasticity = elasticity_result.elasticity_coefficient
        current_price = product.current_price
        unit_cost = product.unit_cost
        
        # Calculate price change
        price_change_percent = ((new_price - current_price) / current_price) * 100
        
        # Validate price change limits
        if price_change_percent < -30:
            return {'error': 'Price decrease exceeds 30% limit'}
        if price_change_percent > 20:
            return {'error': 'Price increase exceeds 20% limit'}
        
        # Get historical averages
        date_threshold = datetime.now().date() - timedelta(days=90)
        
        historical_sales = Sale.query.filter(
            Sale.product_id == product_id,
            Sale.date >= date_threshold
        ).all()
        
        if len(historical_sales) < 10:
            return {'error': 'Insufficient historical data'}
        
        df = pd.DataFrame([{
            'quantity': sale.quantity,
            'revenue': sale.revenue,
            'profit': sale.profit,
            'price': sale.price
        } for sale in historical_sales])
        
        current_avg_quantity = df['quantity'].mean()
        current_avg_revenue = df['revenue'].mean()
        current_avg_profit = df['profit'].mean()
        
        # Calculate predicted values using elasticity
        # % change in quantity = elasticity * % change in price
        quantity_change_percent = elasticity * (price_change_percent / 100) * 100
        
        predicted_quantity = current_avg_quantity * (1 + quantity_change_percent / 100)
        predicted_revenue = new_price * predicted_quantity
        predicted_profit = (new_price - unit_cost) * predicted_quantity
        
        # Calculate changes
        revenue_change_percent = ((predicted_revenue - current_avg_revenue) / current_avg_revenue) * 100
        profit_change_percent = ((predicted_profit - current_avg_profit) / current_avg_profit) * 100
        
        # Project over simulation period
        total_current_revenue = current_avg_revenue * simulation_days
        total_predicted_revenue = predicted_revenue * simulation_days
        
        total_current_profit = current_avg_profit * simulation_days
        total_predicted_profit = predicted_profit * simulation_days
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(
            elasticity_result, current_avg_quantity, current_price, new_price
        )
        
        # Generate scenario name if not provided
        if not scenario_name:
            direction = "Increase" if price_change_percent > 0 else "Decrease"
            scenario_name = f"Price {direction} {abs(price_change_percent):.1f}% - {simulation_days} days"
        
        result = {
            'scenario_name': scenario_name,
            'product_id': product_id,
            'product_name': product.name,
            'simulation_days': simulation_days,
            'pricing': {
                'current_price': current_price,
                'new_price': new_price,
                'price_change': new_price - current_price,
                'price_change_percent': round(price_change_percent, 2)
            },
            'demand': {
                'current_daily_quantity': round(current_avg_quantity, 1),
                'predicted_daily_quantity': round(predicted_quantity, 1),
                'quantity_change_percent': round(quantity_change_percent, 2),
                'total_current_volume': round(current_avg_quantity * simulation_days, 0),
                'total_predicted_volume': round(predicted_quantity * simulation_days, 0)
            },
            'revenue': {
                'current_daily_revenue': round(current_avg_revenue, 2),
                'predicted_daily_revenue': round(predicted_revenue, 2),
                'revenue_change_percent': round(revenue_change_percent, 2),
                'total_current_revenue': round(total_current_revenue, 2),
                'total_predicted_revenue': round(total_predicted_revenue, 2),
                'total_revenue_change': round(total_predicted_revenue - total_current_revenue, 2)
            },
            'profit': {
                'current_daily_profit': round(current_avg_profit, 2),
                'predicted_daily_profit': round(predicted_profit, 2),
                'profit_change_percent': round(profit_change_percent, 2),
                'total_current_profit': round(total_current_profit, 2),
                'total_predicted_profit': round(total_predicted_profit, 2),
                'total_profit_change': round(total_predicted_profit - total_current_profit, 2)
            },
            'margins': {
                'current_margin_percent': round(((current_price - unit_cost) / current_price) * 100, 2),
                'predicted_margin_percent': round(((new_price - unit_cost) / new_price) * 100, 2)
            },
            'elasticity': {
                'coefficient': elasticity,
                'type': elasticity_result.elasticity_type,
                'confidence_interval': confidence_intervals
            },
            'recommendation': self._generate_recommendation(
                price_change_percent, revenue_change_percent, profit_change_percent
            )
        }
        
        # Save scenario to database
        self._save_scenario(result, elasticity)
        
        return result
    
    def _calculate_confidence_intervals(self, elasticity_result, current_qty, current_price, new_price):
        """Calculate confidence intervals for predictions"""
        elasticity = elasticity_result.elasticity_coefficient
        el_lower = elasticity_result.confidence_interval_lower or elasticity * 0.8
        el_upper = elasticity_result.confidence_interval_upper or elasticity * 1.2
        
        price_change = (new_price - current_price) / current_price
        
        # Lower bound (pessimistic)
        qty_change_lower = el_lower * price_change
        qty_lower = current_qty * (1 + qty_change_lower)
        revenue_lower = new_price * qty_lower
        
        # Upper bound (optimistic)
        qty_change_upper = el_upper * price_change
        qty_upper = current_qty * (1 + qty_change_upper)
        revenue_upper = new_price * qty_upper
        
        return {
            'quantity': {
                'lower': round(qty_lower, 1),
                'upper': round(qty_upper, 1)
            },
            'revenue': {
                'lower': round(revenue_lower, 2),
                'upper': round(revenue_upper, 2)
            }
        }
    
    def _generate_recommendation(self, price_change, revenue_change, profit_change):
        """Generate recommendation based on simulation results"""
        if revenue_change > 5 and profit_change > 5:
            return {
                'action': 'Highly Recommended',
                'reason': 'Both revenue and profit increase significantly',
                'risk_level': 'Low'
            }
        elif revenue_change > 0 and profit_change > 0:
            return {
                'action': 'Recommended',
                'reason': 'Positive impact on revenue and profit',
                'risk_level': 'Low'
            }
        elif profit_change > 0 and revenue_change < 0:
            return {
                'action': 'Consider',
                'reason': 'Profit increases but revenue decreases (volume play)',
                'risk_level': 'Medium'
            }
        elif profit_change > -5 and revenue_change < 0:
            return {
                'action': 'Caution',
                'reason': 'Slight profit decrease, monitor closely',
                'risk_level': 'Medium'
            }
        else:
            return {
                'action': 'Not Recommended',
                'reason': 'Negative impact on profitability',
                'risk_level': 'High'
            }
    
    def _save_scenario(self, result, elasticity):
        """Save scenario to database"""
        try:
            scenario = Scenario(
                name=result['scenario_name'],
                description=f"Simulation of {result['pricing']['price_change_percent']}% price change",
                product_id=result['product_id'],
                current_price=result['pricing']['current_price'],
                new_price=result['pricing']['new_price'],
                price_change_percent=result['pricing']['price_change_percent'],
                current_demand=result['demand']['current_daily_quantity'],
                predicted_demand=result['demand']['predicted_daily_quantity'],
                demand_change_percent=result['demand']['quantity_change_percent'],
                current_revenue=result['revenue']['current_daily_revenue'],
                predicted_revenue=result['revenue']['predicted_daily_revenue'],
                revenue_change_percent=result['revenue']['revenue_change_percent'],
                current_profit=result['profit']['current_daily_profit'],
                predicted_profit=result['profit']['predicted_daily_profit'],
                profit_change_percent=result['profit']['profit_change_percent'],
                simulation_days=result['simulation_days'],
                elasticity_used=elasticity
            )
            
            db.session.add(scenario)
            db.session.commit()
            
            result['scenario_id'] = scenario.id
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving scenario: {e}")
    
    def compare_scenarios(self, scenario_ids):
        """Compare multiple scenarios side by side"""
        scenarios = Scenario.query.filter(Scenario.id.in_(scenario_ids)).all()
        
        if not scenarios:
            return {'error': 'No scenarios found'}
        
        comparison = {
            'scenarios': [],
            'best_for_revenue': None,
            'best_for_profit': None,
            'best_for_volume': None
        }
        
        max_revenue_change = float('-inf')
        max_profit_change = float('-inf')
        max_volume_change = float('-inf')
        
        for scenario in scenarios:
            scenario_data = scenario.to_dict()
            comparison['scenarios'].append(scenario_data)
            
            if scenario.revenue_change_percent > max_revenue_change:
                max_revenue_change = scenario.revenue_change_percent
                comparison['best_for_revenue'] = scenario_data
            
            if scenario.profit_change_percent > max_profit_change:
                max_profit_change = scenario.profit_change_percent
                comparison['best_for_profit'] = scenario_data
            
            if scenario.demand_change_percent > max_volume_change:
                max_volume_change = scenario.demand_change_percent
                comparison['best_for_volume'] = scenario_data
        
        return comparison
    
    def simulate_competitive_response(self, product_id, our_price_change, competitor_response):
        """
        Simulate scenario with competitive response
        
        Args:
            product_id: Product ID
            our_price_change: Our price change percentage
            competitor_response: Dict with competitor response {delay_days, match_percent}
        """
        product = Product.query.get(product_id)
        if not product:
            return {'error': 'Product not found'}
        
        current_price = product.current_price
        new_price = current_price * (1 + our_price_change / 100)
        
        # Phase 1: Before competitor responds
        phase1 = self.simulate_scenario(
            product_id, 
            new_price, 
            simulation_days=competitor_response.get('delay_days', 7),
            scenario_name="Phase 1: Before Competitor Response"
        )
        
        # Phase 2: After competitor responds
        # Adjust elasticity based on competitor matching
        match_percent = competitor_response.get('match_percent', 100)
        
        # If competitor matches, our price advantage is reduced
        effective_price_change = our_price_change * (1 - match_percent / 100)
        effective_new_price = current_price * (1 + effective_price_change / 100)
        
        phase2 = self.simulate_scenario(
            product_id,
            effective_new_price,
            simulation_days=30,
            scenario_name="Phase 2: After Competitor Response"
        )
        
        return {
            'product_id': product_id,
            'product_name': product.name,
            'our_price_change': our_price_change,
            'competitor': {
                'delay_days': competitor_response.get('delay_days'),
                'match_percent': match_percent
            },
            'phase1': phase1,
            'phase2': phase2,
            'summary': {
                'total_revenue_impact': (
                    phase1['revenue']['total_revenue_change'] + 
                    phase2['revenue']['total_revenue_change']
                ),
                'total_profit_impact': (
                    phase1['profit']['total_profit_change'] + 
                    phase2['profit']['total_profit_change']
                )
            }
        }
    
    def simulate_seasonal_scenario(self, product_id, new_price, season):
        """Simulate scenario with seasonal adjustments"""
        # Get seasonal multipliers from historical data
        sales = Sale.query.filter_by(product_id=product_id).all()
        
        df = pd.DataFrame([{
            'season': sale.season,
            'quantity': sale.quantity
        } for sale in sales if sale.season])
        
        if df.empty:
            return self.simulate_scenario(product_id, new_price, 30)
        
        # Calculate seasonal factors
        avg_quantity = df['quantity'].mean()
        seasonal_factors = df.groupby('season')['quantity'].mean() / avg_quantity
        
        season_factor = seasonal_factors.get(season, 1.0)
        
        # Run base simulation
        base_scenario = self.simulate_scenario(product_id, new_price, 30)
        
        # Adjust for seasonality
        base_scenario['demand']['predicted_daily_quantity'] *= season_factor
        base_scenario['demand']['seasonal_adjustment'] = season_factor
        base_scenario['demand']['season'] = season
        
        # Recalculate revenue and profit
        pred_qty = base_scenario['demand']['predicted_daily_quantity']
        pred_rev = new_price * pred_qty
        
        product = Product.query.get(product_id)
        pred_profit = (new_price - product.unit_cost) * pred_qty
        
        base_scenario['revenue']['predicted_daily_revenue'] = round(pred_rev, 2)
        base_scenario['profit']['predicted_daily_profit'] = round(pred_profit, 2)
        
        return base_scenario
    
    def bulk_simulate(self, product_ids, price_changes):
        """
        Simulate multiple price changes across multiple products
        
        Args:
            product_ids: List of product IDs
            price_changes: List of price change percentages
            
        Returns:
            dict: Results for all combinations
        """
        results = []
        
        for product_id in product_ids:
            product = Product.query.get(product_id)
            if not product:
                continue
            
            for price_change in price_changes:
                new_price = product.current_price * (1 + price_change / 100)
                
                scenario = self.simulate_scenario(
                    product_id,
                    new_price,
                    simulation_days=30,
                    scenario_name=f"{product.name} - {price_change:+.1f}%"
                )
                
                if 'error' not in scenario:
                    results.append(scenario)
        
        # Aggregate results
        total_revenue_impact = sum(r['revenue']['total_revenue_change'] for r in results)
        total_profit_impact = sum(r['profit']['total_profit_change'] for r in results)
        
        return {
            'scenarios': results,
            'summary': {
                'total_scenarios': len(results),
                'total_revenue_impact': round(total_revenue_impact, 2),
                'total_profit_impact': round(total_profit_impact, 2),
                'average_revenue_change_percent': round(
                    sum(r['revenue']['revenue_change_percent'] for r in results) / len(results), 2
                ) if results else 0
            }
        }
