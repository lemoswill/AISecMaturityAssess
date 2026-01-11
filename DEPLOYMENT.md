# 🚀 Deployment Guide - Streamlit Cloud

## Pre-Deployment Checklist

- [x] Move dev files to `_dev/`
- [x] Create `.gitignore`
- [x] Update `requirements.txt` with pinned versions
- [x] Add demo warning banner
- [x] Add CSV download functionality
- [x] Create README.md

## Step-by-Step Deployment

### 1. Initialize Git Repository

```bash
cd maturity_ai_security
git init
git add .
git commit -m "Initial commit - MVP1"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-security-maturity-tool`
3. Description: "AI-powered security maturity assessment tool (NIST AI RMF + CSA AICM)"
4. **Keep it Public** (required for free Streamlit hosting)
5. Click "Create repository"

### 3. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-security-maturity-tool.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository: `ai-security-maturity-tool`
4. Main file path: `app.py`
5. Click "Deploy!"

**Deployment time**: ~3-5 minutes

### 5. Post-Deployment Configuration

The app will work immediately, but for AI features:

1. Users need to provide their own API keys in the "Evidence Locker" tab
2. No additional secrets configuration needed for MVP1

## Expected Behavior

### ✅ What Works
- Full assessment workflow
- AI auto-assessment (with user-provided keys)
- Maturity wave filtering
- Dashboard visualization
- CSV download

### ⚠️ Known Limitations (MVP1)
- Data resets on app restart/redeploy
- No user authentication
- Evidence files are ephemeral
- Single-tenant mode

## Monitoring

After deployment, monitor:
- App URL: `https://YOUR_APP_NAME.streamlit.app`
- Logs: Available in Streamlit Cloud dashboard
- Usage: Check Streamlit Cloud analytics

## Troubleshooting

### Issue: App won't start
**Solution**: Check logs for missing dependencies. Verify `requirements.txt` versions.

### Issue: AI features not working
**Solution**: Ensure users are providing valid API keys in the Evidence Locker tab.

### Issue: Slow performance
**Solution**: Expected on free tier. Consider upgrading or optimizing ChromaDB queries.

## Next Steps (MVP2)

For production deployment:
1. Migrate to PostgreSQL (Supabase)
2. Add user authentication (Streamlit Auth or Auth0)
3. Implement persistent evidence storage (S3/GCS)
4. Add API endpoints
5. Custom domain

## Support

For issues, check:
- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
