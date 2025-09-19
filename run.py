#!/usr/bin/env python3
"""
SehatMind - AI-based Dropout Prediction and Counseling System
Startup script for the application
"""

import os
import sys
from app import app, db

def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        import matplotlib
        import seaborn
        import plotly
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting SehatMind - AI Dropout Prediction System")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create database tables
    create_tables()
    
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Server starting on http://{host}:{port}")
    print("📊 Dashboard available at the root URL")
    print("🔧 API endpoints available at /api/*")
    print("=" * 60)
    
    # Start the application
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down SehatMind...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
