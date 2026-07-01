"""
🌐 WSGI Entry Point for Cloud & Production Deployment
=====================================================
Used by production WSGI servers (Gunicorn, Waitress, uWSGI) when deployed
to cloud platforms like Render, Railway, Heroku, or AWS.
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from dashboard.app import app

if __name__ == "__main__":
    app.run()
