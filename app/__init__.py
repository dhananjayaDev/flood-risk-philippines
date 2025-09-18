"""
Flask App Factory - Database-Free Version
Real-time Philippine flood monitoring without database dependencies.
"""

from flask import Flask
from flask_socketio import SocketIO
from config import Config

# Initialize SocketIO (no database needed)
socketio = SocketIO()

def create_app():
    """Create and configure Flask app for real-time data only"""
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    
    # Initialize SocketIO for real-time updates
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    print("✅ Philippine Flood Monitor initialized (Real-time mode)")
    print("🌊 No database - Real-time API data only")
    print("🇵🇭 Philippine rivers and weather monitoring")
    
    return app

def get_app_info():
    """Get application information"""
    return {
        'name': 'Philippine Flood Monitor',
        'version': '2.0',
        'description': 'Real-time Philippine river and weather monitoring',
        'database_enabled': False,
        'real_time_only': True
    }