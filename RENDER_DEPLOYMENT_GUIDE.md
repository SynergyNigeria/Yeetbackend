# YEET Bank Backend - Render Deployment Guide

This guide will help you deploy the YEET Bank backend to Render using Daphne and SQLite.

## Prerequisites

1. GitHub account with your backend repository
2. Render account (free tier works fine)
3. Your backend code should be pushed to GitHub

## Files Created for Deployment

The following files have been created/updated for production deployment:

- **build.sh**: Build script that installs dependencies and runs migrations
- **render.yaml**: Render configuration (optional, can configure via dashboard)
- **requirements.txt**: Updated with production dependencies (Daphne, WhiteNoise, etc.)
- **.env.example**: Environment variables template

## Step-by-Step Deployment Guide

### 1. Prepare Your Repository

Before deploying, commit and push all changes to GitHub:

```bash
# In the backend directory
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your backend repository

### 3. Configure the Web Service

Fill in the following settings:

#### Basic Settings:
- **Name**: `yeet-bank-backend` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or specify if backend is in subfolder)
- **Runtime**: **Python**
- **Build Command**: `./build.sh`
- **Start Command**: `daphne -b 0.0.0.0 -p $PORT yeet_bank.asgi:application`

#### Advanced Settings:
- **Auto-Deploy**: Yes (recommended)

### 4. Set Environment Variables

In the Render dashboard, add the following environment variables:

#### Required Variables:

```
SECRET_KEY = [Click "Generate" button or use your own secure random string]
DEBUG = False
ALLOWED_HOSTS = your-app-name.onrender.com
```

#### CORS and CSRF Settings:

```
CORS_ALLOWED_ORIGINS = https://your-frontend-url.com,https://your-frontend-domain.com
CSRF_TRUSTED_ORIGINS = https://your-app-name.onrender.com,https://your-frontend-url.com
```

#### VAPID Keys (for Push Notifications):

Copy the keys from your `.env.example` or generate new ones:

```
VAPID_PRIVATE_KEY = -----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgIuOdF1awT1XX0euH
6n6IY04j+GxrPJCFJ5SQ++4B2ZKhRANCAATabJGGoXpI82V3XY/6drEHpgFC3+EF
CpZq08+LLBaC/TjQtbuwiM63PU/GDwdF3U1Yc++I/wcXRmHpetmTrM4S
-----END PRIVATE KEY-----

VAPID_PUBLIC_KEY = BNpskYahekjzZXddj_p2sQemAULf4QUKlmrTz4ssFoL9ONC1u7CIzrc9T8YPB0XdTVhz74j_BxdGYel62ZOszhI

VAPID_EMAIL = mailto:admin@yeetbank.com
```

#### Optional Variables:

```
PYTHON_VERSION = 3.11.0
```

### 5. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run `build.sh` (collect static files and run migrations)
   - Start the app with Daphne

### 6. Monitor Deployment

- Watch the logs in the Render dashboard
- First deployment takes 5-10 minutes
- Look for "Build completed successfully!" message

### 7. Verify Deployment

Once deployed, test your API:

```bash
# Replace with your actual Render URL
curl https://your-app-name.onrender.com/api/auth/health/
```

## Important Notes

### SQLite Database

- ⚠️ **Important**: Render's free tier uses ephemeral storage, meaning your SQLite database will be reset on each deployment
- For production with persistent data, consider upgrading to a paid Render plan or using PostgreSQL
- The database file will be recreated on each deployment with fresh migrations

### Static Files

- Static files are served via WhiteNoise middleware
- Files are collected during build with `collectstatic`
- Compressed and cached automatically

### Media Files (User Uploads)

- ⚠️ **Important**: Media files (like chat photos) will also be lost on redeployment with free tier
- For persistent media storage, consider:
  - Upgrading to paid Render plan with persistent disk
  - Using cloud storage (AWS S3, Cloudinary, etc.)

### Auto-Deploy

- With auto-deploy enabled, pushing to GitHub triggers automatic redeployment
- Disable auto-deploy if you want manual control

## Updating Your Application

After initial deployment, any push to your GitHub repository will trigger a new build automatically.

## Troubleshooting

### Build Fails

1. Check the build logs in Render dashboard
2. Verify `build.sh` has executable permissions:
   ```bash
   git update-index --chmod=+x build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

### Application Crashes

1. Check runtime logs in Render dashboard
2. Verify environment variables are set correctly
3. Check DEBUG=False to see actual errors

### CORS Errors

1. Update `CORS_ALLOWED_ORIGINS` with your actual frontend URL
2. Update `CSRF_TRUSTED_ORIGINS` with both backend and frontend URLs
3. Include full URLs with protocol: `https://your-app.com` (not `your-app.com`)

### Database Issues

1. Migrations run automatically during build
2. If migrations fail, check the build logs
3. You can manually run migrations via Render Shell if needed

## Connecting Frontend to Backend

Update your frontend `.env` file:

```
REACT_APP_API_URL=https://your-app-name.onrender.com
REACT_APP_VAPID_PUBLIC_KEY=BNpskYahekjzZXddj_p2sQemAULf4QUKlmrTz4ssFoL9ONC1u7CIzrc9T8YPB0XdTVhz74j_BxdGYel62ZOszhI
```

## Free Tier Limitations

Render's free tier has these limitations:

- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds to wake up
- 750 hours/month free (enough for one always-on service)
- Ephemeral storage (database resets on deployment)

## Upgrading to Paid Plan

For production with persistent storage:

1. Go to your service in Render dashboard
2. Navigate to "Settings"
3. Upgrade to a paid plan ($7/month)
4. Add persistent disk for database and media files

## Support

If you encounter issues:

1. Check Render logs (Logs tab in dashboard)
2. Review Render documentation: https://render.com/docs
3. Check your environment variables
4. Verify GitHub repository is up to date

## Next Steps

After successful deployment:

1. Update frontend to use production backend URL
2. Test all features (auth, transactions, chat, notifications)
3. Monitor performance and logs
4. Consider upgrading to paid plan for persistence
5. Set up proper domain name (optional)
6. Configure SSL certificate (automatically provided by Render)

---

**Congratulations!** Your YEET Bank backend is now deployed on Render! 🎉
