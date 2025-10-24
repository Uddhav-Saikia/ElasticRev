# ElasticRev Backend

Dynamic Pricing Optimization API using demand elasticity analysis.

## 🚀 Quick Start

### Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Mac/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the development server**
   ```bash
   python app.py
   ```

   Server runs at `http://localhost:5000`

### Production Deployment (Render)

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for comprehensive deployment instructions.

**Quick steps:**
1. Create PostgreSQL database on Render
2. Create web service pointing to this `backend` directory
3. Set environment variables (see `.env.example`)
4. Deploy!

Use [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) to ensure everything is configured correctly.

## 📁 Project Structure

```
backend/
├── app.py                    # Main Flask application
├── config.py                 # Configuration (DB, CORS, etc.)
├── models.py                 # SQLAlchemy database models
├── elasticity.py             # Elasticity calculation engine
├── scenarios.py              # Scenario simulation logic
├── database.py               # Database utilities
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version (3.11.8)
├── pyproject.toml           # Build system configuration
├── .env.example             # Environment variables template
├── RENDER_DEPLOYMENT.md     # Deployment guide
└── DEPLOYMENT_CHECKLIST.md  # Pre-flight checklist
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
DATABASE_URL=postgresql://user:pass@host:port/db  # PostgreSQL in production
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DEBUG=False
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Database

- **Development**: SQLite (auto-created in `../database/elasticrev.db`)
- **Production**: PostgreSQL (set `DATABASE_URL`)

The app automatically uses the right database based on `DATABASE_URL` presence.

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Products
```
GET    /api/products          # List all products
POST   /api/products          # Create product
GET    /api/products/:id      # Get product details
PUT    /api/products/:id      # Update product
DELETE /api/products/:id      # Delete product
```

### Sales Data
```
POST   /api/sales             # Upload sales data
GET    /api/sales             # Get sales data
```

### Elasticity Analysis
```
POST   /api/elasticity/calculate    # Calculate elasticity
GET    /api/elasticity/results      # Get results
```

### Scenarios
```
POST   /api/scenarios         # Run scenario simulation
GET    /api/scenarios         # Get scenarios
```

### Reports
```
GET    /api/export/excel      # Export analysis to Excel
```

## 🧪 Testing

Run tests (when available):
```bash
pytest
```

## 📦 Dependencies

Key packages:
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **pandas** - Data manipulation
- **scikit-learn** - Machine learning
- **openpyxl** - Excel export
- **gunicorn** - Production WSGI server
- **psycopg2-binary** - PostgreSQL adapter

See [requirements.txt](./requirements.txt) for complete list.

## 🔐 Security

- Never commit `.env` files
- Use strong `SECRET_KEY` in production
- Keep `DATABASE_URL` private
- Set `DEBUG=False` in production
- Restrict `CORS_ORIGINS` to your domains

## 🐛 Troubleshooting

### "metadata-generation-failed" on Render
- Ensure `runtime.txt` specifies `python-3.11.8`
- Check `pyproject.toml` exists
- Review build logs for specific errors

### Database Connection Error
- Verify `DATABASE_URL` is correct
- Use Internal Database URL on Render (not External)
- Ensure database and web service are in same region

### CORS Errors
- Add your frontend URL to `CORS_ORIGINS`
- Format: comma-separated, no spaces
- Example: `https://app1.com,https://app2.com`

### Import Errors
- Activate virtual environment
- Run `pip install -r requirements.txt`
- Check Python version matches `runtime.txt`

## 📚 Resources

- [Render Documentation](https://render.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

## 📄 License

See root repository for license information.

---

Built with ❤️ for dynamic pricing optimization
