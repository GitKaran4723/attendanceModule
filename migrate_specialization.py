
import sqlite3
import os
from app import app, db

# Path to database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'attendance.db')

print(f"Migrating database at: {db_path}")

try:
    # 1. Add is_specialization column to subjects table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking subjects table...")
    try:
        # Check if column exists
        cursor.execute("SELECT is_specialization FROM subjects LIMIT 1")
        print("Column 'is_specialization' already exists.")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        print("Adding 'is_specialization' column...")
        cursor.execute("ALTER TABLE subjects ADD COLUMN is_specialization BOOLEAN DEFAULT 0")
        conn.commit()
        print("Column added successfully.")
    
    conn.close()

    # 2. Create new tables (StudentSubjectEnrollment)
    print("Creating new tables...")
    with app.app_context():
        db.create_all()
        print("Database schema updated successfully!")

except Exception as e:
    print(f"Error during migration: {e}")
