"""
Check and fix student status values
"""

import sqlite3
import os

DB_PATH = 'instance/attendance.db'

def check_and_fix_status():
    """Check student status values and fix them"""
    
    print("\n" + "="*70)
    print("CHECK AND FIX STUDENT STATUS")
    print("="*70)
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check current status values
        print("\n1. Checking current status values...")
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM students 
            WHERE is_deleted = 0
            GROUP BY status
        """)
        
        status_counts = cursor.fetchall()
        print("\n   Current status distribution:")
        for status, count in status_counts:
            print(f"     - {status or 'NULL'}: {count} students")
        
        # Count students with non-active status
        cursor.execute("""
            SELECT COUNT(*) 
            FROM students 
            WHERE is_deleted = 0 AND (status IS NULL OR status != 'active')
        """)
        inactive_count = cursor.fetchone()[0]
        
        if inactive_count == 0:
            print("\n✓ All students already have 'active' status!")
            return
        
        print(f"\n2. Found {inactive_count} students with non-active status")
        
        # Ask for confirmation
        response = input("\nSet all non-deleted students to 'active' status? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        
        # Update all non-deleted students to active
        cursor.execute("""
            UPDATE students 
            SET status = 'active' 
            WHERE is_deleted = 0 AND (status IS NULL OR status != 'active')
        """)
        
        updated = cursor.rowcount
        conn.commit()
        
        print(f"\n✓ Updated {updated} students to 'active' status")
        
        # Show new distribution
        print("\n3. New status distribution:")
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM students 
            WHERE is_deleted = 0
            GROUP BY status
        """)
        
        for status, count in cursor.fetchall():
            print(f"     - {status or 'NULL'}: {count} students")
        
        print("\n" + "="*70)
        print("✓ DONE!")
        print("="*70)
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {str(e)}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_fix_status()
