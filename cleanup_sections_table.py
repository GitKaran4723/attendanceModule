"""
Clean up duplicate column from sections table
Removes: name (duplicate of section_name)
"""

import sqlite3
import os

DB_PATH = 'instance/attendance.db'

def cleanup_sections_table():
    """Remove duplicate name column from sections table"""
    
    print("\n" + "="*70)
    print("CLEANUP SECTIONS TABLE")
    print("="*70)
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if sections table exists
        print("\n1. Checking sections table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sections'")
        if not cursor.fetchone():
            print("   ✗ 'sections' table not found!")
            return
        
        print("   ✓ Table 'sections' found")
        
        # Create new table with correct schema
        print("\n2. Creating new sections table...")
        cursor.execute("""
            CREATE TABLE sections_new (
                section_id VARCHAR(36) PRIMARY KEY NOT NULL,
                section_name VARCHAR(64) NOT NULL,
                program_id VARCHAR(36) NOT NULL,
                year_of_study INTEGER,
                academic_year VARCHAR(20),
                current_semester INTEGER,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                is_deleted BOOLEAN NOT NULL,
                class_teacher_id VARCHAR(36),
                FOREIGN KEY (program_id) REFERENCES programs(program_id),
                FOREIGN KEY (class_teacher_id) REFERENCES faculty(faculty_id)
            )
        """)
        print("   ✓ New table created")
        
        # Copy data
        print("\n3. Copying data...")
        cursor.execute("""
            INSERT INTO sections_new (
                section_id, section_name, program_id, year_of_study,
                academic_year, current_semester, created_at, updated_at,
                is_deleted, class_teacher_id
            )
            SELECT 
                section_id, section_name, program_id, year_of_study,
                academic_year, current_semester, created_at, updated_at,
                is_deleted, class_teacher_id
            FROM sections
        """)
        rows_copied = cursor.rowcount
        print(f"   ✓ Copied {rows_copied} section records")
        
        # Drop old table
        print("\n4. Dropping old table...")
        cursor.execute("DROP TABLE sections")
        print("   ✓ Old table dropped")
        
        # Rename new table
        print("\n5. Renaming new table...")
        cursor.execute("ALTER TABLE sections_new RENAME TO sections")
        print("   ✓ Table renamed")
        
        # Recreate indexes
        print("\n6. Recreating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_program ON sections(program_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_teacher ON sections(class_teacher_id)")
        print("   ✓ Indexes created")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*70)
        print("✓ CLEANUP COMPLETE!")
        print("="*70)
        print("\nRemoved columns:")
        print("  - name (duplicate of section_name)")
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
        cleanup_sections_table()
    else:
        print("Cancelled.")
