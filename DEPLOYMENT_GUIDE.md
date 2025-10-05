# Rigelstok - Railway.app Deployment Guide

This folder contains all the necessary files for deploying Rigelstok to Railway.app.

## 📁 Project Structure

```
rigelstok-deploy/
├── app.py                  # Main Flask application
├── config.py               # Application configuration
├── requirements.txt        # Python dependencies
├── Procfile               # Process file for deployment
├── runtime.txt            # Python version specification
├── .env.production        # Environment variables template
├── .gitignore             # Git ignore rules
├── stok_takip_dev.db      # SQLite database
├── routes/                # Application routes
│   ├── __init__.py
│   └── main.py            # Main route handlers
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Dashboard
│   ├── stock_list.html    # Stock listing
│   ├── stock_movements.html # Stock movements
│   └── ...                # Other templates
├── static/                # Static files (CSS, JS, Images)
│   ├── css/
│   ├── js/
│   └── images/
├── utils/                 # Utility modules
│   ├── database.py        # Database operations
│   └── excel_processor.py # Excel processing
└── uploads/               # File upload directory
```

## 🚀 Railway.app Deployment Steps

### Step 1: GitHub Repository Setup
1. Create a new repository on GitHub called `rigelstok`
2. Initialize git in this directory:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Rigelstok deployment ready"
   ```
3. Connect to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/rigelstok.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Railway Account Setup
1. Go to https://railway.app/
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `rigelstok` repository

### Step 3: Environment Variables Configuration
In Railway dashboard, go to Variables section and add:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-change-this
DATABASE_PATH=stok_takip_dev.db
PORT=5000
```

**Important**: Change the `SECRET_KEY` to a strong, unique value!

### Step 4: Deployment
Railway will automatically:
- Detect Python project
- Install dependencies from requirements.txt
- Run the application using Procfile
- Assign a public URL

### Step 5: Verification
1. Wait for deployment to complete
2. Click on the generated URL
3. Test the application functionality

## 🔧 Key Features Included

- ✅ **Stock Management**: Add, edit, delete products
- ✅ **Stock Movements**: Entry, exit, transfer tracking
- ✅ **Real-time Dashboard**: Quick overview and recent activities
- ✅ **Excel Import**: Bulk product import functionality
- ✅ **Reports**: Stock reports and movement history
- ✅ **Reservations**: Product reservation system
- ✅ **Responsive Design**: Works on desktop and mobile

## 🗄️ Database

The application uses SQLite database (`stok_takip_dev.db`) which includes:
- Products table with stock levels
- Stock movements history
- User reservations
- Import logs

## 🔒 Security Notes

- Change the `SECRET_KEY` in environment variables
- The current database is for development - consider creating production data
- File uploads are stored in `uploads/` directory
- Environment variables are properly configured for production

## 📞 Support

If you encounter any issues during deployment:
1. Check Railway logs for error messages
2. Verify all environment variables are set correctly
3. Ensure GitHub repository is properly connected
4. Test the application locally first

## 🎯 Next Steps After Deployment

1. **Custom Domain**: Connect your own domain in Railway settings
2. **SSL Certificate**: Automatically provided by Railway
3. **Database Backup**: Set up regular database backups
4. **Monitoring**: Use Railway's built-in monitoring features
5. **Updates**: Push changes to GitHub to auto-deploy updates

---

**Railway Deployment URL**: Will be generated after deployment
**GitHub Repository**: https://github.com/YOUR_USERNAME/rigelstok
**Local Development**: Use `python app.py` to run locally