"""
Add current_academic_year field to programs table
Each program (UG/PG) can have its own academic year
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'instance/attendance.db'

def add_academic_year_to_programs():
    """Add current_academic_year to programs table"""
    
    print("\n" + "="*70)
    print("ADD ACADEMIC YEAR TO PROGRAMS")
    print("="*70)
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add to programs table
        print("\n1. Adding current_academic_year to programs table...")
        try:
            cursor.execute("""
                ALTER TABLE programs 
                ADD COLUMN current_academic_year VARCHAR(20)
            """)
            print("   ✓ Column added to programs")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ℹ Column already exists in programs")
            else:
                raise
        
        # Set default academic year for existing programs
        print("\n2. Setting default academic year for existing programs...")
        current_year = datetime.now().year
        default_academic_year = f"{current_year}-{current_year + 1}"
        
        cursor.execute("""
            UPDATE programs 
            SET current_academic_year = ?
            WHERE current_academic_year IS NULL
        """, (default_academic_year,))
        
        updated_programs = cursor.rowcount
        print(f"   ✓ Updated {updated_programs} programs")
        
        # Show programs
        print("\n3. Current programs:")
        cursor.execute("SELECT program_code, program_name, current_academic_year FROM programs WHERE is_deleted = 0")
        programs = cursor.fetchall()
        for prog in programs:
            print(f"   - {prog[0]}: {prog[1]} → {prog[2]}")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "="*70)
        print("✓ MIGRATION COMPLETE!")
        print("="*70)
        print(f"\nDefault Academic Year: {default_academic_year}")
        print(f"Programs Updated: {updated_programs}")
        print("\nNow each program can have its own academic year!")
        print("UG and PG programs can run on different schedules.")
        print("\n" + "="*70)
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {str(e)}")
        print("\nRolling back changes...")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will add a new column to the programs table!")
    print("   Make sure you have a backup before proceeding.")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() == 'yes':
        add_academic_year_to_programs()
    else:
        print("Cancelled.")
