#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_api import app

if __name__ == '__main__':
    print("Starting ML Backend Sync API...")
    print("API will be available at: http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
