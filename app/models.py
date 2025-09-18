"""
Models - Database-Free Version
No database models needed for real-time Philippine flood monitoring.
All data is fetched from APIs in real-time.
"""

def get_app_info():
    """Get application information"""
    return {
        'name': 'Philippine Flood Monitor',
        'version': '2.0',
        'description': 'Real-time Philippine river and weather monitoring',
        'database_enabled': False,
        'real_time_only': True
    }
