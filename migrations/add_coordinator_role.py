"""
Migration: Add Coordinator Role Support
- Add is_coordinator field to faculties table
- Add GPS accuracy fields to faculty_attendance table
- Create program_coordinators association table
"""

import sqlite3
from datetime import datetime

def migrate():
    """Apply migration to add coordinator support"""
    conn = sqlite3.connect('instance/attendance.db')
    cursor = conn.cursor()
    
    try:
        print("Starting migration: Add Coordinator Role Support...")
        
        # 1. Add is_coordinator to faculties table
        print("1. Adding is_coordinator column to faculties table...")
        try:
            cursor.execute("""
                ALTER TABLE faculties 
                ADD COLUMN is_coordinator BOOLEAN NOT NULL DEFAULT 0
            """)
            print("   ✓ Added is_coordinator column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠ is_coordinator column already exists, skipping")
            else:
                raise
        
        # 2. Add GPS accuracy fields to faculty_attendance table
        print("2. Adding GPS accuracy columns to faculty_attendance table...")
        try:
            cursor.execute("""
                ALTER TABLE faculty_attendance 
                ADD COLUMN check_in_accuracy REAL
            """)
            print("   ✓ Added check_in_accuracy column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠ check_in_accuracy column already exists, skipping")
            else:
                raise
        
        try:
            cursor.execute("""
                ALTER TABLE faculty_attendance 
                ADD COLUMN check_out_accuracy REAL
            """)
            print("   ✓ Added check_out_accuracy column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠ check_out_accuracy column already exists, skipping")
            else:
                raise
        
        # 3. Create program_coordinators table
        print("3. Creating program_coordinators table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS program_coordinators (
                assignment_id TEXT PRIMARY KEY,
                faculty_id TEXT NOT NULL,
                program_id TEXT NOT NULL,
                assigned_by TEXT,
                assigned_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (faculty_id) REFERENCES faculties (faculty_id),
                FOREIGN KEY (program_id) REFERENCES programs (program_id),
                FOREIGN KEY (assigned_by) REFERENCES users (user_id),
                UNIQUE (faculty_id, program_id, is_deleted)
            )
        """)
        print("   ✓ Created program_coordinators table")
        
        # 4. Create indexes for program_coordinators
        print("4. Creating indexes for program_coordinators table...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_program_coordinators_faculty 
            ON program_coordinators (faculty_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_program_coordinators_program 
            ON program_coordinators (program_id)
        """)
        print("   ✓ Created indexes")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
