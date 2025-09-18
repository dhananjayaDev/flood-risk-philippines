"""
Philippine River Data Service - Philippine Focus Only
This file contains only Philippine river functionality.
Sri Lankan code has been moved to river_sri_lankan_backup.py for reference.
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import pytz
try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Global river configuration - Philippine Focus
DEFAULT_RIVER = "Agno River"  # Philippine default

def get_current_river():
    """
    Check current_location.txt and return the appropriate Philippine river name.
    """
    try:
        # Get the current location from the file
        from .search import load_location_from_file
        current_location = load_location_from_file()
        
        if not current_location:
            return DEFAULT_RIVER
        
        # Check if current location matches any Philippine river
        try:
            from .philippine_river_service import get_current_philippine_river
            philippine_river = get_current_philippine_river()
            if philippine_river != 'Agno River':  # Default, means we found a match
                return philippine_river
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error checking Philippine river: {e}")
                except:
                    print(f"Error checking Philippine river: {e}")
            else:
                print(f"Error checking Philippine river: {e}")
        
        # If no match found, return default
        return DEFAULT_RIVER
        
    except Exception as e:
        if FLASK_AVAILABLE:
            try:
                current_app.logger.error(f"Error getting current river: {e}")
            except:
                print(f"Error getting current river: {e}")
        else:
            print(f"Error getting current river: {e}")
        return DEFAULT_RIVER

def get_current_river_height(river_name=None):
    """
    Get the current river height for a Philippine river.
    Args:
        river_name (str): Name of the river (default: uses current location to determine river)
    Returns:
        dict: Dictionary with current river height data or None if no data
    """
    try:
        # Use current location-based river if no river name provided
        if river_name is None:
            river_name = get_current_river()
        
        # Use Philippine river service
        try:
            from .philippine_river_service import get_philippine_river_height, get_current_philippine_river
            
            # Check if current river is a Philippine river
            philippine_river = get_current_philippine_river()
            if philippine_river != 'Agno River':  # Default, means we found a match
                philippine_data = get_philippine_river_height(philippine_river)
                if philippine_data:
                    return philippine_data
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error checking Philippine river: {e}")
                except:
                    print(f"Error checking Philippine river: {e}")
            else:
                print(f"Error checking Philippine river: {e}")
        
        # If no Philippine data, return None
        if FLASK_AVAILABLE:
            current_app.logger.warning(f"No Philippine river data available for {river_name}")
        else:
            print(f"No Philippine river data available for {river_name}")
        return None
        
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error getting current river height: {str(e)}")
        else:
            print(f"Error getting current river height: {str(e)}")
        
        return None

def get_river_height_7day(river_name=None):
    """
    Get 7-day river height data for chart display (real-time Philippine data only).
    Args:
        river_name (str): Name of the river (default: uses current location to determine river)
    Returns:
        list: 7-day array with river height data
    """
    try:
        # Use current location-based river if no river name provided
        if river_name is None:
            river_name = get_current_river()
        
        # Use Philippine river service
        try:
            from .philippine_river_service import get_philippine_river_7day, get_current_philippine_river
            
            # Check if current river is a Philippine river
            philippine_river = get_current_philippine_river()
            if philippine_river != 'Agno River':  # Default, means we found a match
                philippine_data = get_philippine_river_7day(philippine_river)
                if philippine_data:
                    return philippine_data
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error checking Philippine river 7-day: {e}")
                except:
                    print(f"Error checking Philippine river 7-day: {e}")
            else:
                print(f"Error checking Philippine river 7-day: {e}")
        
        # If no Philippine data, return empty 7-day array
        result = []
        today = datetime.now(pytz.timezone('Asia/Manila'))
        
        for i in range(7):
            # Calculate date for this day (3 days ago to 3 days from now)
            day_date = today - timedelta(days=3-i)
            day_name = day_date.strftime('%a')  # Dynamic day name (Mon, Tue, Wed, etc.)
            
            result.append({
                'day': day_name,
                'height': 0.0,  # No data available
                'date': day_date.strftime('%Y-%m-%d'),
                'is_current': i == 3
            })
        
        return result
        
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error getting 7-day river height: {str(e)}")
        else:
            print(f"Error getting 7-day river height: {str(e)}")
        
        # Return empty data on error
        result = []
        today = datetime.now(pytz.timezone('Asia/Manila'))
        for i in range(7):
            day_date = today - timedelta(days=3-i)
            day_name = day_date.strftime('%a')  # Dynamic day name
            result.append({
                'day': day_name,
                'height': 0.0,  # Always 0 on error
                'date': day_date.strftime('%Y-%m-%d'),
                'is_current': i == 3
            })
        return result

if __name__ == "__main__":
    # Test with Philippine rivers
    print("Testing Philippine River Service")
    river_data = get_current_river_height()
    if river_data:
        print(f"Current river: {river_data['river_name']}")
        print(f"Height: {river_data['current_height']}m")
    else:
        print("No river data available")
