import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
# Use PostgreSQL for production, SQLite for development
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production: Use PostgreSQL (Render, Vercel, etc.)
    # Fix for SQLAlchemy 1.4+ postgres:// -> postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    # Development: Use SQLite
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'elasticrev.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')

# Create directories if they don't exist
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# API Configuration
API_PREFIX = '/api'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

# ML Model Configuration
ELASTICITY_MODELS = {
    'linear_regression': {
        'name': 'Linear Regression',
        'enabled': True
    },
    'gradient_boosting': {
        'name': 'Gradient Boosting',
        'enabled': True,
        'params': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 3
        }
    }
}

# Business Rules
PRICE_CHANGE_LIMITS = {
    'min_discount': -30,  # Max 30% discount
    'max_increase': 20,   # Max 20% increase
}

# Elasticity Thresholds
ELASTICITY_CATEGORIES = {
    'highly_elastic': -2.0,      # |e| > 2
    'elastic': -1.0,             # 1 < |e| <= 2
    'unit_elastic': -0.9,        # |e| ≈ 1
    'inelastic': 0               # |e| < 1
}

# Scenario Simulation Parameters
SIMULATION_DAYS = [30, 60, 90, 180]  # Default simulation periods
CONFIDENCE_LEVEL = 0.95

# Excel Export Configuration
EXCEL_TEMPLATES = {
    'pricing_strategy': {
        'sheets': ['Summary', 'Elasticity', 'Scenarios', 'Recommendations']
    }
}

# CORS Configuration
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:3001']

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'elasticrev.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
