"""
Add current_academic_year to students and faculties tables
This allows filtering all data by academic year for reports
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/attendance.db'

def add_academic_year_to_all():
    """Add current_academic_year to students and faculties tables"""
    
    print("\n" + "="*70)
    print("ADD ACADEMIC YEAR TO STUDENTS AND FACULTY")
    print("="*70)
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add to students table
        print("\n1. Adding current_academic_year to students table...")
        try:
            cursor.execute("""
                ALTER TABLE students 
                ADD COLUMN current_academic_year VARCHAR(20)
            """)
            print("   ✓ Column added to students")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ Column already exists in students")
            else:
                raise
        
        # Add to faculties table
        print("\n2. Adding current_academic_year to faculties table...")
        try:
            cursor.execute("""
                ALTER TABLE faculties 
                ADD COLUMN current_academic_year VARCHAR(20)
            """)
            print("   ✓ Column added to faculties")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ Column already exists in faculties")
            else:
                raise
        
        # Set academic year for students based on their program
        print("\n3. Setting academic year for students from their programs...")
        cursor.execute("""
            UPDATE students 
            SET current_academic_year = (
                SELECT p.current_academic_year 
                FROM programs p 
                WHERE p.program_id = students.program_id
            )
            WHERE students.current_academic_year IS NULL 
            AND students.program_id IS NOT NULL
        """)
        updated_students = cursor.rowcount
        print(f"   ✓ Updated {updated_students} students")
        
        # Set default for students without programs
        current_year = datetime.now().year
        default_academic_year = f"{current_year}-{current_year + 1}"
        
        cursor.execute("""
            UPDATE students 
            SET current_academic_year = ?
            WHERE current_academic_year IS NULL
        """, (default_academic_year,))
        default_students = cursor.rowcount
        print(f"   ✓ Set default for {default_students} students without programs")
        
        # Set academic year for faculty (default to current year)
        print("\n4. Setting academic year for faculty...")
        cursor.execute("""
            UPDATE faculties 
            SET current_academic_year = ?
            WHERE current_academic_year IS NULL
        """, (default_academic_year,))
        updated_faculty = cursor.rowcount
        print(f"   ✓ Updated {updated_faculty} faculty members")
        
        # Show summary
        print("\n5. Summary by academic year:")
        cursor.execute("""
            SELECT current_academic_year, COUNT(*) 
            FROM students 
            WHERE is_deleted = 0 
            GROUP BY current_academic_year
        """)
        student_summary = cursor.fetchall()
        print("   Students:")
        for year, count in student_summary:
            print(f"     - {year or 'Not Set'}: {count} students")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*70)
        print("✓ MIGRATION COMPLETE!")
        print("="*70)
        print(f"\nDefault Academic Year: {default_academic_year}")
        print(f"Students Updated: {updated_students + default_students}")
        print(f"Faculty Updated: {updated_faculty}")
        print("\nNow all reports will include academic year context!")
        print("\n" + "="*70)
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {str(e)}")
        print("\nRolling back changes...")
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will add academic year columns to students and faculties!")
    print("   Make sure you have a backup before proceeding.")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() == 'yes':
        add_academic_year_to_all()
    else:
        print("Cancelled.")
