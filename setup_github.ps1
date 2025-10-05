# Rigelstok GitHub Setup Script
# Run this script from the rigelstok-deploy directory

Write-Host "🚀 Rigelstok GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Check if git is installed
try {
    git --version | Out-Null
    Write-Host "✅ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Initialize git repository
Write-Host "`n📁 Initializing Git repository..." -ForegroundColor Yellow
git init

# Add all files
Write-Host "📦 Adding files to repository..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit - Rigelstok stock management system ready for deployment"

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Create a new repository on GitHub:" -ForegroundColor White
Write-Host "   👉 Go to https://github.com/new" -ForegroundColor Gray
Write-Host "   👉 Name it 'rigelstok'" -ForegroundColor Gray
Write-Host "   👉 Make it public or private" -ForegroundColor Gray
Write-Host "   👉 Don't initialize with README (we already have files)" -ForegroundColor Gray

Write-Host "`n2. Connect this repository to GitHub:" -ForegroundColor White
Write-Host "   Replace 'YOUR_USERNAME' with your GitHub username:" -ForegroundColor Gray
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/rigelstok.git" -ForegroundColor DarkGray
Write-Host "   git branch -M main" -ForegroundColor DarkGray
Write-Host "   git push -u origin main" -ForegroundColor DarkGray

Write-Host "`n3. Deploy on Railway.app:" -ForegroundColor White
Write-Host "   👉 Go to https://railway.app/" -ForegroundColor Gray
Write-Host "   👉 Sign in with GitHub" -ForegroundColor Gray
Write-Host "   👉 Click 'New Project' > 'Deploy from GitHub repo'" -ForegroundColor Gray
Write-Host "   👉 Select your rigelstok repository" -ForegroundColor Gray

Write-Host "`n4. Configure Environment Variables in Railway:" -ForegroundColor White
Write-Host "   FLASK_ENV=production" -ForegroundColor DarkGray
Write-Host "   SECRET_KEY=your-super-secret-key-change-this" -ForegroundColor DarkGray
Write-Host "   DATABASE_PATH=stok_takip_dev.db" -ForegroundColor DarkGray
Write-Host "   PORT=5000" -ForegroundColor DarkGray

Write-Host "`n✨ Ready for deployment! Good luck!" -ForegroundColor Green