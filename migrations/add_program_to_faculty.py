"""
Database Migration Script: Add program_id to Faculty table

This script adds the program_id column to the faculties table to associate 
faculty members with specific programs/departments.

Run this script once to update an existing database.
For new databases, the models.py will create the table with this column.
"""

import sys
import os

# Add parent directory to path so we can import app and models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Faculty, Program

def add_program_id_to_faculties():
    """Add program_id column to faculties table"""
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('faculties')]
            
            if 'program_id' in columns:
                print("✓ Column 'program_id' already exists in faculties table")
                return
            
            print("Adding 'program_id' column to faculties table...")
            
            # SQLite has limited ALTER TABLE support
            # We'll just add the column - SQLAlchemy ORM will handle the foreign key relationship
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    'ALTER TABLE faculties ADD COLUMN program_id VARCHAR(36)'
                ))
                conn.commit()
            
            print("✓ Successfully added 'program_id' column to faculties table")
            print("\n📝 Note: Foreign key relationship is managed by SQLAlchemy ORM.")
            print("   The column is now available and faculty can be assigned to programs!")
            print("\nMigration completed successfully!")
            
        except Exception as e:
            print(f"✗ Error during migration: {str(e)}")
            print("\nIf you're starting fresh, you can delete the database and restart the app.")
            print("The new database will be created with the correct schema automatically.")
            db.session.rollback()


if __name__ == '__main__':
    print("="*60)
    print("Faculty Program Assignment Migration")
    print("="*60)
    print("\nThis will add program_id field to the faculties table.")
    print("Existing faculty records will have NULL program_id (can be updated later).\n")
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        add_program_id_to_faculties()
    else:
        print("Migration cancelled.")
