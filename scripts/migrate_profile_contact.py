"""
Migration Script: Add profile contact fields
Phase 53: Profile Page Redesign

Adds the following columns to personal_profiles table:
- email (String)
- phone (String)
- date_of_birth (String)
- gender (String)
- address (Text)
"""

import sqlite3
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import DB_PATH

def migrate():
    """Add new contact columns to personal_profiles table."""
    print(f"[Migration] Connecting to database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(personal_profiles)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    print(f"[Migration] Existing columns: {existing_columns}")
    
    # New columns to add
    new_columns = [
        ("email", "TEXT"),
        ("phone", "TEXT"),
        ("date_of_birth", "TEXT"),
        ("gender", "TEXT"),
        ("address", "TEXT"),
    ]
    
    added = 0
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE personal_profiles ADD COLUMN {col_name} {col_type}")
                print(f"[Migration] ✅ Added column: {col_name}")
                added += 1
            except sqlite3.OperationalError as e:
                print(f"[Migration] ⚠️ Column {col_name} might already exist: {e}")
        else:
            print(f"[Migration] ⏭️ Column {col_name} already exists, skipping")
    
    conn.commit()
    conn.close()
    
    print(f"[Migration] Complete! Added {added} new columns.")
    return added

if __name__ == "__main__":
    migrate()
