"""
Migration script to create faculty_attendance table
Run this script to add the faculty check-in/checkout tracking table
"""

import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    try:
        # Create faculty_attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faculty_attendance (
                attendance_id TEXT PRIMARY KEY,
                faculty_id TEXT NOT NULL,
                date DATE NOT NULL,
                check_in_time DATETIME,
                check_in_latitude REAL,
                check_in_longitude REAL,
                check_out_time DATETIME,
                check_out_latitude REAL,
                check_out_longitude REAL,
                check_out_valid BOOLEAN DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (faculty_id) REFERENCES faculty (faculty_id)
            )
        ''')
        
        # Create index
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_faculty_date 
            ON faculty_attendance (faculty_id, date)
        ''')
        
        conn.commit()
        print("✅ Successfully created faculty_attendance table")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
