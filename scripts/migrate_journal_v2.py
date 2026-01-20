import os
import sys
from sqlalchemy import create_engine, text

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import DATABASE_URL, DB_PATH

def migrate_journal_v2():
    """Add PR #6 fields to journal_entries table"""
    print(f"Migrating Database at: {DB_PATH}")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get existing columns
        result = conn.execute(text("PRAGMA table_info(journal_entries)"))
        columns = [row[1] for row in result.fetchall()]
        
        # Define new columns
        # Format: (name, sql_type)
        new_columns = [
            ("screen_time_mins", "INTEGER"),
            ("stress_level", "INTEGER"),
            ("stress_triggers", "TEXT"),
            ("daily_schedule", "TEXT")
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding column: {col_name}...")
                try:
                    conn.execute(text(f"ALTER TABLE journal_entries ADD COLUMN {col_name} {col_type}"))
                    print(f"✅ Added {col_name}")
                except Exception as e:
                    print(f"❌ Failed to add {col_name}: {e}")
            else:
                print(f"ℹ️ Column {col_name} already exists. Skipping.")
        
        conn.commit()
        print("Migration V2 (Journal Expansion) Completed Successfully.")

if __name__ == "__main__":
    migrate_journal_v2()
