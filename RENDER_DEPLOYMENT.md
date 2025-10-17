# Render Deployment with PostgreSQL

This guide explains how to deploy the database-driven app builder system to Render with PostgreSQL.

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **PostgreSQL Database**: Render provides managed PostgreSQL

## Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `app-builder-db`
   - **Database**: `appbuilder`
   - **User**: `appbuilder_user`
   - **Region**: Choose closest to your users
4. Click **"Create Database"**
5. Note the **External Database URL** (you'll need this)

## Step 2: Deploy Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

### Basic Settings
- **Name**: `app-builder-api`
- **Region**: Same as database
- **Branch**: `main`
- **Root Directory**: Leave empty

### Build & Deploy
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Environment Variables
Add these environment variables in Render dashboard:

```bash
# Database
DATABASE_URL=postgresql://appbuilder_user:password@host:port/appbuilder

# App Configuration
STUDENT_SECRET=hlo_iitm_student
AIPIPE_TOKEN=your_aipipe_token_here
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username

# Optional
PYTHON_VERSION=3.11
```

### Advanced Settings
- **Auto-Deploy**: Yes (for automatic deployments)
- **Health Check Path**: `/health`

## Step 3: Database Migration

The database tables will be created automatically when the app starts. However, you can also run migrations manually:

1. Go to your web service dashboard
2. Click **"Shell"**
3. Run: `python database.py`

## Step 4: Test Deployment

1. **Health Check**: Visit `https://your-app.onrender.com/health`
2. **API Docs**: Visit `https://your-app.onrender.com/docs`
3. **Root Endpoint**: Visit `https://your-app.onrender.com/`

## Step 5: Test Database System

Run the test script to verify the database integration:

```bash
python test_database_system.py
```

This will test:
- Round 1: Creates app and stores in database
- Round 2: Updates existing app using database data

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `STUDENT_SECRET` | Authentication secret | Yes |
| `AIPIPE_TOKEN` | AIPipe API token | Yes |
| `GITHUB_TOKEN` | GitHub personal access token | Yes |
| `GITHUB_USERNAME` | GitHub username | Yes |
| `PYTHON_VERSION` | Python version (default: 3.11) | No |

## Database Schema

### app_requests Table
- Stores all app build requests (round 1 and round 2)
- Links to llm_responses via task field

### llm_responses Table
- Stores LLM generated code and repository information
- Tracks different rounds for the same task

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check `DATABASE_URL` format
   - Ensure database is running
   - Verify credentials

2. **GitHub API Errors**
   - Check `GITHUB_TOKEN` permissions
   - Verify `GITHUB_USERNAME` is correct
   - Ensure token has repo access

3. **AIPipe API Errors**
   - Verify `AIPIPE_TOKEN` is valid
   - Check API endpoint availability

4. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt
   - Check build logs in Render dashboard

### Logs

View logs in Render dashboard:
1. Go to your web service
2. Click **"Logs"** tab
3. Check for errors and warnings

### Database Access

Access database directly:
1. Go to your PostgreSQL service
2. Click **"Connect"**
3. Use external database URL with psql or GUI tool

## Monitoring

- **Health Endpoint**: `/health` - Basic health check
- **Status Endpoint**: `/status/{nonce}` - Request status
- **API Documentation**: `/docs` - Interactive API docs

## Scaling

- **Free Tier**: 750 hours/month, sleeps after 15 minutes
- **Starter Plan**: $7/month, always on
- **Professional Plan**: $25/month, better performance

## Security Notes

- Never commit secrets to Git
- Use Render's environment variables for sensitive data
- Regularly rotate API tokens
- Monitor database access logs

## Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **PostgreSQL Docs**: [postgresql.org/docs](https://postgresql.org/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
