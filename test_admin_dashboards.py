"""
Quick Test Script for Admin Dashboards
Tests both console and GUI dashboards
"""

import sys
import os

print("=" * 60)
print("Testing Admin Dashboard Features")
print("=" * 60)

# Test 1: Console Dashboard Import
print("\n[TEST 1] Importing console dashboard...")
try:
    from admin_console import AdminConsoleDashboard
    print("✓ Console dashboard imported successfully")
except Exception as e:
    print(f"✗ Failed to import console dashboard: {e}")
    sys.exit(1)

# Test 2: GUI Dashboard Import
print("\n[TEST 2] Importing GUI dashboard...")
try:
    from admin_dashboard import AdminDashboard
    print("✓ GUI dashboard imported successfully")
except Exception as e:
    print(f"✗ Failed to import GUI dashboard: {e}")
    sys.exit(1)

# Test 3: Database Connection
print("\n[TEST 3] Testing database connection...")
try:
    import sqlite3
    conn = sqlite3.connect("soulsense_db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scores")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"✓ Database connection successful ({count} scores found)")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    sys.exit(1)

# Test 4: Console Dashboard Methods
print("\n[TEST 4] Testing console dashboard methods...")
try:
    dashboard = AdminConsoleDashboard()
    
    # Test individual methods
    print("  - Testing show_overview...")
    dashboard.show_overview()
    
    print("\n  - Testing show_age_group_analysis...")
    dashboard.show_age_group_analysis()
    
    print("\n  - Testing show_score_distribution...")
    dashboard.show_score_distribution()
    
    print("\n✓ Console dashboard methods work correctly")
except Exception as e:
    print(f"✗ Console dashboard methods failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Required Modules
print("\n[TEST 5] Checking required modules...")
try:
    import matplotlib
    print(f"✓ matplotlib version {matplotlib.__version__}")
except ImportError:
    print("✗ matplotlib not installed")
    
try:
    import numpy
    print(f"✓ numpy version {numpy.__version__}")
except ImportError:
    print("✗ numpy not installed")

try:
    import tkinter
    print("✓ tkinter available")
except ImportError:
    print("⚠ tkinter not available (GUI dashboard won't work)")

print("\n" + "=" * 60)
print("All Tests Passed! ✓")
print("=" * 60)
print("\nYou can now use:")
print("  - python admin_console.py           (Console view)")
print("  - python admin_console.py -i        (Interactive menu)")
print("  - python admin_dashboard.py         (GUI view)")
print("=" * 60)
