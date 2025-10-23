# ElasticRev - System Architecture & Data Flow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│                     http://localhost:3000                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND (Port 3000)                    │
├─────────────────────────────────────────────────────────────────┤
│  Components:                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  Dashboard   │ │   Products   │ │  Elasticity  │            │
│  │   - KPIs     │ │   - List     │ │  - Calculate │            │
│  │   - Charts   │ │   - Search   │ │  - Results   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐                              │
│  │  Scenarios   │ │Recommendations│                              │
│  │  - Simulate  │ │  - AI Suggest│                              │
│  └──────────────┘ └──────────────┘                              │
│                                                                   │
│  State Management: React Query                                   │
│  Styling: Tailwind CSS                                           │
│  Charts: Recharts                                                │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP REST API
                             │ (Axios)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND (Port 5000)                     │
├─────────────────────────────────────────────────────────────────┤
│  API Endpoints (app.py):                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /api/products          - Product catalog                  │  │
│  │ /api/sales             - Sales history                    │  │
│  │ /api/elasticity        - Price elasticity analysis        │  │
│  │ /api/scenarios         - What-if simulations              │  │
│  │ /api/recommendations   - AI pricing suggestions           │  │
│  │ /api/analytics         - Dashboard metrics                │  │
│  │ /api/export/excel      - Report generation                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Business Logic:                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ elasticity.py│ │ scenarios.py │ │  models.py   │            │
│  │  - Linear    │ │  - Simulate  │ │  - ORM       │            │
│  │    Regression│ │  - Compare   │ │  - Schema    │            │
│  │  - Gradient  │ │  - Optimize  │ │              │            │
│  │    Boosting  │ │              │ │              │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                   │
│  ML Libraries: scikit-learn, statsmodels, pandas, numpy         │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQLAlchemy ORM
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SQLITE DATABASE                                │
│                database/elasticrev.db                            │
├─────────────────────────────────────────────────────────────────┤
│  Tables:                                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ products          - Product catalog (50 rows)             │  │
│  │   ├─ id, sku, name, category, price, cost                │  │
│  │   └─ Primary Key: id                                      │  │
│  │                                                            │  │
│  │ sales             - Sales transactions (35,000+ rows)     │  │
│  │   ├─ id, product_id, date, quantity, price, revenue      │  │
│  │   └─ Foreign Key: product_id → products.id               │  │
│  │                                                            │  │
│  │ elasticity_results - Calculated elasticity                │  │
│  │   ├─ id, product_id, coefficient, type, r_squared        │  │
│  │   └─ Foreign Key: product_id → products.id               │  │
│  │                                                            │  │
│  │ scenarios         - What-if simulations                   │  │
│  │   ├─ id, product_id, new_price, predictions              │  │
│  │   └─ Foreign Key: product_id → products.id               │  │
│  │                                                            │  │
│  │ competitor_prices - Competitor data                       │  │
│  │   ├─ id, product_id, competitor, price, date             │  │
│  │   └─ Foreign Key: product_id → products.id               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ▲
                             │ Data Loading
                             │
┌─────────────────────────────────────────────────────────────────┐
│                        DATA GENERATION                           │
│                   data/generate_data.py                          │
├─────────────────────────────────────────────────────────────────┤
│  Generates:                                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ products.csv       - 50 products                          │  │
│  │   - 6 categories                                          │  │
│  │   - Realistic pricing ($2-$2000)                          │  │
│  │   - Various brands                                        │  │
│  │                                                            │  │
│  │ sales_data.csv     - 35,000+ transactions                 │  │
│  │   - 2 years history (2023-2024)                          │  │
│  │   - Seasonal patterns                                     │  │
│  │   - Holiday effects                                       │  │
│  │   - Promotions                                            │  │
│  │                                                            │  │
│  │ competitors.csv    - Competitor pricing                   │  │
│  │   - 4 competitors                                         │  │
│  │   - Weekly price tracking                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### 1. Elasticity Calculation Flow

```
┌──────────┐
│  User    │
│ clicks   │
│"Calculate│
│Elasticity│
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ Frontend: ProductDetail.jsx              │
│ - Calls API: calculateElasticity()      │
└────┬────────────────────────────────────┘
     │ POST /api/elasticity/calculate
     │ { product_id: 1, model_type: "gradient_boosting" }
     ▼
┌─────────────────────────────────────────┐
│ Backend: app.py                          │
│ - Receives request                       │
│ - Validates product_id                   │
│ - Calls ElasticityCalculator             │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ Backend: elasticity.py                   │
│ Step 1: Query sales data from database  │
│   SELECT * FROM sales WHERE product_id=1 │
│                                          │
│ Step 2: Prepare data                     │
│   - log(price), log(quantity)           │
│   - Add features (discount, holiday...)  │
│                                          │
│ Step 3: Train ML model                   │
│   - Gradient Boosting Regressor         │
│   - Fit on price vs quantity            │
│                                          │
│ Step 4: Calculate elasticity             │
│   - Partial derivative dQ/dP             │
│   - Bootstrap confidence intervals       │
│                                          │
│ Step 5: Classify elasticity type         │
│   - Elastic, Inelastic, or Unit         │
│                                          │
│ Step 6: Generate recommendations         │
│   - Optimal price                        │
│   - Expected revenue change              │
│                                          │
│ Step 7: Save to database                 │
│   INSERT INTO elasticity_results...     │
└────┬────────────────────────────────────┘
     │
     │ Returns: { elasticity_coefficient: -1.5,
     │            elasticity_type: "elastic",
     │            optimal_price: 94.99,
     │            expected_revenue_change: 8.5 }
     ▼
┌─────────────────────────────────────────┐
│ Frontend: ProductDetail.jsx              │
│ - Updates UI with results                │
│ - Shows elasticity curve chart           │
│ - Displays recommendations               │
└─────────────────────────────────────────┘
```

### 2. Scenario Simulation Flow

```
┌──────────┐
│  User    │
│ enters   │
│new price │
│& clicks  │
│"Simulate"│
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ Frontend: Scenarios.jsx                  │
│ - Calls API: simulateScenario()         │
└────┬────────────────────────────────────┘
     │ POST /api/scenarios/simulate
     │ { product_id: 1, new_price: 89.99, simulation_days: 30 }
     ▼
┌─────────────────────────────────────────┐
│ Backend: scenarios.py                    │
│                                          │
│ Step 1: Get product & elasticity        │
│   SELECT * FROM products WHERE id=1      │
│   SELECT * FROM elasticity_results...    │
│                                          │
│ Step 2: Calculate price change           │
│   price_change_pct = (89.99-99.99)/99.99│
│   = -10%                                 │
│                                          │
│ Step 3: Predict quantity change          │
│   quantity_change = elasticity * price_change│
│   = -1.5 * (-10%) = +15%                │
│                                          │
│ Step 4: Calculate new metrics            │
│   new_quantity = old_quantity * 1.15    │
│   new_revenue = new_price * new_quantity│
│   new_profit = (price-cost) * quantity  │
│                                          │
│ Step 5: Generate recommendation          │
│   - Compare current vs predicted         │
│   - Assess risk level                    │
│   - Provide action advice                │
│                                          │
│ Step 6: Save scenario                    │
│   INSERT INTO scenarios...               │
└────┬────────────────────────────────────┘
     │
     │ Returns: { pricing: {...},
     │            demand: {...},
     │            revenue: {...},
     │            profit: {...},
     │            recommendation: {...} }
     ▼
┌─────────────────────────────────────────┐
│ Frontend: Scenarios.jsx                  │
│ - Display results in cards               │
│ - Show green/red indicators              │
│ - Add to scenarios table                 │
└─────────────────────────────────────────┘
```

## Machine Learning Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    PRICE ELASTICITY ML PIPELINE              │
└─────────────────────────────────────────────────────────────┘

Step 1: Data Collection
┌────────────────────────────────┐
│ Historical Sales Data          │
│ - Dates, Prices, Quantities    │
│ - Discounts, Promotions        │
│ - Seasonal factors             │
│ - Competitor prices            │
└────────────┬───────────────────┘
             │
             ▼
Step 2: Feature Engineering
┌────────────────────────────────┐
│ Transform Features             │
│ - log(price)                   │
│ - log(quantity)                │
│ - discount_percent             │
│ - is_holiday (0/1)             │
│ - promotion_active (0/1)       │
│ - log(competitor_price)        │
└────────────┬───────────────────┘
             │
             ▼
Step 3: Model Selection
┌────────────────────────────────┐
│ Two Models Available:          │
│                                │
│ A. Linear Regression           │
│    - Fast, interpretable       │
│    - OLS with statsmodels      │
│    - Good for simple patterns  │
│                                │
│ B. Gradient Boosting           │
│    - More accurate             │
│    - Handles non-linearity     │
│    - Better for complex data   │
└────────────┬───────────────────┘
             │
             ▼
Step 4: Model Training
┌────────────────────────────────┐
│ Fit Model:                     │
│   X = [log_price, ...]         │
│   y = [log_quantity]           │
│                                │
│   model.fit(X, y)              │
│                                │
│ Cross-validation (k=5)         │
│ Calculate R² score             │
└────────────┬───────────────────┘
             │
             ▼
Step 5: Elasticity Extraction
┌────────────────────────────────┐
│ Extract Coefficient:           │
│                                │
│ Linear: β₁ from regression     │
│         elasticity = β₁        │
│                                │
│ GBoost: ∂Q/∂P at mean price   │
│         numerical derivative   │
└────────────┬───────────────────┘
             │
             ▼
Step 6: Confidence Intervals
┌────────────────────────────────┐
│ Calculate Uncertainty:         │
│                                │
│ Linear: From OLS standard error│
│         95% confidence interval│
│                                │
│ GBoost: Bootstrap method       │
│         100 iterations         │
│         Percentile intervals   │
└────────────┬───────────────────┘
             │
             ▼
Step 7: Classification
┌────────────────────────────────┐
│ Classify Elasticity Type:      │
│                                │
│ if |e| > 2:    highly_elastic  │
│ elif |e| > 1:  elastic         │
│ elif 0.9<|e|<1.1: unit_elastic│
│ else:          inelastic       │
└────────────┬───────────────────┘
             │
             ▼
Step 8: Business Insights
┌────────────────────────────────┐
│ Generate Recommendations:      │
│                                │
│ Elastic:                       │
│   → Decrease price             │
│   → Increase volume & revenue  │
│                                │
│ Inelastic:                     │
│   → Increase price             │
│   → Increase margin & profit   │
│                                │
│ Calculate optimal price:       │
│   P* = Cost × (e/(e+1))       │
└────────────┬───────────────────┘
             │
             ▼
Step 9: Validation & Storage
┌────────────────────────────────┐
│ - Check model quality (R²)     │
│ - Validate predictions         │
│ - Store in database            │
│ - Return to frontend           │
└────────────────────────────────┘
```

## Database Schema Relationships

```
┌────────────────────────────────┐
│          products              │
├────────────────────────────────┤
│ PK  id                         │
│     sku (unique)               │
│     name                       │
│     category                   │
│     subcategory                │
│     brand                      │
│     unit_cost                  │
│     current_price              │
│     currency                   │
│     created_at                 │
│     updated_at                 │
└────────┬───────────────────────┘
         │ 1:N
         │
         ├──────────────────────────────────────┐
         │                                      │
         │ 1:N                                  │ 1:N
┌────────▼───────────────┐          ┌──────────▼─────────────┐
│        sales            │          │  elasticity_results    │
├─────────────────────────┤          ├────────────────────────┤
│ PK  id                  │          │ PK  id                 │
│ FK  product_id          │          │ FK  product_id         │
│     date                │          │     coefficient        │
│     quantity            │          │     elasticity_type    │
│     price               │          │     r_squared          │
│     revenue             │          │     sample_size        │
│     cost                │          │     model_type         │
│     profit              │          │     conf_interval_low  │
│     discount_percent    │          │     conf_interval_high │
│     competitor_price    │          │     calculation_date   │
│     season              │          │     period_start       │
│     day_of_week         │          │     period_end         │
│     is_holiday          │          │     recommended_action │
│     promotion_active    │          │     optimal_price      │
│     created_at          │          │     expected_rev_change│
└─────────────────────────┘          └────────────────────────┘
         │ 1:N                                  │
         │                                      │
         │                         ┌────────────▼────────────┐
         │                         │      scenarios          │
         │                         ├─────────────────────────┤
         │                         │ PK  id                  │
         │                         │ FK  product_id          │
         │                         │     name                │
         │                         │     description         │
         │                         │     current_price       │
         │                         │     new_price           │
         │                         │     price_change_pct    │
         │                         │     current_demand      │
         │                         │     predicted_demand    │
         │                         │     demand_change_pct   │
         │                         │     current_revenue     │
         │                         │     predicted_revenue   │
         │                         │     revenue_change_pct  │
         │                         │     current_profit      │
         │                         │     predicted_profit    │
         │                         │     profit_change_pct   │
         │                         │     simulation_days     │
         │                         │     elasticity_used     │
         │                         │     created_at          │
         │                         └─────────────────────────┘
         │ 1:N
         │
┌────────▼───────────────┐
│  competitor_prices      │
├─────────────────────────┤
│ PK  id                  │
│ FK  product_id          │
│     competitor_name     │
│     competitor_price    │
│     date                │
│     url                 │
│     created_at          │
└─────────────────────────┘
```

## Technology Stack Details

```
┌─────────────────────────────────────────────────────────────┐
│                       FRONTEND STACK                         │
├─────────────────────────────────────────────────────────────┤
│ React 18.2.0              - UI framework                     │
│ Vite 5.0.7                - Build tool & dev server          │
│ React Router 6.20.0       - Navigation & routing             │
│ Axios 1.6.2               - HTTP client for API calls        │
│ React Query 3.39.3        - Server state management          │
│ Recharts 2.10.3           - Data visualization library       │
│ Lucide React 0.294.0      - Icon library                     │
│ Tailwind CSS 3.3.6        - Utility-first CSS framework      │
│ Date-fns 2.30.0           - Date manipulation                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       BACKEND STACK                          │
├─────────────────────────────────────────────────────────────┤
│ Flask 3.0.0               - Web framework                    │
│ Flask-CORS 4.0.0          - Cross-origin resource sharing    │
│ Flask-SQLAlchemy 3.1.1    - SQL toolkit & ORM               │
│ SQLAlchemy 2.0.23         - Database abstraction             │
│ Pandas 2.1.3              - Data manipulation & analysis     │
│ NumPy 1.26.2              - Numerical computing              │
│ Scikit-learn 1.3.2        - Machine learning library         │
│ Statsmodels 0.14.0        - Statistical modeling             │
│ SciPy 1.11.4              - Scientific computing             │
│ OpenPyXL 3.1.2            - Excel file generation            │
│ Matplotlib 3.8.2          - Plotting library                 │
│ Seaborn 0.13.0            - Statistical visualization        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                               │
├─────────────────────────────────────────────────────────────┤
│ SQLite 3                  - Embedded SQL database            │
│ Location: database/elasticrev.db                             │
│ Size: ~10-50 MB (depends on data)                           │
│ Tables: 5 (products, sales, elasticity, scenarios, comp)    │
│ Indexes: Multiple for query optimization                     │
└─────────────────────────────────────────────────────────────┘
```

This visual architecture document helps understand how all components work together!
