from flask import jsonify, request
from flask_login import login_required
from app.weather import bp
from app.weather_service import (
    get_current_weather, 
    get_daily_forecast, 
    get_3day_history, 
    get_astronomy, 
    get_alerts,
    get_weather_summary
)

@bp.route('/api/weather/current')
@login_required
def api_current_weather():
    """API endpoint to get current weather data"""
    try:
        weather_data = get_current_weather()
        if weather_data:
            return jsonify({
                'success': True,
                'data': weather_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch current weather data'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/weather/forecast')
@login_required
def api_forecast():
    """API endpoint to get weather forecast"""
    try:
        days = request.args.get('days', 3, type=int)
        forecast_data = get_daily_forecast(days)
        return jsonify({
            'success': True,
            'data': forecast_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/weather/history')
@login_required
def api_history():
    """API endpoint to get weather history"""
    try:
        history_data = get_3day_history()
        return jsonify({
            'success': True,
            'data': history_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/weather/astronomy')
@login_required
def api_astronomy():
    """API endpoint to get astronomy data"""
    try:
        astronomy_data = get_astronomy()
        if astronomy_data:
            return jsonify({
                'success': True,
                'data': astronomy_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch astronomy data'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/weather/alerts')
@login_required
def api_alerts():
    """API endpoint to get weather alerts"""
    try:
        alerts_data = get_alerts()
        return jsonify({
            'success': True,
            'data': alerts_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/weather/summary')
@login_required
def api_weather_summary():
    """API endpoint to get complete weather summary"""
    try:
        summary_data = get_weather_summary()
        if summary_data:
            return jsonify({
                'success': True,
                'data': summary_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch weather summary'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/weather/public/current')
def api_public_current_weather():
    """Public API endpoint to get current weather data (no authentication required)"""
    try:
        weather_data = get_current_weather()
        if weather_data:
            return jsonify({
                'success': True,
                'data': weather_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch current weather data'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/weather/public/forecast')
def api_public_forecast():
    """Public API endpoint to get weather forecast (no authentication required)"""
    try:
        days = request.args.get('days', 3, type=int)
        forecast_data = get_daily_forecast(days)
        return jsonify({
            'success': True,
            'data': forecast_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
