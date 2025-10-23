from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, Index

db = SQLAlchemy()

class Product(db.Model):
    """Product catalog with pricing information"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    subcategory = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    unit_cost = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = db.relationship('Sale', back_populates='product', lazy='dynamic')
    price_history = db.relationship('PriceHistory', back_populates='product', lazy='dynamic')
    elasticity_results = db.relationship('ElasticityResult', back_populates='product', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'brand': self.brand,
            'unit_cost': self.unit_cost,
            'current_price': self.current_price,
            'currency': self.currency,
            'margin': round(((self.current_price - self.unit_cost) / self.current_price) * 100, 2),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Sale(db.Model):
    """Historical sales transactions"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, default=0)
    competitor_price = db.Column(db.Float)
    season = db.Column(db.String(20))
    day_of_week = db.Column(db.String(10))
    is_holiday = db.Column(db.Boolean, default=False)
    promotion_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', back_populates='sales')
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_product_date', 'product_id', 'date'),
        Index('idx_date_range', 'date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'date': self.date.isoformat() if self.date else None,
            'quantity': self.quantity,
            'price': self.price,
            'revenue': self.revenue,
            'cost': self.cost,
            'profit': self.profit,
            'margin': round((self.profit / self.revenue) * 100, 2) if self.revenue > 0 else 0,
            'discount_percent': self.discount_percent,
            'competitor_price': self.competitor_price,
            'season': self.season,
            'day_of_week': self.day_of_week,
            'is_holiday': self.is_holiday,
            'promotion_active': self.promotion_active
        }


class PriceHistory(db.Model):
    """Price change tracking"""
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    old_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    change_percent = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.Date, nullable=False, index=True)
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    # Relationships
    product = db.relationship('Product', back_populates='price_history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'old_price': self.old_price,
            'new_price': self.new_price,
            'change_percent': self.change_percent,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }


class ElasticityResult(db.Model):
    """Calculated price elasticity results"""
    __tablename__ = 'elasticity_results'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    elasticity_coefficient = db.Column(db.Float, nullable=False)
    elasticity_type = db.Column(db.String(50))  # elastic, inelastic, unit_elastic
    r_squared = db.Column(db.Float)
    sample_size = db.Column(db.Integer)
    model_type = db.Column(db.String(50))  # linear_regression, gradient_boosting
    confidence_interval_lower = db.Column(db.Float)
    confidence_interval_upper = db.Column(db.Float)
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    
    # Recommendations based on elasticity
    recommended_action = db.Column(db.String(100))
    optimal_price = db.Column(db.Float)
    expected_revenue_change = db.Column(db.Float)
    
    # Relationships
    product = db.relationship('Product', back_populates='elasticity_results')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'elasticity_coefficient': self.elasticity_coefficient,
            'elasticity_type': self.elasticity_type,
            'r_squared': self.r_squared,
            'sample_size': self.sample_size,
            'model_type': self.model_type,
            'confidence_interval': {
                'lower': self.confidence_interval_lower,
                'upper': self.confidence_interval_upper
            },
            'calculation_date': self.calculation_date.isoformat() if self.calculation_date else None,
            'period': {
                'start': self.period_start.isoformat() if self.period_start else None,
                'end': self.period_end.isoformat() if self.period_end else None
            },
            'recommended_action': self.recommended_action,
            'optimal_price': self.optimal_price,
            'expected_revenue_change': self.expected_revenue_change
        }


class Scenario(db.Model):
    """What-if scenario simulations"""
    __tablename__ = 'scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)
    
    # Scenario parameters
    current_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    price_change_percent = db.Column(db.Float, nullable=False)
    
    # Predictions
    current_demand = db.Column(db.Float)
    predicted_demand = db.Column(db.Float)
    demand_change_percent = db.Column(db.Float)
    
    current_revenue = db.Column(db.Float)
    predicted_revenue = db.Column(db.Float)
    revenue_change_percent = db.Column(db.Float)
    
    current_profit = db.Column(db.Float)
    predicted_profit = db.Column(db.Float)
    profit_change_percent = db.Column(db.Float)
    
    # Metadata
    simulation_days = db.Column(db.Integer, default=30)
    elasticity_used = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    product = db.relationship('Product')
    
    def to_dict(self):
        # Calculate recommendation based on scenario results
        recommendation = self._calculate_recommendation()
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'pricing': {
                'current_price': self.current_price,
                'new_price': self.new_price,
                'price_change_percent': self.price_change_percent
            },
            'demand': {
                'current': self.current_demand,
                'predicted': self.predicted_demand,
                'change_percent': self.demand_change_percent,
                'quantity_change_percent': self.demand_change_percent  # Frontend expects this name
            },
            'revenue': {
                'current': self.current_revenue,
                'predicted': self.predicted_revenue,
                'change_percent': self.revenue_change_percent,
                'revenue_change_percent': self.revenue_change_percent,  # Frontend expects this name
                'total_revenue_change': (self.predicted_revenue - self.current_revenue) if (self.predicted_revenue and self.current_revenue) else 0
            },
            'profit': {
                'current': self.current_profit,
                'predicted': self.predicted_profit,
                'change_percent': self.profit_change_percent,
                'profit_change_percent': self.profit_change_percent,  # Frontend expects this name
                'total_profit_change': (self.predicted_profit - self.current_profit) if (self.predicted_profit and self.current_profit) else 0
            },
            'recommendation': recommendation,
            'simulation_days': self.simulation_days,
            'elasticity_used': self.elasticity_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def _calculate_recommendation(self):
        """Calculate recommendation based on scenario results"""
        if not all([self.profit_change_percent, self.revenue_change_percent, self.demand_change_percent]):
            return None
        
        # Determine recommendation action based on profit and revenue impact
        profit_positive = self.profit_change_percent > 0
        revenue_positive = self.revenue_change_percent > 0
        
        # Calculate a composite score
        score = (self.profit_change_percent * 0.5) + (self.revenue_change_percent * 0.3) + (self.demand_change_percent * 0.2)
        
        if score > 5 and profit_positive and revenue_positive:
            action = 'Highly Recommended'
            reason = f'Excellent profit (+{self.profit_change_percent:.1f}%) and revenue (+{self.revenue_change_percent:.1f}%) gains'
        elif score > 2 and profit_positive:
            action = 'Recommended'
            reason = f'Positive profit impact (+{self.profit_change_percent:.1f}%)'
        elif score > 0:
            action = 'Consider'
            reason = f'Mixed results: profit {self.profit_change_percent:+.1f}%, revenue {self.revenue_change_percent:+.1f}%'
        else:
            action = 'Not Recommended'
            reason = f'Negative impact: profit {self.profit_change_percent:+.1f}%, revenue {self.revenue_change_percent:+.1f}%'
        
        return {
            'action': action,
            'reason': reason,
            'score': round(score, 2)
        }


class CompetitorPrice(db.Model):
    """Competitor pricing data"""
    __tablename__ = 'competitor_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    competitor_name = db.Column(db.String(100), nullable=False)
    competitor_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product')
    
    __table_args__ = (
        Index('idx_competitor_product_date', 'product_id', 'competitor_name', 'date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'competitor_name': self.competitor_name,
            'competitor_price': self.competitor_price,
            'date': self.date.isoformat() if self.date else None,
            'url': self.url
        }
