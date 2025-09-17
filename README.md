# Flood Risk Management Application

A modern Flask-based web application for flood detection and risk management with user authentication and a responsive dashboard.

## Features

- **User Authentication**: Secure login and registration system
- **Modern UI**: Clean, responsive design with Bootstrap 5
- **Dashboard**: Real-time monitoring interface with statistics and alerts
- **Flood Risk Management**: Core functionality for flood detection and monitoring
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Project Structure

```
flood-risk01/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── auth/                # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── forms.py         # Login/Registration forms
│   │   └── routes.py        # Auth routes
│   └── main/                # Main application blueprint
│       ├── __init__.py
│       └── routes.py        # Main routes
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Landing page
│   ├── home.html           # Dashboard
│   └── auth/               # Authentication templates
│       ├── login.html
│       └── register.html
├── static/                 # Static files
│   ├── css/
│   │   └── style.css       # Custom styles
│   ├── js/
│   │   └── main.js         # JavaScript functionality
│   └── images/             # Image assets
├── venv/                   # Virtual environment
├── app.py                  # Application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone or Download

Download the project files to your local machine.

### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Environment Variables

Create a `.env` file in the project root (optional):
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
```

### Step 5: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### First Time Setup

1. **Register a new account**: Visit `/auth/register` to create your first user account
2. **Login**: Use your credentials to access the dashboard
3. **Explore**: Navigate through the dashboard to see the flood risk management interface

### Features Overview

- **Landing Page**: Public homepage with feature overview
- **Authentication**: Secure user registration and login
- **Dashboard**: Private area with flood monitoring statistics and controls
- **Responsive Design**: Optimized for all device sizes

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (with SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with WTForms
- **Frontend**: Bootstrap 5, Font Awesome icons
- **Styling**: Custom CSS with modern design principles
- **JavaScript**: Vanilla JS with Bootstrap components

## Development

### Adding New Features

1. Create new blueprints in the `app/` directory
2. Add routes, forms, and templates as needed
3. Update the main `__init__.py` to register new blueprints
4. Test thoroughly before deployment

### Database Management

The application uses SQLite by default. To reset the database:

```bash
# Delete the database file
rm app.db

# Restart the application to recreate tables
python app.py
```

### Customization

- **Styling**: Modify `static/css/style.css` for custom designs
- **JavaScript**: Update `static/js/main.js` for additional functionality
- **Configuration**: Adjust settings in `config.py`

## Security Notes

- Change the `SECRET_KEY` in production
- Use environment variables for sensitive configuration
- Consider using a production database (PostgreSQL, MySQL)
- Implement HTTPS in production
- Regular security updates for dependencies

## Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure a reverse proxy (Nginx)
4. Use a production database
5. Set up SSL certificates
6. Configure proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of a larger flood detection system. Please ensure proper licensing for production use.

## Support

For questions or issues, please refer to the Flask documentation or create an issue in the project repository.
