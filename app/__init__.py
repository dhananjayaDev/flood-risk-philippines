from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.flood_routes import flood_bp
    app.register_blueprint(flood_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Create tables for all river databases
        try:
            from app.models import (
                RiverHeight, KuruGangaHeight, WeyGangaHeight, 
                DenawakaGangaHeight, KukuleGangaHeight, GalathuraOyaHeight,
                PelmadullaWeather, RatnapuraWeather, KalawanaWeather,
                KuruvitaWeather, AyagamaWeather, KahawattaWeather
            )
            
            # Create tables for each river database
            river_models = [
                (RiverHeight, 'kalugangadb'),
                (KuruGangaHeight, 'kuruganga'),
                (WeyGangaHeight, 'weyganga'),
                (DenawakaGangaHeight, 'denawakaganga'),
                (KukuleGangaHeight, 'kukuleganga'),
                (GalathuraOyaHeight, 'galathuraoya')
            ]
            
            # Create tables for each weather database
            weather_models = [
                (PelmadullaWeather, 'pelmadulla_weather'),
                (RatnapuraWeather, 'ratnapura_weather'),
                (KalawanaWeather, 'kalawana_weather'),
                (KuruvitaWeather, 'kuruvita_weather'),
                (AyagamaWeather, 'ayagama_weather'),
                (KahawattaWeather, 'kahawatta_weather')
            ]
            
            # Create river tables
            for model, bind_key in river_models:
                try:
                    model.__table__.create(db.engines[bind_key], checkfirst=True)
                    print(f"✅ Created river table for {bind_key}")
                except Exception as e:
                    print(f"⚠️ Could not create river table for {bind_key}: {e}")
            
            # Create weather tables
            for model, bind_key in weather_models:
                try:
                    model.__table__.create(db.engines[bind_key], checkfirst=True)
                    print(f"✅ Created weather table for {bind_key}")
                except Exception as e:
                    print(f"⚠️ Could not create weather table for {bind_key}: {e}")
                    
        except Exception as e:
            print(f"Note: Could not create river/weather tables: {e}")
    
    # Start automatic river data collection
    try:
        from app.river_data_collector import start_river_data_collection
        if start_river_data_collection(app):
            print("✅ Automatic river data collection started")
        else:
            print("⚠️ Failed to start automatic river data collection")
    except Exception as e:
        print(f"⚠️ River data collector not available: {e}")
    
    # Start automatic weather data collection
    try:
        from app.weather_data_collector import start_weather_data_collection
        if start_weather_data_collection(app):
            print("✅ Automatic weather data collection started")
        else:
            print("⚠️ Failed to start automatic weather data collection")
    except Exception as e:
        print(f"⚠️ Weather data collector not available: {e}")
    
    return app
