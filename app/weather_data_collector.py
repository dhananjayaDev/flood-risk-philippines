"""
Weather Data Collector Module
Handles automatic collection of weather data for multiple locations every 30 minutes.
"""

import time
import threading
from datetime import datetime
import pytz
from app.weather_service import fetch_api, get_astronomy
from app import db

class WeatherDataCollector:
    """Collects weather data for multiple locations every 30 minutes"""
    
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        
        # Weather locations configuration
        self.WEATHER_LOCATIONS = [
            {
                'name': 'Pelmadulla',
                'query': 'Pelmadulla, Sri Lanka',
                'model': None,  # Will be set after import
                'bind_key': 'pelmadulla_weather'
            },
            {
                'name': 'Ratnapura',
                'query': 'Ratnapura, Sri Lanka',
                'model': None,  # Will be set after import
                'bind_key': 'ratnapura_weather'
            },
            {
                'name': 'Kalawana',
                'query': 'Kalawana, Sri Lanka',
                'model': None,  # Will be set after import
                'bind_key': 'kalawana_weather'
            },
            {
                'name': 'Kuruvita',
                'query': 'Kuruvita, Sri Lanka',
                'model': None,  # Will be set after import
                'bind_key': 'kuruvita_weather'
            },
            {
                'name': 'Ayagama',
                'query': 'Ayagama, Sri Lanka',
                'model': None,  # Will be set after import
                'bind_key': 'ayagama_weather'
            },
            {
                'name': 'Kahawatta',
                'query': 'Kahawatta, Sri Lanka',
                'model': None,  # Will be set after import
                'bind_key': 'kahawatta_weather'
            }
        ]
        
        # Import weather models
        self._import_weather_models()
    
    def _import_weather_models(self):
        """Import weather models and assign them to location configs"""
        try:
            from app.models import (
                PelmadullaWeather, RatnapuraWeather, KalawanaWeather,
                KuruvitaWeather, AyagamaWeather, KahawattaWeather
            )
            
            weather_models = [
                PelmadullaWeather, RatnapuraWeather, KalawanaWeather,
                KuruvitaWeather, AyagamaWeather, KahawattaWeather
            ]
            
            for i, model in enumerate(weather_models):
                self.WEATHER_LOCATIONS[i]['model'] = model
                
        except ImportError as e:
            print(f"❌ Error importing weather models: {e}")
            raise
    
    def start(self):
        """Start the weather data collection in a background thread"""
        if self.running:
            print("⚠️ Weather data collection is already running")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.thread.start()
        print("✅ Weather data collection started")
        return True
    
    def stop(self):
        """Stop the weather data collection"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⏹️ Weather data collection stopped")
    
    def _collect_loop(self):
        """Main collection loop - runs every 30 minutes"""
        with self.app.app_context():
            print("⏳ Waiting 2 minutes before first weather collection to avoid duplicates...")
            for i in range(120):  # 2 minutes
                if not self.running:
                    return
                time.sleep(1)
            
            while self.running:
                try:
                    self._collect_all_weather()
                    for i in range(1800):  # 30 minutes = 1800 seconds
                        if not self.running:
                            break
                        time.sleep(1)
                except Exception as e:
                    print(f"❌ Error in weather collection: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
    
    def _collect_all_weather(self):
        """Collect weather data from all locations"""
        print(f"🌤️ Starting weather data collection at {datetime.now(pytz.timezone('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S')}")
        
        for location_config in self.WEATHER_LOCATIONS:
            try:
                self._collect_weather_for_location(location_config)
            except Exception as e:
                print(f"❌ Error collecting weather for {location_config['name']}: {e}")
        
        print("✅ Weather data collection completed")
    
    def _collect_weather_for_location(self, location_config):
        """Collect weather data for a specific location"""
        location_name = location_config['name']
        query = location_config['query']
        model_class = location_config['model']
        bind_key = location_config['bind_key']
        
        try:
            # Fetch current weather data
            current_data = fetch_api('current', {'q': query})
            current = current_data['current']
            
            # Fetch astronomy data for sunrise/sunset
            today = datetime.now().strftime('%Y-%m-%d')
            astronomy_data = fetch_api('astronomy', {'q': query, 'dt': today})
            astro = astronomy_data['astronomy']['astro']
            
            # Create timestamp
            timestamp = datetime.now(pytz.timezone('Asia/Colombo'))
            
            # Prepare weather data
            weather_data = {
                'location': location_name,
                'timestamp': timestamp,
                'temperature_c': current.get('temp_c', 0.0),
                'humidity': current.get('humidity', 0.0),
                'precip_mm': current.get('precip_mm', 0.0),
                'pressure_mb': current.get('pressure_mb', 0.0),
                'wind_kph': current.get('wind_kph', 0.0),
                'wind_dir': current.get('wind_dir', 'N'),
                'uv_index': current.get('uv', 0.0),
                'condition': current.get('condition', {}).get('text', 'Unknown'),
                'feelslike_c': current.get('feelslike_c', 0.0),
                'cloud': current.get('cloud', 0.0),
                'visibility_km': current.get('vis_km', 0.0),
                'gust_kph': current.get('gust_kph', 0.0),
                'sunrise': astro.get('sunrise', '06:00 AM'),
                'sunset': astro.get('sunset', '06:00 PM')
            }
            
            # Check for duplicate records (same timestamp and location)
            existing_record = model_class.query.filter(
                model_class.timestamp == timestamp,
                model_class.location == location_name
            ).first()
            
            if existing_record:
                print(f"  ⚠️ {location_name}: Duplicate record found, skipping")
                return
            
            # Create new weather record
            weather_record = model_class(**weather_data)
            db.session.add(weather_record)
            db.session.commit()
            
            print(f"  ✅ {location_name}: Weather data recorded - {weather_data['temperature_c']}°C, {weather_data['condition']}")
            
        except Exception as e:
            print(f"  ❌ {location_name}: Error collecting weather data: {e}")
            db.session.rollback()
    
    def collect_now(self):
        """Manually trigger weather data collection for all locations"""
        if not self.running:
            print("⚠️ Weather collector is not running. Start it first.")
            return False
        
        with self.app.app_context():
            self._collect_all_weather()
        return True
    
    def get_status(self):
        """Get the current status of the weather collector"""
        return {
            'running': self.running,
            'locations': len(self.WEATHER_LOCATIONS),
            'location_names': [loc['name'] for loc in self.WEATHER_LOCATIONS]
        }

# Global weather collector instance
_weather_collector = None

def start_weather_data_collection(app):
    """Start weather data collection for all locations"""
    global _weather_collector
    
    try:
        _weather_collector = WeatherDataCollector(app)
        return _weather_collector.start()
    except Exception as e:
        print(f"❌ Failed to start weather data collection: {e}")
        return False

def stop_weather_data_collection():
    """Stop weather data collection"""
    global _weather_collector
    
    if _weather_collector:
        _weather_collector.stop()
        return True
    return False

def collect_weather_data_now():
    """Manually trigger weather data collection"""
    global _weather_collector
    
    if _weather_collector:
        return _weather_collector.collect_now()
    return False

def get_weather_collector_status():
    """Get weather collector status"""
    global _weather_collector
    
    if _weather_collector:
        return _weather_collector.get_status()
    return {'running': False, 'locations': 0, 'location_names': []}
