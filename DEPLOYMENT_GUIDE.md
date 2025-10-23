# 🚀 Deployment Guide - ElasticRev

## Quick Deployment Options

### Option 1: Vercel (Frontend) + Render (Backend) ⭐ Recommended

**Best for**: Production deployment with free tiers

```bash
# 1. Run deployment script
./deploy.bat  # Windows
./deploy.sh   # Linux/Mac

# 2. Deploy backend on Render
# 3. Deploy frontend on Vercel
```

**Pros**:
- ✅ Free tiers available
- ✅ Auto-deploy on git push
- ✅ Global CDN (Vercel)
- ✅ Easy setup

**Setup Time**: ~15 minutes

📖 **Full Guide**: [VERCEL_QUICKSTART.md](VERCEL_QUICKSTART.md)

---

### Option 2: Render (Full Stack)

**Best for**: Unified platform, single service

```bash
# Deploy both frontend and backend on Render
```

**Pros**:
- ✅ Single platform
- ✅ PostgreSQL included
- ✅ Simple management

**Setup Time**: ~10 minutes

📖 **Full Guide**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

---

### Option 3: Docker (Any Platform)

**Best for**: Consistent environments, any cloud provider

```bash
docker-compose up -d
```

**Pros**:
- ✅ Works anywhere
- ✅ Consistent environment
- ✅ Easy local testing

**Setup Time**: ~5 minutes

📖 **Full Guide**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

---

## Architecture Diagrams

### Vercel + Render Architecture
```
┌─────────────────────────────────────┐
│         Vercel (Frontend)           │
│  ┌──────────────────────────────┐   │
│  │    React + Vite Build        │   │
│  │    Static Assets (CDN)       │   │
│  └──────────────────────────────┘   │
└────────────┬────────────────────────┘
             │ HTTPS Requests
             ↓
┌─────────────────────────────────────┐
│         Render (Backend)            │
│  ┌──────────────────────────────┐   │
│  │    Flask API (Gunicorn)      │   │
│  │    ML Models                 │   │
│  └──────────┬───────────────────┘   │
│             ↓                        │
│  ┌──────────────────────────────┐   │
│  │    PostgreSQL Database       │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Render Full Stack Architecture
```
┌─────────────────────────────────────┐
│         Render (Monolith)           │
│  ┌──────────────────────────────┐   │
│  │    Static Frontend           │   │
│  └──────────┬───────────────────┘   │
│             ↓                        │
│  ┌──────────────────────────────┐   │
│  │    Flask API                 │   │
│  └──────────┬───────────────────┘   │
│             ↓                        │
│  ┌──────────────────────────────┐   │
│  │    PostgreSQL                │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Comparison Table

| Feature | Vercel + Render | Render Only | Docker |
|---------|----------------|-------------|--------|
| **Setup Difficulty** | Easy | Easiest | Medium |
| **Cost (Free Tier)** | Yes | Yes | Self-hosted |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Auto-Deploy** | Yes | Yes | Manual |
| **Custom Domain** | Yes | Yes | Yes |
| **SSL Certificate** | Free | Free | Manual |
| **Database** | PostgreSQL | PostgreSQL | Any |
| **Best For** | Production | Simple Setup | Any Cloud |

---

## Environment Variables

### Frontend (Vercel)
```env
VITE_API_URL=https://your-backend.onrender.com
```

### Backend (Render)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

---

## Cost Breakdown

### Free Tier Limits

**Vercel**:
- 100GB bandwidth/month
- Unlimited deployments
- 100 GB-hours compute

**Render**:
- 750 hours/month (single service)
- 100GB bandwidth
- 512MB RAM

**PostgreSQL**:
- Render: 1GB storage (free)
- Supabase: 500MB (free)
- Neon: 512MB (free)

### Paid Plans (if needed)

**Vercel Pro**: $20/month
- 1TB bandwidth
- Unlimited team members
- Priority support

**Render Standard**: $7/month per service
- Always-on (no spin-down)
- 512MB-16GB RAM
- More compute

---

## Pre-Deployment Checklist

- [ ] Code tested locally
- [ ] All dependencies in requirements.txt
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] API endpoints tested
- [ ] Frontend builds successfully
- [ ] Code pushed to GitHub

---

## Post-Deployment Tasks

### 1. Verify Deployment
```bash
# Test backend
curl https://your-backend.onrender.com/api/health

# Test frontend
open https://your-app.vercel.app
```

### 2. Monitor Performance
- Set up uptime monitoring
- Check error logs
- Review analytics

### 3. Configure Domain (Optional)
- Add custom domain
- Set up SSL
- Update DNS records

### 4. Set Up CI/CD
- Enable auto-deploy
- Add deployment status badges
- Configure branch protections

---

## Troubleshooting

### Common Issues

**Issue**: Frontend can't connect to backend
```bash
# Solution: Check VITE_API_URL is set correctly
# Verify backend is running
curl https://your-backend.onrender.com/api/health
```

**Issue**: Database connection fails
```bash
# Solution: Check DATABASE_URL format
# PostgreSQL URL should start with postgresql://
# Update config.py if needed
```

**Issue**: Build fails on Vercel
```bash
# Solution: Check Node version
# Update package.json engines section
```

---

## Support & Resources

### Documentation
- 📘 [Vercel Quick Start](VERCEL_QUICKSTART.md)
- 📗 [Render Deployment](RENDER_DEPLOYMENT.md)
- 📙 [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)

### Community
- 💬 Vercel Discord
- 💬 Render Community Forum
- 🐛 GitHub Issues

### Monitoring Tools
- 📊 Vercel Analytics
- 📊 Render Metrics
- 📊 UptimeRobot (uptime monitoring)
- 📊 Sentry (error tracking)

---

## Security Best Practices

1. **Environment Variables**
   - Never commit secrets to git
   - Use platform environment variables
   - Rotate keys regularly

2. **CORS Configuration**
   - Restrict allowed origins
   - Update for production domains

3. **Database**
   - Use connection pooling
   - Enable SSL connections
   - Regular backups

4. **API Security**
   - Rate limiting
   - Input validation
   - Error handling

---

## Need Help?

1. Check the deployment guides
2. Review the troubleshooting section
3. Check platform status pages
4. Contact platform support
5. Open a GitHub issue

---

**Ready to deploy?** Start with [VERCEL_QUICKSTART.md](VERCEL_QUICKSTART.md)! 🚀
