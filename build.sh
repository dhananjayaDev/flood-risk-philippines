#!/bin/bash

# Build script for Vercel deployment
echo "Building Flask application for Vercel..."

# Copy requirements file
cp requirements_vercel.txt requirements.txt

# Create necessary directories
mkdir -p api

# Copy the main app files
cp -r app api/

# Copy templates and static files
cp -r templates api/
cp -r static api/

# Copy configuration files
cp config.py api/ 2>/dev/null || echo "No config.py found, using environment variables"

echo "Build completed successfully!"
