# NeoJambu Heroku Deployment Guide

This guide explains how to deploy the NeoJambu linguistics webapp to Heroku using uv for fast, efficient builds.

## 🚀 Quick Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## 📋 Prerequisites

- Heroku CLI installed
- Git repository
- Python 3.10.6+

## 🔧 Configuration Files

The project includes these deployment files:

- `Procfile` - Defines release and web processes
- `runtime.txt` - Specifies Python version (3.10.6)
- `app.json` - Heroku app configuration with uv buildpack
- `.buildpacks` - Ensures uv buildpack is used
- `release.sh` - Handles database download and verification
- `verify_deployment.py` - Post-deployment verification

## 🏗️ Deployment Process

### 1. Using Heroku CLI

```bash
# Create Heroku app
heroku create your-app-name

# Set buildpack (if not using app.json)
heroku buildpacks:set https://github.com/astral-sh/uv-python-buildpack

# Deploy
git push heroku main
```

### 2. Using Heroku Dashboard

1. Go to [Heroku Dashboard](https://dashboard.heroku.com)
2. Click "New" → "Create new app"
3. Connect to your Git repository
4. Enable automatic deploys (optional)
5. Click "Deploy Branch"

## 🔄 Release Process

The deployment automatically:

1. **Installs dependencies** using uv (faster than pip)
2. **Downloads database** from GitHub releases (313k lemmas)
3. **Verifies database integrity** 
4. **Checks performance indexes**
5. **Starts web server** with gunicorn

## 🎯 Performance Optimizations

The deployment includes:

- **Database indexes** for fast queries on 313k lemmas
- **Connection pooling** for better concurrency
- **Eager loading** to prevent DetachedInstanceError
- **uv package manager** for 10-100x faster builds

## 🔍 Verification

After deployment, the app automatically verifies:

- ✅ Database connectivity (313k+ lemmas, 615+ languages)  
- ✅ Performance indexes existence
- ✅ Session management functionality
- ✅ Flask routes accessibility

## 🐛 Troubleshooting

### Build Issues

```bash
# Check buildpack
heroku buildpacks

# View build logs
heroku logs --tail

# Run verification manually
heroku run python verify_deployment.py
```

### Runtime Issues

```bash
# Check app logs
heroku logs --tail

# Check database
heroku run sqlite3 data.db ".tables"

# Test specific route
curl https://your-app-name.herokuapp.com/entries
```

### Performance Issues

```bash
# Check database indexes
heroku run sqlite3 data.db "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"

# Run performance tests
heroku run python test_performance.py
```

## 📊 App Configuration

**Recommended Heroku Plan:** Basic ($7/month)
- Supports the 313k lemma database
- Handles moderate concurrent users
- Includes performance optimizations

**Environment Variables:**
- No special environment variables required
- Database is downloaded automatically

## 🔧 Advanced Configuration

### Custom Domain

```bash
heroku domains:add your-domain.com
```

### SSL/HTTPS

```bash
heroku certs:auto:enable
```

### Scaling

```bash
# Scale web dynos
heroku ps:scale web=2

# Check current scaling
heroku ps
```

## 📈 Monitoring

Monitor your app:

```bash
# View metrics
heroku logs --tail

# Check dyno status  
heroku ps

# Database size
heroku run du -h data.db
```

## 🔄 Updates

To deploy updates:

```bash
git add .
git commit -m "Update webapp"
git push heroku main
```

The release process will automatically:
- Re-download latest database (if needed)
- Verify all systems
- Restart with zero downtime

---

**Questions?** Check the logs: `heroku logs --tail`