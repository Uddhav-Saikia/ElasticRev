# ElasticRev - Dynamic Pricing Optimization using Demand Elasticity

## 🎯 Project Overview

ElasticRev is a comprehensive data-driven pricing optimization platform that helps businesses maximize revenue and profit margins through demand elasticity analysis and intelligent pricing strategies.

## 🌟 Key Features

### Analytics & Modeling
- **Price Elasticity Analysis**: Calculate demand elasticity coefficients for products
- **Machine Learning Models**: Gradient boosting and regression models for demand prediction
- **Historical Analysis**: Analyze sales patterns, seasonality, and price sensitivity
- **Product Segmentation**: Categorize products by elasticity characteristics

### Business Intelligence
- **What-If Scenarios**: Simulate revenue/margin impacts of pricing changes
- **Dynamic Pricing Recommendations**: AI-powered optimal price suggestions
- **Competitor Analysis**: Track and respond to market pricing
- **Revenue Optimization**: Maximize revenue vs. volume trade-offs
- **Margin Analysis**: Understand profit implications of pricing decisions

### Visualization & Reporting
- **Interactive Dashboard**: Real-time charts and KPIs
- **Elasticity Curves**: Visual demand response to price changes
- **Revenue Projections**: Forecast outcomes of pricing strategies
- **Excel Reports**: Exportable pricing strategy documents
- **Comparative Analysis**: Before/after scenario comparisons

### Data Management
- **SQL Data Extraction**: Query historical sales and pricing data
- **Data Upload**: Import CSV/Excel sales data
- **Database Management**: SQLite backend for data persistence
- **Real-time Updates**: Live data synchronization

## 🏗️ Technology Stack

### Backend
- **Python 3.9+**
- **Flask**: REST API framework
- **SQLAlchemy**: Database ORM
- **Pandas & NumPy**: Data manipulation
- **Scikit-learn**: ML models (Gradient Boosting, Linear Regression)
- **Statsmodels**: Statistical analysis
- **OpenPyXL**: Excel generation

### Frontend
- **React 18**: UI framework
- **Axios**: HTTP client
- **Recharts**: Data visualization
- **Tailwind CSS**: Styling
- **React Query**: State management

### Database
- **SQLite**: Relational database
- **SQL**: Data extraction and analysis

## 📁 Project Structure

```
ElasticRev/
├── backend/
│   ├── app.py                 # Flask application
│   ├── models.py              # Database models
│   ├── elasticity.py          # Price elasticity calculations
│   ├── ml_models.py           # Machine learning models
│   ├── scenarios.py           # What-if scenario engine
│   ├── database.py            # Database utilities
│   ├── config.py              # Configuration
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   ├── pages/             # Page components
│   │   └── App.jsx            # Main app
│   ├── package.json
│   └── public/
├── data/
│   ├── sales_data.csv         # Historical sales data
│   ├── products.csv           # Product catalog
│   ├── competitors.csv        # Competitor pricing
│   └── generate_data.py       # Data generation script
├── database/
│   └── schema.sql             # Database schema
├── docs/
│   ├── API.md                 # API documentation
│   └── SETUP.md               # Setup guide
└── scripts/
    └── run.sh                 # Launch script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ElasticRev.git
cd ElasticRev
```

2. **Setup Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Setup Frontend**
```bash
cd frontend
npm install
```

4. **Generate Sample Data**
```bash
cd data
python generate_data.py
```

5. **Initialize Database**
```bash
cd backend
python database.py
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
# Backend runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
# Frontend runs on http://localhost:3000
```

## 📊 Business Impact

- **Revenue Optimization**: Data-backed pricing strategies increase revenue by 8-15%
- **Margin Improvement**: Identify optimal price points for maximum profitability
- **Competitive Advantage**: Real-time pricing adjustments based on demand elasticity
- **Risk Reduction**: Simulate pricing changes before implementation
- **Strategic Insights**: Understand customer price sensitivity by product/segment

## 🔧 API Endpoints

### Data Management
- `GET /api/products` - Get all products
- `GET /api/sales` - Get sales history
- `POST /api/upload` - Upload sales data

### Analysis
- `POST /api/elasticity/calculate` - Calculate price elasticity
- `GET /api/elasticity/products/:id` - Get product elasticity
- `POST /api/scenarios/simulate` - Run what-if scenario
- `GET /api/recommendations` - Get pricing recommendations

### Reports
- `GET /api/export/excel` - Export pricing strategy report

## 📈 Usage Examples

### Calculate Price Elasticity
```python
# Price elasticity = % change in quantity / % change in price
# Elastic: |elasticity| > 1 (demand sensitive to price)
# Inelastic: |elasticity| < 1 (demand insensitive to price)
```

### What-If Scenario
```javascript
// Simulate 5% price decrease
const scenario = {
  productId: 1,
  priceChange: -5,  // percentage
  duration: 30      // days
}
// Returns: predicted revenue, volume, margin impacts
```

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

## 📝 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

Built with ❤️ for data-driven business optimization

## 📞 Support

For issues and questions, please open a GitHub issue.

---

**Last Updated**: October 2025
