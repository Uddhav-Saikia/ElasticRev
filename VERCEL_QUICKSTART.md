# Quick Start: Deploy ElasticRev on Vercel

## 🚀 Fastest Way (Recommended)

### Step 1: Deploy Backend on Render
```bash
# Backend needs persistent storage, deploy on Render first
# Follow: RENDER_DEPLOYMENT.md for backend setup
```

### Step 2: Deploy Frontend on Vercel

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Vercel configuration"
   git push origin main
   ```

2. **Import to Vercel**:
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your repository
   - Vercel auto-detects settings from `vercel.json`

3. **Add Environment Variable**:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```
   (Use your backend URL from Render)

4. **Deploy**: Click "Deploy" ✨

5. **Done!** Your app is live at: `https://your-app.vercel.app`

## 📋 What Gets Deployed

```
Vercel (Frontend)          Render (Backend)
├── React Dashboard   →   ├── Flask API
├── Static Assets          ├── SQLite Database
└── Vite Build             ├── ML Models
                           └── Data Generation
```

## ⚡ Quick Commands

```bash
# Deploy with Vercel CLI
npm install -g vercel
vercel login
vercel --prod

# Or use GitHub integration (automatic on push)
git push origin main
```

## 🔧 Configuration

All configuration is in:
- `vercel.json` - Vercel settings
- `frontend/.env.production` - Environment variables
- `frontend/package.json` - Build scripts

## 📝 Environment Variables

Required in Vercel Dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-backend.onrender.com` | Backend API URL |

## 🎯 Post-Deployment

1. **Test the deployment**:
   - Visit your Vercel URL
   - Check if dashboard loads
   - Verify API connection

2. **Custom Domain** (optional):
   - Vercel → Settings → Domains
   - Add your domain
   - Update DNS records

3. **Monitor**:
   - Vercel → Analytics (usage stats)
   - Vercel → Logs (error tracking)

## ⚠️ Important Notes

- **Database**: Backend must be deployed separately (Render/Railway/Fly.io)
- **SQLite**: Not supported on Vercel's serverless environment
- **API Calls**: Frontend proxies to backend via `VITE_API_URL`
- **Free Tier**: 100GB bandwidth/month, unlimited deployments

## 🆘 Troubleshooting

**Build fails**:
```bash
# Check Node version in package.json
"engines": {
  "node": "18.x"
}
```

**API not connecting**:
```bash
# Verify VITE_API_URL is set in Vercel
# Check backend is running
curl https://your-backend.onrender.com/api/health
```

**404 on routes**:
```bash
# Ensure vercel.json has rewrites for SPA
"rewrites": [{"source": "/(.*)", "destination": "/index.html"}]
```

## 📚 Full Documentation

- Backend setup: `RENDER_DEPLOYMENT.md`
- Detailed guide: `VERCEL_DEPLOYMENT.md`

## 🎉 You're Live!

Frontend: `https://your-app.vercel.app`
Backend: `https://your-backend.onrender.com`

Happy deploying! 🚀
