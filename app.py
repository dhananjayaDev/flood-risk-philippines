"""
Philippine Flood Monitor - Public Dashboard
Real-time Philippine river and weather monitoring without database dependencies.
"""

from app import create_app, socketio

# Create the Flask app
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'app': app}

if __name__ == '__main__':
    print("🌊 Starting Philippine Flood Monitor - Public Dashboard")
    print("📍 Real-time weather and river data for the Philippines")
    print("🚫 No authentication required - Public access only")
    print("💾 No database - Real-time API data only")
    
    # Run the app
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)