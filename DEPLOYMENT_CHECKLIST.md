# cPanel Deployment Checklist - CSS Fix Guide

Follow these steps to fix CSS not working on cPanel:

## ✅ Changes Made to Fix CSS Issues

### 1. **Updated `portfolio_project/settings.py`**
   - ✅ Added `whitenoise.middleware.WhiteNoiseMiddleware` to MIDDLEWARE
   - ✅ Added `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`

### 2. **Created `.htaccess` file**
   - ✅ Apache configuration for static files
   - ✅ Security headers
   - ✅ Compression and caching rules

## 📋 Deployment Steps for cPanel

### Step 1: Upload Files to cPanel
Upload all project files to your cPanel `public_html` folder or a subdirectory.

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=your_cpanel_db_name
DB_USER=your_cpanel_db_user
DB_PASSWORD=your_cpanel_db_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 4: Configure Database
1. Create a MySQL database in cPanel
2. Update `.env` with your database credentials
3. Run migrations:
```bash
python manage.py migrate
```

### Step 5: Collect Static Files (CRITICAL!)
```bash
python manage.py collectstatic --noinput
```
This command collects all static files into the `staticfiles/` directory where WhiteNoise can serve them.

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Set File Permissions
```bash
chmod 755 manage.py
chmod -R 755 static/
chmod -R 755 media/
chmod 644 .htaccess
```

### Step 8: Configure cPanel Python App
1. **Python App**: Set up a Python app in cPanel with the correct Python version (3.8+)
2. **Application Entry Point**: `passenger_wsgi:application`
3. **Application URL**: Set to your domain
4. **Passenger**: Enable if using Passenger WSGI

### Step 9: Restart the Application
Restart your Python app in cPanel to apply the changes.

## 🔍 Troubleshooting CSS Issues

### If CSS still doesn't work:

1. **Check Browser Console (F12)**
   - Look for 404 errors on CSS files
   - Check if the CSS file paths are correct

2. **Verify Static Files Collection**
   ```bash
   # Check if staticfiles directory exists and has content
   ls -la staticfiles/
   ```
   You should see `css/`, `js/`, and `images/` folders inside `staticfiles/`

3. **Check File Permissions**
   ```bash
   # Ensure static files are readable
   chmod -R 755 static/
   chmod -R 755 staticfiles/
   ```

4. **Clear Browser Cache**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

5. **Check .htaccess is Working**
   - Ensure `.htaccess` file is in your root directory (same level as `manage.py`)
   - Check cPanel error logs for any .htaccess errors

6. **Verify WhiteNoise is Installed**
   ```bash
   pip show whitenoise
   ```
   Should show version 6.6.0 or higher

7. **Check Django Settings**
   - Ensure `DEBUG = False` in production
   - Verify `STATIC_URL = 'static/'`
   - Verify `STATIC_ROOT = BASE_DIR / 'staticfiles'`

## 📁 Expected Directory Structure

```
your_project/
├── manage.py
├── passenger_wsgi.py
├── .htaccess
├── .env
├── static/                          # Source static files
│   ├── css/
│   ├── js/
│   └── images/
├── staticfiles/                     # Collected static files (created by collectstatic)
│   ├── css/
│   ├── js/
│   └── images/
├── media/                           # User-uploaded files
├── templates/
├── main/
└── portfolio_project/
```

## 🎯 Common Issues and Solutions

### Issue 1: CSS files return 404
**Solution**: Run `python manage.py collectstatic --noinput`

### Issue 2: CSS loads but styles are broken
**Solution**: Check browser console for CORS errors or mixed content (HTTP vs HTTPS)

### Issue 3: Static files not loading at all
**Solution**: 
- Verify WhiteNoise is in MIDDLEWARE
- Check file permissions (755 for directories, 644 for files)
- Restart the Python app in cPanel

### Issue 4: Changes to CSS not reflecting
**Solution**: 
- Run `collectstatic` again after CSS changes
- Clear browser cache
- Add version query strings (already handled by WhiteNoise)

## 🔐 Security Notes

- Never commit `.env` file to version control
- Always set `DEBUG = False` in production
- Keep `SECRET_KEY` secure and unique
- The `.htaccess` file protects sensitive files from direct access

## 📞 Still Having Issues?

1. Check cPanel error logs: **Metrics → Errors**
2. Check Django logs in your application
3. Verify all file paths are correct
4. Ensure Python version is 3.8 or higher
5. Contact your hosting provider if Passenger/WSGI is not configured correctly

## ✨ What Was Fixed

The main issue was that **WhiteNoise middleware was not configured** in your Django settings. WhiteNoise is essential for serving static files in production on cPanel because:

1. It serves static files directly through WSGI
2. It handles caching and compression automatically
3. It works seamlessly with Django's static file system
4. It's the recommended solution for Django on PaaS platforms like cPanel

With these changes, your CSS and other static files should now load correctly on cPanel!