#!/bin/bash

echo "🚀 Deploying Flood Risk Philippines to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "npm install -g vercel"
    exit 1
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel. Please run: vercel login"
    exit 1
fi

# Copy Vercel-compatible files
echo "📋 Preparing files for Vercel..."
cp requirements_vercel.txt requirements.txt
cp app_vercel.py app.py

# Create api directory if it doesn't exist
mkdir -p api

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at the URL shown above."
echo ""
echo "📝 Don't forget to:"
echo "   1. Set environment variables in Vercel dashboard"
echo "   2. Configure your database connection"
echo "   3. Test all functionality"
