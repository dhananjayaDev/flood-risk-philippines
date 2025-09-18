"""
Vercel-compatible Flask application entry point
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Import and create the Flask app
from app import create_app

app = create_app()

# For Vercel deployment
if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
