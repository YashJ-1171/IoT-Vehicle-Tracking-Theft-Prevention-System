"""
▲ Vercel Serverless Function Entry Point
========================================
Routes incoming HTTP requests on Vercel to the Flask application.
"""

import os
import sys

# Ensure project root is in Python module search path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dashboard.app import app

# Export WSGI app handler for Vercel Python runtime
handler = app
