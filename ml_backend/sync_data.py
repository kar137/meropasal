#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_sync_manager import main

if __name__ == '__main__':
    print("Starting data sync...")
    main()
