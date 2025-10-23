#!/bin/bash

echo "🚀 ElasticRev Vercel Deployment"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${RED}❌ Git repository not initialized${NC}"
    echo "Run: git init"
    exit 1
fi

echo -e "${GREEN}✅ Git repository found${NC}"

# Check for vercel.json
if [ ! -f vercel.json ]; then
    echo -e "${RED}❌ vercel.json not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Vercel configuration found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not installed${NC}"
    echo "Install from: https://nodejs.org"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version) found${NC}"

# Test frontend build
echo ""
echo -e "${YELLOW}📦 Testing frontend build...${NC}"
cd frontend
npm install --silent
if npm run build; then
    echo -e "${GREEN}✅ Frontend builds successfully${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi
cd ..

# Commit changes
echo ""
echo -e "${YELLOW}💾 Preparing commit...${NC}"
git add .
git status --short

read -p "Commit message (default: 'Deploy to Vercel'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Deploy to Vercel"}

git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✅ Changes committed${NC}"

# Push to GitHub
echo ""
echo -e "${YELLOW}⬆️  Pushing to GitHub...${NC}"
BRANCH=$(git branch --show-current)
git push origin $BRANCH

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Code pushed to GitHub successfully!${NC}"
else
    echo -e "${RED}❌ Failed to push to GitHub${NC}"
    exit 1
fi

# Instructions
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Ready for Vercel Deployment!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Deploy Backend on Render:"
echo "   → Go to: https://render.com/new"
echo "   → Select your repository"
echo "   → Follow: RENDER_DEPLOYMENT.md"
echo ""
echo "2️⃣  Deploy Frontend on Vercel:"
echo "   → Go to: https://vercel.com/new"
echo "   → Import your GitHub repository"
echo "   → Vercel will auto-detect settings"
echo ""
echo "3️⃣  Add Environment Variable in Vercel:"
echo "   → VITE_API_URL=<your-backend-url-from-render>"
echo ""
echo "4️⃣  Click 'Deploy' and wait 2-3 minutes"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation:"
echo "   • Quick Start: VERCEL_QUICKSTART.md"
echo "   • Full Guide: VERCEL_DEPLOYMENT.md"
echo "   • Checklist: DEPLOYMENT_CHECKLIST.md"
echo ""
echo -e "${GREEN}Good luck! 🍀${NC}"
echo ""
