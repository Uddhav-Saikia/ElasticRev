@echo off
echo.
echo ========================================
echo   ElasticRev Vercel Deployment
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo [ERROR] Git repository not initialized
    echo Run: git init
    exit /b 1
)
echo [OK] Git repository found

REM Check for vercel.json
if not exist vercel.json (
    echo [ERROR] vercel.json not found
    exit /b 1
)
echo [OK] Vercel configuration found

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not installed
    echo Install from: https://nodejs.org
    exit /b 1
)
echo [OK] Node.js found

REM Test frontend build
echo.
echo [BUILD] Testing frontend build...
cd frontend
call npm install --silent
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend build failed
    cd ..
    exit /b 1
)
echo [OK] Frontend builds successfully
cd ..

REM Commit changes
echo.
echo [GIT] Preparing commit...
git add .
git status --short

set /p COMMIT_MSG="Commit message (default: 'Deploy to Vercel'): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Deploy to Vercel

git commit -m "%COMMIT_MSG%"
echo [OK] Changes committed

REM Push to GitHub
echo.
echo [GIT] Pushing to GitHub...
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
git push origin %BRANCH%

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to push to GitHub
    exit /b 1
)
echo [OK] Code pushed successfully!

REM Instructions
echo.
echo ========================================
echo   Ready for Vercel Deployment!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Deploy Backend on Render:
echo    - Go to: https://render.com/new
echo    - Select your repository
echo    - Follow: RENDER_DEPLOYMENT.md
echo.
echo 2. Deploy Frontend on Vercel:
echo    - Go to: https://vercel.com/new
echo    - Import your GitHub repository
echo    - Vercel will auto-detect settings
echo.
echo 3. Add Environment Variable in Vercel:
echo    - VITE_API_URL=YOUR-BACKEND-URL
echo.
echo 4. Click 'Deploy' and wait 2-3 minutes
echo.
echo ========================================
echo.
echo Documentation:
echo    - VERCEL_QUICKSTART.md
echo    - VERCEL_DEPLOYMENT.md
echo    - DEPLOYMENT_CHECKLIST.md
echo.
echo Good luck!
echo.
pause
