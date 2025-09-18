"""
Notification Service for storing detailed weather descriptions
"""

import json
from datetime import datetime
import pytz
try:
    from flask import current_app
    from app import db
    from app.models import WeatherNotification
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

def store_weather_notification(location, river_name, short_description, full_description, prediction_data=None, weather_data=None, river_data=None):
    """
    Store detailed weather description in notification database
    
    Args:
        location (str): Location name
        river_name (str): River name
        short_description (str): 2-line description for UI
        full_description (str): Full detailed description
        prediction_data (dict): Full prediction data from Gemini
        weather_data (dict): Weather data used for prediction
        river_data (dict): River data used for prediction
    """
    try:
        if not FLASK_AVAILABLE:
            print("Flask not available, cannot store notification")
            return None
        
        # Create notification record
        notification = WeatherNotification(
            location=location,
            river_name=river_name,
            short_description=short_description,
            full_description=full_description,
            prediction_data=json.dumps(prediction_data) if prediction_data else None,
            weather_data=json.dumps(weather_data) if weather_data else None,
            river_data=json.dumps(river_data) if river_data else None
        )
        
        # Add to database
        db.session.add(notification)
        db.session.commit()
        
        if current_app:
            current_app.logger.info(f"Stored weather notification for {location}")
        else:
            print(f"Stored weather notification for {location}")
        
        return notification
        
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error storing notification: {e}")
        else:
            print(f"Error storing notification: {e}")
        
        # Rollback on error
        if FLASK_AVAILABLE:
            db.session.rollback()
        
        return None

def get_recent_notifications(limit=10):
    """
    Get recent weather notifications
    
    Args:
        limit (int): Number of notifications to retrieve
        
    Returns:
        list: List of notification dictionaries
    """
    try:
        if not FLASK_AVAILABLE:
            return []
        
        notifications = WeatherNotification.query.order_by(
            WeatherNotification.created_at.desc()
        ).limit(limit).all()
        
        return [notification.to_dict() for notification in notifications]
        
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error retrieving notifications: {e}")
        else:
            print(f"Error retrieving notifications: {e}")
        
        return []

def get_notification_by_id(notification_id):
    """
    Get specific notification by ID
    
    Args:
        notification_id (int): Notification ID
        
    Returns:
        dict: Notification data or None
    """
    try:
        if not FLASK_AVAILABLE:
            return None
        
        notification = WeatherNotification.query.get(notification_id)
        return notification.to_dict() if notification else None
        
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error retrieving notification {notification_id}: {e}")
        else:
            print(f"Error retrieving notification {notification_id}: {e}")
        
        return None
