# Vercel Deployment for ElasticRev

This project can be deployed on Vercel with the following setup.

## Prerequisites

1. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository** - Your code must be in a GitHub repository
3. **Vercel CLI** (optional) - `npm install -g vercel`

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import Project**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Git Repository"
   - Select your GitHub repository
   - Vercel will auto-detect the configuration

3. **Configure Build Settings**:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: `npm run build:frontend`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `npm install`

4. **Add Environment Variables**:
   ```
   FLASK_ENV=production
   PYTHON_VERSION=3.9
   DATABASE_URL=<your-database-url>
   ```

5. **Deploy**: Click "Deploy" and wait for completion (2-3 minutes)

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```
   Follow the prompts to configure your project

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

## Important Notes

### Database Considerations

⚠️ **SQLite Limitation**: Vercel's serverless environment doesn't support SQLite file-based databases because:
- Files are read-only
- No persistent storage between requests
- Functions are stateless

**Solutions**:

1. **Use PostgreSQL (Recommended)**:
   ```bash
   # Sign up for free PostgreSQL at:
   # - Vercel Postgres
   # - Supabase
   # - Railway
   # - Neon
   ```

2. **Use Vercel KV (Redis)**:
   - For caching and session storage
   - Limited to key-value data

3. **Use External Database Service**:
   - Update `config.py` to use PostgreSQL connection string
   - Set `DATABASE_URL` environment variable

### API Routes

Since Vercel uses serverless functions, the backend needs to be adapted:

**Current Structure**:
```
backend/app.py (Flask app)
```

**Vercel Structure**:
```
api/
  index.py (serverless function)
  products.py
  elasticity.py
  scenarios.py
```

## Modified Configuration

### Update Backend for Vercel

I'll create a serverless-compatible version:

**File: `api/index.py`**
```python
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "environment": "vercel"})

# Import routes
from backend.app import app as backend_app

# This is the entry point for Vercel
def handler(request):
    return backend_app(request)
```

### Update Frontend API URL

**File: `frontend/.env.production`**
```
VITE_API_URL=/api
```

### Update Vite Config

```javascript
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

## Alternative: Split Deployment

### Deploy Frontend on Vercel

1. **Create `vercel.json` for frontend only**:
   ```json
   {
     "buildCommand": "cd frontend && npm install && npm run build",
     "outputDirectory": "frontend/dist",
     "framework": "vite",
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```

2. **Deploy frontend**: `vercel --prod`

### Deploy Backend on Render/Railway

1. Deploy backend separately on Render (as previously described)
2. Update frontend environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

## Troubleshooting

### Build Fails

**Issue**: Python dependencies fail
```bash
# Solution: Use requirements.txt with compatible versions
pip freeze > backend/requirements.txt
```

**Issue**: Node version mismatch
```bash
# Add to package.json:
"engines": {
  "node": "18.x",
  "npm": "9.x"
}
```

### Database Connection Issues

**Issue**: SQLite not working
```bash
# Solution 1: Use PostgreSQL
DATABASE_URL=postgresql://user:pass@host/db

# Solution 2: Use in-memory SQLite (data lost on restart)
DATABASE_URL=sqlite:///:memory:
```

### API Routes Not Working

**Issue**: 404 on API calls
```bash
# Check vercel.json routes configuration
# Ensure /api/* routes to backend
```

### CORS Errors

**Issue**: CORS policy blocking requests
```python
# Update backend/app.py
CORS(app, origins=['https://your-app.vercel.app', 'http://localhost:3000'])
```

## Production Checklist

- [ ] Code pushed to GitHub
- [ ] Database migrated to PostgreSQL
- [ ] Environment variables configured
- [ ] API routes tested
- [ ] CORS configured for production domain
- [ ] Frontend builds successfully
- [ ] Backend functions deploy successfully
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active

## Recommended Architecture for Vercel

```
┌─────────────────────┐
│   Vercel Frontend   │
│   (Static Site)     │
└──────────┬──────────┘
           │
           ↓ API Calls
┌─────────────────────┐
│  Render Backend     │
│  (Flask API)        │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  PostgreSQL DB      │
│  (Supabase/Neon)    │
└─────────────────────┘
```

This split architecture provides:
- ✅ Fast global frontend delivery (Vercel CDN)
- ✅ Reliable backend with persistent storage (Render)
- ✅ Scalable database (PostgreSQL)

## Cost Breakdown

**Vercel Free Tier**:
- 100GB bandwidth/month
- Unlimited deployments
- Free SSL
- Edge functions

**Render Free Tier**:
- 750 hours/month
- 100GB bandwidth/month

**Database Options**:
- Supabase: 500MB free
- Neon: 512MB free
- Railway: $5/month credit

## Support

For issues:
- **Vercel Docs**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **Community**: https://github.com/vercel/vercel/discussions
