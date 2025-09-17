"""
Flood Risk Prediction Routes
Provides API endpoints for flood risk prediction and monitoring
"""

from flask import Blueprint, jsonify, request
from app.flood_risk_predictor import predict_flood_risk, format_prediction_for_display, get_risk_level_info
from app import db
from app.models import RiverHeight, KuruGangaHeight, WeyGangaHeight, DenawakaGangaHeight, KukuleGangaHeight, GalathuraOyaHeight

# Create blueprint
flood_bp = Blueprint('flood', __name__, url_prefix='/flood')

@flood_bp.route('/predict', methods=['GET'])
def get_flood_prediction():
    """Get current flood risk prediction"""
    try:
        # Get hours parameter (default 24)
        hours_back = request.args.get('hours', 24, type=int)
        
        # Validate hours parameter
        if hours_back < 1 or hours_back > 168:  # Max 1 week
            return jsonify({
                'error': 'Invalid hours parameter. Must be between 1 and 168.',
                'status': 'error'
            }), 400
        
        # Get prediction
        prediction = predict_flood_risk(hours_back)
        
        if not prediction:
            return jsonify({
                'error': 'Failed to generate prediction',
                'status': 'error'
            }), 500
        
        # Format for API response
        response = {
            'status': 'success',
            'prediction': prediction,
            'formatted': format_prediction_for_display(prediction)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': f'Prediction failed: {str(e)}',
            'status': 'error'
        }), 500

@flood_bp.route('/risk-levels', methods=['GET'])
def get_risk_levels():
    """Get available risk levels and their descriptions"""
    try:
        risk_levels = {
            'LOW': {'level': 1, 'color': 'green', 'description': 'Minimal flood risk'},
            'MODERATE': {'level': 2, 'color': 'yellow', 'description': 'Moderate flood risk - monitor closely'},
            'HIGH': {'level': 3, 'color': 'orange', 'description': 'High flood risk - prepare for flooding'},
            'CRITICAL': {'level': 4, 'color': 'red', 'description': 'Critical flood risk - immediate action required'},
            'UNKNOWN': {'level': 0, 'color': 'gray', 'description': 'Unknown risk level'}
        }
        
        return jsonify({
            'status': 'success',
            'risk_levels': risk_levels
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get risk levels: {str(e)}',
            'status': 'error'
        }), 500

@flood_bp.route('/river-status', methods=['GET'])
def get_river_status():
    """Get current status of all rivers"""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        end_time = datetime.now(pytz.timezone('Asia/Colombo'))
        start_time = end_time - timedelta(hours=24)
        
        river_status = {}
        
        # River models and their names
        river_models = [
            (RiverHeight, 'Kalu Ganga (Ratnapura)', 'kalugangadb'),
            (KuruGangaHeight, 'Kuru Ganga (Kuruvita)', 'kuruganga'),
            (WeyGangaHeight, 'Wey Ganga (Kalawana)', 'weyganga'),
            (DenawakaGangaHeight, 'Denawaka Ganga (Pelmadulla)', 'denawakaganga'),
            (KukuleGangaHeight, 'Kukule Ganga (Kahawatta)', 'kukuleganga'),
            (GalathuraOyaHeight, 'Galathura Oya (Ayagama)', 'galathuraoya')
        ]
        
        for model_class, river_name, bind_key in river_models:
            try:
                # Get latest data
                latest = model_class.query.filter(
                    model_class.timestamp >= start_time
                ).order_by(model_class.timestamp.desc()).first()
                
                if latest:
                    # Get trend (compare with previous record)
                    previous = model_class.query.filter(
                        model_class.timestamp < latest.timestamp,
                        model_class.timestamp >= start_time
                    ).order_by(model_class.timestamp.desc()).first()
                    
                    if previous:
                        if latest.height > previous.height:
                            trend = "rising"
                        elif latest.height < previous.height:
                            trend = "falling"
                        else:
                            trend = "stable"
                    else:
                        trend = "unknown"
                    
                    river_status[river_name] = {
                        'current_height': latest.height,
                        'trend': trend,
                        'last_update': latest.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'active'
                    }
                else:
                    river_status[river_name] = {
                        'current_height': 0,
                        'trend': 'no_data',
                        'last_update': 'No recent data',
                        'status': 'inactive'
                    }
                    
            except Exception as e:
                river_status[river_name] = {
                    'current_height': 0,
                    'trend': 'error',
                    'last_update': f'Error: {str(e)}',
                    'status': 'error'
                }
        
        return jsonify({
            'status': 'success',
            'rivers': river_status,
            'analysis_period': '24 hours',
            'timestamp': end_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get river status: {str(e)}',
            'status': 'error'
        }), 500

@flood_bp.route('/weather-status', methods=['GET'])
def get_weather_status():
    """Get current weather status for all locations"""
    try:
        from datetime import datetime, timedelta
        import pytz
        from app.models import PelmadullaWeather, RatnapuraWeather, KalawanaWeather, KuruvitaWeather, AyagamaWeather, KahawattaWeather
        
        end_time = datetime.now(pytz.timezone('Asia/Colombo'))
        start_time = end_time - timedelta(hours=24)
        
        weather_status = {}
        
        # Weather models and their names
        weather_models = [
            (PelmadullaWeather, 'Pelmadulla'),
            (RatnapuraWeather, 'Ratnapura'),
            (KalawanaWeather, 'Kalawana'),
            (KuruvitaWeather, 'Kuruvita'),
            (AyagamaWeather, 'Ayagama'),
            (KahawattaWeather, 'Kahawatta')
        ]
        
        for model_class, location_name in weather_models:
            try:
                # Get latest weather data
                latest = model_class.query.filter(
                    model_class.timestamp >= start_time
                ).order_by(model_class.timestamp.desc()).first()
                
                if latest:
                    weather_status[location_name] = {
                        'temperature_c': latest.temperature_c,
                        'humidity': latest.humidity,
                        'precip_mm': latest.precip_mm,
                        'pressure_mb': latest.pressure_mb,
                        'wind_kph': latest.wind_kph,
                        'wind_dir': latest.wind_dir,
                        'condition': latest.condition,
                        'cloud': latest.cloud,
                        'visibility_km': latest.visibility_km,
                        'last_update': latest.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'active'
                    }
                else:
                    weather_status[location_name] = {
                        'temperature_c': 0,
                        'humidity': 0,
                        'precip_mm': 0,
                        'pressure_mb': 0,
                        'wind_kph': 0,
                        'wind_dir': 'N',
                        'condition': 'No data',
                        'cloud': 0,
                        'visibility_km': 0,
                        'last_update': 'No recent data',
                        'status': 'inactive'
                    }
                    
            except Exception as e:
                weather_status[location_name] = {
                    'temperature_c': 0,
                    'humidity': 0,
                    'precip_mm': 0,
                    'pressure_mb': 0,
                    'wind_kph': 0,
                    'wind_dir': 'N',
                    'condition': 'Error',
                    'cloud': 0,
                    'visibility_km': 0,
                    'last_update': f'Error: {str(e)}',
                    'status': 'error'
                }
        
        return jsonify({
            'status': 'success',
            'weather': weather_status,
            'analysis_period': '24 hours',
            'timestamp': end_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get weather status: {str(e)}',
            'status': 'error'
        }), 500

@flood_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data including prediction, river status, and weather"""
    try:
        # Get flood prediction
        prediction = predict_flood_risk(24)
        
        # Get river status
        river_response = get_river_status()
        river_data = river_response.get_json() if hasattr(river_response, 'get_json') else {}
        
        # Get weather status
        weather_response = get_weather_status()
        weather_data = weather_response.get_json() if hasattr(weather_response, 'get_json') else {}
        
        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'rivers': river_data.get('rivers', {}),
            'weather': weather_data.get('weather', {}),
            'timestamp': datetime.now(pytz.timezone('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get dashboard data: {str(e)}',
            'status': 'error'
        }), 500
