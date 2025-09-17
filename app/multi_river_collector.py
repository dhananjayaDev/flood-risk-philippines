"""
Multi-River Data Collector
Collects data from all 6 rivers automatically every 30 minutes
"""

import threading
import time
from datetime import datetime
import pytz
from app import db
from app.models import (
    RiverHeight, KuruGangaHeight, WeyGangaHeight, 
    DenawakaGangaHeight, KukuleGangaHeight, GalathuraOyaHeight
)
from app.river import get_current_river_height

# River configuration with API keys and models
RIVER_CONFIG = {
    "Kalu Ganga (Ratnapura)": {
        "api_key": "2bq292rf6uz",
        "model": RiverHeight,
        "bind_key": "kalugangadb",
        "priority": 1
    },
    "Kuru Ganga (Kuruvita)": {
        "api_key": "76k6cqo0ipwk", 
        "model": KuruGangaHeight,
        "bind_key": "kuruganga",
        "priority": 1
    },
    "Wey Ganga (Kahawaththa)": {
        "api_key": "5f4al4atv8ws",
        "model": WeyGangaHeight,
        "bind_key": "weyganga",
        "priority": 2
    },
    "Denawaka Ganga (Pelmadulla)": {
        "api_key": "1kp1hhh7zbu",
        "model": DenawakaGangaHeight,
        "bind_key": "denawakaganga",
        "priority": 1
    },
    "Kukule Ganga (Kalawana)": {
        "api_key": "5asknpp28bs",
        "model": KukuleGangaHeight,
        "bind_key": "kukuleganga",
        "priority": 1
    },
    "Galathura Oya (Ayagama)": {
        "api_key": "6nb2troqa5c0",
        "model": GalathuraOyaHeight,
        "bind_key": "galathuraoya",
        "priority": 3
    }
}

class MultiRiverCollector:
    """Multi-river data collection system"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.app = None
    
    def start_collection(self, app):
        """Start automatic data collection for all rivers"""
        if self.running:
            print("⚠️ Multi-river data collection already running")
            return True
        
        try:
            self.app = app
            self.running = True
            self.thread = threading.Thread(target=self._collect_loop, daemon=True)
            self.thread.start()
            
            print("🌊 Multi-river data collection started - collecting from 6 rivers every 30 minutes")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start multi-river data collection: {e}")
            return False
    
    def stop_collection(self):
        """Stop data collection"""
        if not self.running:
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        print("⏹️ Multi-river data collection stopped")
        return True
    
    def _collect_loop(self):
        """Main collection loop - runs every 30 minutes"""
        with self.app.app_context():
            # Wait 2 minutes before first collection to avoid duplicates on restart
            print("⏳ Waiting 2 minutes before first collection to avoid duplicates...")
            for i in range(120):  # 2 minutes
                if not self.running:
                    return
                time.sleep(1)
            
            while self.running:
                try:
                    # Collect data from all rivers
                    self._collect_all_rivers()
                    
                    # Wait 30 minutes (1800 seconds)
                    for i in range(1800):  # 30 minutes = 1800 seconds
                        if not self.running:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"❌ Error in multi-river collection: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
    
    def _collect_all_rivers(self):
        """Collect data from all rivers"""
        current_time = datetime.now(pytz.timezone('Asia/Colombo'))
        print(f"\n🌊 Collecting data from all rivers at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        success_count = 0
        total_rivers = len(RIVER_CONFIG)
        
        for river_name, config in RIVER_CONFIG.items():
            try:
                print(f"📡 Collecting {river_name}...")
                
                # Get current river height from API
                current_data = get_current_river_height(river_name)
                
                if current_data:
                    height = current_data['current_height']
                    timestamp_str = current_data['timestamp']
                    # Convert timestamp string to datetime object
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M').replace(tzinfo=pytz.timezone('Asia/Colombo'))
                    print(f"  ✅ {river_name}: {height}m at {timestamp}")
                else:
                    print(f"  ⚠️ {river_name}: No API data, using fallback")
                    height = 0.5  # Fallback value
                    timestamp = datetime.now(pytz.timezone('Asia/Colombo'))
                
                # Check for duplicate records (same timestamp and height)
                model_class = config['model']
                existing_record = model_class.query.filter(
                    model_class.timestamp == timestamp,
                    model_class.height == height
                ).first()
                
                if existing_record:
                    print(f"  ⚠️ {river_name}: Duplicate record found, skipping")
                    success_count += 1
                    continue
                
                # Record the data using the specific model
                river_record = model_class(
                    river_name=river_name,
                    timestamp=timestamp,
                    height=height
                )
                
                db.session.add(river_record)
                db.session.commit()
                
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ {river_name}: Error - {e}")
                db.session.rollback()
                continue
        
        print(f"📊 Collection complete: {success_count}/{total_rivers} rivers successful")
        
        # Show statistics for each river
        self._show_statistics()
    
    def _show_statistics(self):
        """Show statistics for all rivers"""
        print("\n📈 River Data Statistics:")
        
        for river_name, config in RIVER_CONFIG.items():
            try:
                model_class = config['model']
                total_records = model_class.query.count()
                latest = model_class.query.order_by(model_class.timestamp.desc()).first()
                
                if latest:
                    print(f"  {river_name}: {total_records} records, latest: {latest.height}m at {latest.timestamp}")
                else:
                    print(f"  {river_name}: {total_records} records, no data yet")
                    
            except Exception as e:
                print(f"  {river_name}: Error getting statistics - {e}")
    
    def collect_now(self):
        """Manually collect data from all rivers now"""
        if not self.app:
            return False
        
        with self.app.app_context():
            self._collect_all_rivers()
            return True
    
    def get_status(self):
        """Get collection status"""
        return {
            'running': self.running,
            'rivers': list(RIVER_CONFIG.keys()),
            'next_collection': 'In 30 minutes' if self.running else 'Not running'
        }

# Global collector instance
multi_collector = MultiRiverCollector()

def start_multi_river_collection(app):
    """Start automatic multi-river data collection"""
    return multi_collector.start_collection(app)

def stop_multi_river_collection():
    """Stop automatic multi-river data collection"""
    return multi_collector.stop_collection()

def collect_all_rivers_now():
    """Manually collect data from all rivers now"""
    return multi_collector.collect_now()

def get_multi_river_status():
    """Get multi-river collection status"""
    return multi_collector.get_status()
