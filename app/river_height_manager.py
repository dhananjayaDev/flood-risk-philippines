"""
River Height Manager for Kalu Ganga
Handles recording and retrieving river height data from kalugangadb
"""

from datetime import datetime, timedelta
import pytz
from app import db
from app.models import RiverHeight
from app.river import get_current_river_height

def record_river_height(height=None, timestamp=None, river_name="Kalu Ganga (Ratnapura)"):
    """
    Record a river height measurement for Kalu Ganga.
    
    Args:
        height (float): River height in meters. If None, fetches current height from API
        timestamp (datetime): Timestamp for the measurement. If None, uses current time
        river_name (str): Name of the river (default: Kalu Ganga)
    
    Returns:
        RiverHeight: The created record or None if failed
    """
    try:
        # Use current time if no timestamp provided
        if timestamp is None:
            timestamp = datetime.now(pytz.timezone('Asia/Colombo'))
        
        # Fetch current height from API if not provided
        if height is None:
            current_data = get_current_river_height(river_name)
            if current_data:
                height = current_data['current_height']
            else:
                print("Warning: Could not fetch current river height from API")
                return None
        
        # Create new river height record
        river_height = RiverHeight(
            river_name=river_name,
            timestamp=timestamp,
            height=height
        )
        
        # Add to database
        db.session.add(river_height)
        db.session.commit()
        
        print(f"Recorded river height: {height}m at {timestamp}")
        return river_height
        
    except Exception as e:
        db.session.rollback()
        print(f"Error recording river height: {e}")
        return None

def get_river_heights(limit=100, start_date=None, end_date=None):
    """
    Retrieve Kalu Ganga river height records from the database.
    
    Args:
        limit (int): Maximum number of records to return
        start_date (datetime): Start date for filtering (inclusive)
        end_date (datetime): End date for filtering (inclusive)
    
    Returns:
        list: List of RiverHeight objects for Kalu Ganga only
    """
    try:
        return RiverHeight.get_kalu_ganga_data(limit, start_date, end_date)
    except Exception as e:
        print(f"Error retrieving river heights: {e}")
        return []

def get_latest_river_height():
    """
    Get the most recent Kalu Ganga river height record.
    
    Returns:
        RiverHeight: Latest Kalu Ganga record or None if no records exist
    """
    try:
        return RiverHeight.get_latest_kalu_ganga_height()
    except Exception as e:
        print(f"Error getting latest river height: {e}")
        return None

def get_river_heights_last_24h():
    """
    Get Kalu Ganga river height records from the last 24 hours.
    
    Returns:
        list: List of RiverHeight objects for Kalu Ganga from last 24 hours
    """
    try:
        return RiverHeight.get_kalu_ganga_last_24h()
    except Exception as e:
        print(f"Error getting last 24h river heights: {e}")
        return []

def get_river_heights_last_7days():
    """
    Get Kalu Ganga river height records from the last 7 days.
    
    Returns:
        list: List of RiverHeight objects for Kalu Ganga from last 7 days
    """
    try:
        return RiverHeight.get_kalu_ganga_last_7days()
    except Exception as e:
        print(f"Error getting last 7 days river heights: {e}")
        return []

def delete_old_records(days_to_keep=365):
    """
    Delete river height records older than specified days.
    
    Args:
        days_to_keep (int): Number of days of data to keep (default: 365)
    
    Returns:
        int: Number of records deleted
    """
    try:
        cutoff_date = datetime.now(pytz.timezone('Asia/Colombo')) - timedelta(days=days_to_keep)
        
        old_records = RiverHeight.query.filter(
            RiverHeight.timestamp < cutoff_date
        ).all()
        
        count = len(old_records)
        
        for record in old_records:
            db.session.delete(record)
        
        db.session.commit()
        print(f"Deleted {count} old river height records")
        return count
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting old records: {e}")
        return 0

def get_river_height_statistics():
    """
    Get basic statistics for Kalu Ganga river height data.
    
    Returns:
        dict: Statistics including count, min, max, average, latest
    """
    try:
        return RiverHeight.get_kalu_ganga_statistics()
    except Exception as e:
        print(f"Error getting river height statistics: {e}")
        return {
            'count': 0,
            'min_height': 0,
            'max_height': 0,
            'avg_height': 0,
            'latest_height': 0,
            'latest_timestamp': None
        }

if __name__ == "__main__":
    # Test the functions
    print("Testing River Height Manager...")
    
    # Test recording a height
    test_height = record_river_height(height=2.5)
    if test_height:
        print(f"✓ Successfully recorded height: {test_height}")
    
    # Test getting latest height
    latest = get_latest_river_height()
    if latest:
        print(f"✓ Latest height: {latest.height}m at {latest.timestamp}")
    
    # Test getting statistics
    stats = get_river_height_statistics()
    print(f"✓ Statistics: {stats}")
