"""
Database Migration Script for Internal Marks System
Adds new columns to the tests table
"""

import sqlite3
import os

# Get the database path - it's in the instance folder
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'attendance.db')

print("=" * 60)
print("Internal Marks System - Database Migration")
print("=" * 60)

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n✓ Connected to database")
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(tests)")
    columns = [column[1] for column in cursor.fetchall()]
    
    migrations_needed = []
    if 'component_type' not in columns:
        migrations_needed.append('component_type')
    if 'weightage' not in columns:
        migrations_needed.append('weightage')
    if 'description' not in columns:
        migrations_needed.append('description')
    if 'is_published' not in columns:
        migrations_needed.append('is_published')
    
    if not migrations_needed:
        print("\n✓ All columns already exist. No migration needed.")
        conn.close()
        exit(0)
    
    print(f"\n→ Columns to add: {', '.join(migrations_needed)}")
    
    # Add component_type column
    if 'component_type' in migrations_needed:
        print("\n→ Adding component_type column...")
        cursor.execute("""
            ALTER TABLE tests 
            ADD COLUMN component_type TEXT NOT NULL DEFAULT 'test'
        """)
        print("  ✓ component_type added")
    
    # Add weightage column
    if 'weightage' in migrations_needed:
        print("\n→ Adding weightage column...")
        cursor.execute("""
            ALTER TABLE tests 
            ADD COLUMN weightage REAL
        """)
        print("  ✓ weightage added")
    
    # Add description column
    if 'description' in migrations_needed:
        print("\n→ Adding description column...")
        cursor.execute("""
            ALTER TABLE tests 
            ADD COLUMN description TEXT
        """)
        print("  ✓ description added")
    
    # Add is_published column
    if 'is_published' in migrations_needed:
        print("\n→ Adding is_published column...")
        cursor.execute("""
            ALTER TABLE tests 
            ADD COLUMN is_published INTEGER NOT NULL DEFAULT 0
        """)
        print("  ✓ is_published added")
    
    # Commit changes
    conn.commit()
    print("\n✓ Migration completed successfully!")
    
    # Verify columns
    cursor.execute("PRAGMA table_info(tests)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"\n✓ Current columns in tests table: {', '.join(columns)}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("Migration completed. You can now use the Internal Marks system.")
    print("=" * 60)
    
except sqlite3.Error as e:
    print(f"\n✗ Database error: {e}")
    print("\nPlease ensure:")
    print("  1. The database file exists")
    print("  2. You have write permissions")
    print("  3. The database is not locked by another process")
    exit(1)
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    exit(1)
