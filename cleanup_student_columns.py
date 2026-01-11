"""
Clean up duplicate/unnecessary columns from students table
Removes: name, dob, semester_id, is_active
"""

import sqlite3
import os

DB_PATH = 'instance/attendance.db'

def cleanup_student_columns():
    """Remove duplicate columns from students table"""
    
    print("\n" + "="*70)
    print("CLEANUP STUDENT TABLE COLUMNS")
    print("="*70)
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if students table exists
        print("\n0. Checking for students table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        result = cursor.fetchone()
        
        if not result:
            print("   ✗ 'students' table not found!")
            print("\n   Available tables:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            for row in cursor.fetchall():
                print(f"     - {row[0]}")
            return
        
        print("   ✓ Table 'students' found")
        
        # Step 1: Create new table with correct schema
        print("\n1. Creating new students table with clean schema...")
        cursor.execute("""
            CREATE TABLE students_new (
                student_id VARCHAR(36) PRIMARY KEY NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                roll_number VARCHAR(64),
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                date_of_birth DATE,
                address TEXT,
                guardian_name VARCHAR(200),
                guardian_phone VARCHAR(20),
                usn VARCHAR(64),
                email VARCHAR(255),
                phone VARCHAR(20),
                program_id VARCHAR(36),
                section_id VARCHAR(36),
                admission_year INTEGER,
                current_semester INTEGER,
                status VARCHAR(32),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                is_deleted BOOLEAN NOT NULL,
                gender VARCHAR(10),
                joining_academic_year VARCHAR(20),
                category VARCHAR(20),
                seat_type VARCHAR(20),
                quota_type VARCHAR(20),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (program_id) REFERENCES programs(program_id),
                FOREIGN KEY (section_id) REFERENCES sections(section_id)
            )
        """)
        print("   ✓ New table created")
        
        # Step 2: Copy data from old table to new table
        print("\n2. Copying data to new table...")
        cursor.execute("""
            INSERT INTO students_new (
                student_id, user_id, roll_number, first_name, last_name,
                date_of_birth, address, guardian_name, guardian_phone, usn,
                email, phone, program_id, section_id, admission_year,
                current_semester, status, created_at, updated_at, is_deleted,
                gender, joining_academic_year, category, seat_type, quota_type
            )
            SELECT 
                student_id, user_id, roll_number, first_name, last_name,
                date_of_birth, address, guardian_name, guardian_phone, usn,
                email, phone, program_id, section_id, admission_year,
                current_semester, status, created_at, updated_at, is_deleted,
                gender, joining_academic_year, category, seat_type, quota_type
            FROM students
        """)
        rows_copied = cursor.rowcount
        print(f"   ✓ Copied {rows_copied} student records")
        
        # Step 3: Drop old table
        print("\n3. Dropping old table...")
        cursor.execute("DROP TABLE students")
        print("   ✓ Old table dropped")
        
        # Step 4: Rename new table
        print("\n4. Renaming new table...")
        cursor.execute("ALTER TABLE students_new RENAME TO students")
        print("   ✓ Table renamed")
        
        # Step 5: Recreate indexes
        print("\n5. Recreating indexes...")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uix_roll_number ON students(roll_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_program ON students(program_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_section ON students(section_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_user ON students(user_id)")
        print("   ✓ Indexes created")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*70)
        print("✓ CLEANUP COMPLETE!")
        print("="*70)
        print("\nRemoved columns:")
        print("  - name (duplicate of first_name + last_name)")
        print("  - dob (duplicate of date_of_birth)")
        print("  - semester_id (wrong type, kept current_semester)")
        print("  - is_active (duplicate of status)")
        print("\n" + "="*70)
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {str(e)}")
        print("\nRolling back changes...")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will modify the database structure!")
    print("   Make sure you have a backup before proceeding.")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_student_columns()
    else:
        print("Cancelled.")
