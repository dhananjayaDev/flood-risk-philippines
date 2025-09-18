import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyCNLAkh8xk2TcX63IQQRNXdZ0hGqAUFmnA'  # Replace with your actual API key
    SQLALCHEMY_BINDS = {
        # River databases
        'kalugangadb': os.environ.get('KALUGANGA_DB_URL') or 'sqlite:///kalugangadb.db',
        'kuruganga': os.environ.get('KURUGANGA_DB_URL') or 'sqlite:///kuruganga.db',
        'weyganga': os.environ.get('WEYGANGA_DB_URL') or 'sqlite:///weyganga.db',
        'denawakaganga': os.environ.get('DENAWAKAGANGA_DB_URL') or 'sqlite:///denawakaganga.db',
        'kukuleganga': os.environ.get('KUKULEGANGA_DB_URL') or 'sqlite:///kukuleganga.db',
        'galathuraoya': os.environ.get('GALATHURAOYA_DB_URL') or 'sqlite:///galathuraoya.db',
        # Weather databases
        'pelmadulla_weather': os.environ.get('PELMADULLA_WEATHER_DB_URL') or 'sqlite:///pelmadulla_weather.db',
        'ratnapura_weather': os.environ.get('RATNAPURA_WEATHER_DB_URL') or 'sqlite:///ratnapura_weather.db',
        'kalawana_weather': os.environ.get('KALAWANA_WEATHER_DB_URL') or 'sqlite:///kalawana_weather.db',
        'kuruvita_weather': os.environ.get('KURUVITA_WEATHER_DB_URL') or 'sqlite:///kuruvita_weather.db',
        'ayagama_weather': os.environ.get('AYAGAMA_WEATHER_DB_URL') or 'sqlite:///ayagama_weather.db',
        'kahawatta_weather': os.environ.get('KAHAWATTA_WEATHER_DB_URL') or 'sqlite:///kahawatta_weather.db',
        # Notification database
        'notification_db': os.environ.get('NOTIFICATION_DB_URL') or 'sqlite:///notification.db'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
