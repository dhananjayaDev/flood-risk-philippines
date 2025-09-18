# Vercel Deployment Guide for Flood Risk Philippines

## Prerequisites
1. Vercel account (sign up at vercel.com)
2. Vercel CLI installed (`npm i -g vercel`)
3. Git repository with your code

## Deployment Steps

### 1. Prepare Your Project
```bash
# Copy the Vercel-compatible files
cp requirements_vercel.txt requirements.txt
cp app_vercel.py app.py

# Make sure all files are in place
ls -la
```

### 2. Install Vercel CLI
```bash
npm install -g vercel
```

### 3. Login to Vercel
```bash
vercel login
```

### 4. Deploy to Vercel
```bash
# From your project root directory
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: flood-risk-philippines
# - Directory: ./
# - Override settings? N
```

### 5. Set Environment Variables
In your Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add the following variables:
   - `SECRET_KEY`: A random secret key for Flask
   - `DATABASE_URL`: Your database connection string (if using external DB)
   - `FLASK_ENV`: production

### 6. Redeploy
```bash
vercel --prod
```

## File Structure for Vercel
```
flood-risk-philippines/
├── api/
│   └── index.py          # Serverless entry point
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── main/
│   ├── auth/
│   └── ...
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── vercel.json          # Vercel configuration
├── requirements.txt     # Python dependencies
├── package.json         # Node.js configuration
└── .vercelignore        # Files to ignore
```

## Important Notes

### Database Considerations
- Vercel serverless functions have limitations with persistent databases
- Consider using external database services like:
  - PostgreSQL (Supabase, Railway, Neon)
  - MongoDB Atlas
  - PlanetScale (MySQL)

### Static Files
- Static files are served from the `static/` directory
- Make sure all CSS, JS, and image files are in the correct paths

### WebSocket Limitations
- Flask-SocketIO may not work perfectly with Vercel
- Consider using alternative real-time solutions like:
  - Server-Sent Events (SSE)
  - Polling
  - External WebSocket services

### Environment Variables
- Never commit sensitive data to your repository
- Use Vercel's environment variables for configuration
- Set different values for development and production

## Troubleshooting

### 404 Errors
- Check that `vercel.json` is properly configured
- Ensure `api/index.py` exists and is correct
- Verify all routes are properly defined

### Import Errors
- Check Python path in `api/index.py`
- Ensure all dependencies are in `requirements.txt`
- Verify file structure matches imports

### Static File Issues
- Check file paths in templates
- Ensure static files are in the `static/` directory
- Verify `url_for('static', ...)` usage

## Alternative Deployment Options
If Vercel doesn't work well for your Flask app, consider:
- **Railway**: Better for Flask apps with databases
- **Render**: Good for full-stack applications
- **Heroku**: Traditional PaaS for Python apps
- **DigitalOcean App Platform**: Flexible deployment option
