import sqlite3
import os

def migrate():
    db_path = 'instance/attendance.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Starting migration...")
        
        # 1. Get existing columns from students table
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'name' in column_names and 'first_name' not in column_names:
            print("Migration already applied.")
            return

        # 2. Create a temporary table with the new schema
        # We need to get the full CREATE TABLE statement or rebuild it
        # For simplicity, let's just add the column if it doesn't exist, populate it, then we can drop columns if needed
        # But SQLite doesn't support DROP COLUMN in older versions (< 3.35.0)
        
        print("Adding 'name' column...")
        cursor.execute("ALTER TABLE students ADD COLUMN name VARCHAR(205)")
        
        print("Populating 'name' column...")
        cursor.execute("UPDATE students SET name = first_name || ' ' || last_name")
        
        # If we want to be very thorough and really REMOVE the columns, 
        # we have to do the table swap dance.
        
        print("Finalizing changes...")
        conn.commit()
        print("Migration successful! 'name' column added and populated.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
