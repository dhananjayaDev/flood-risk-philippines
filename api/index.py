"""
Vercel serverless entry point for Flask application
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Set environment variables for Vercel
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app
try:
    from app import create_app
except ImportError:
    # Fallback to simple version if main app fails
    import sys
    sys.path.append('.')
    from app.__init_simple__ import create_app

# Create the Flask app
app = create_app()

# Vercel serverless handler
def handler(request):
    """Vercel serverless handler"""
    return app(request.environ, lambda *args: None)

# For WSGI compatibility
application = app

# For local development
if __name__ == "__main__":
    app.run(debug=True)
