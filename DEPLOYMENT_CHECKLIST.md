# Pre-Deployment Checklist

Before deploying to Render, make sure you've completed these steps:

## ✅ Code Preparation

- [ ] All files committed to Git
- [ ] Latest code pushed to GitHub
- [ ] `build.sh` is in the repository
- [ ] `requirements.txt` is up to date
- [ ] `.gitignore` excludes sensitive files (.env, db.sqlite3, etc.)

## ✅ Files to Commit

Make sure these files are in your GitHub repository:

- [ ] `build.sh` - Build script for Render
- [ ] `render.yaml` - Render configuration (optional)
- [ ] `requirements.txt` - Python dependencies
- [ ] `.env.example` - Environment variables template
- [ ] `manage.py` - Django management script
- [ ] All app folders (accounts, transactions, notifications, chat)
- [ ] `yeet_bank/settings.py` - Updated with environment variables
- [ ] `yeet_bank/asgi.py` - ASGI configuration

## ✅ Files to EXCLUDE (should be in .gitignore)

- [ ] `.env` - Your local environment variables
- [ ] `db.sqlite3` - Your local database
- [ ] `venv/` - Virtual environment
- [ ] `__pycache__/` - Python cache files
- [ ] `staticfiles/` - Collected static files
- [ ] `media/` - User uploaded files

## ✅ Configuration Check

- [ ] `SECRET_KEY` will be set in Render environment variables
- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` uses environment variable
- [ ] `CORS_ALLOWED_ORIGINS` uses environment variable
- [ ] `CSRF_TRUSTED_ORIGINS` uses environment variable
- [ ] VAPID keys are in `.env.example`

## ✅ Quick Commands

Run these commands before deploying:

```bash
# 1. Make build.sh executable
git update-index --chmod=+x build.sh

# 2. Verify requirements.txt includes all packages
pip freeze > requirements-check.txt
# Compare with requirements.txt and ensure Daphne, WhiteNoise are included

# 3. Test build script locally (optional)
chmod +x build.sh
./build.sh

# 4. Commit all changes
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

## ✅ Environment Variables to Set in Render

Prepare these values before creating the Render service:

1. **SECRET_KEY**: Generate a new one (Render can generate this)
2. **DEBUG**: `False`
3. **ALLOWED_HOSTS**: Will be `your-app-name.onrender.com`
4. **CORS_ALLOWED_ORIGINS**: Your frontend URL(s)
5. **CSRF_TRUSTED_ORIGINS**: Your backend and frontend URLs
6. **VAPID_PRIVATE_KEY**: From `.env.example`
7. **VAPID_PUBLIC_KEY**: From `.env.example`
8. **VAPID_EMAIL**: `mailto:admin@yeetbank.com`

## ✅ Post-Deployment Tasks

After successful deployment:

- [ ] Test API health endpoint
- [ ] Test user registration
- [ ] Test user login
- [ ] Test transactions
- [ ] Test chat functionality
- [ ] Test push notifications
- [ ] Update frontend `.env` with backend URL
- [ ] Update frontend with VAPID public key

## 🚀 Ready to Deploy?

Once all items are checked:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Follow the deployment guide in `RENDER_DEPLOYMENT_GUIDE.md`
3. Monitor the build logs
4. Test your deployed API

## ⚠️ Important Reminders

- **SQLite Warning**: Free tier storage is ephemeral (database resets on deployment)
- **Media Files**: Uploaded files (chat photos) will be lost on redeployment
- **Cold Starts**: Free tier services sleep after 15 min inactivity (~30s wake-up time)
- **Consider**: Upgrading to paid plan ($7/mo) for persistent storage if needed

---

Good luck with your deployment! 🎉
