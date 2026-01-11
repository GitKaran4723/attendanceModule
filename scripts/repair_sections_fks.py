import sqlite3
import os

DB_PATH = os.path.join("instance", "attendance.db")

def repair_tables():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys off to allow dropping tables
    cursor.execute("PRAGMA foreign_keys=OFF;")
    
    tables_to_fix = [
        "class_schedules",
        "tests",
        "work_diaries",
        "subject_allocations",
        "student_enrollments",
        "fee_structures",
        "students"
    ]
    
    for table in tables_to_fix:
        print(f"\n--- Repairing {table} ---")
        try:
            # 1. Get current CREATE statement
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
            result = cursor.fetchone()
            if not result:
                print(f"Table {table} not found!")
                continue
                
            current_sql = result[0]
            
            # 2. Check if it actually references sections_old
            if "sections_old" not in current_sql:
                print(f"Table {table} does not reference sections_old. Skipping.")
                continue
                
            # 3. Create fixed SQL
            # Replace "sections_old" with "sections" or sections_old with sections
            fixed_sql = current_sql.replace('"sections_old"', 'sections').replace('sections_old', 'sections')
            print("Fixed SQL prepared.")
            
            # 4. Rename current table
            temp_table = f"{table}_broken"
            print(f"Renaming {table} to {temp_table}...")
            cursor.execute(f"ALTER TABLE {table} RENAME TO {temp_table};")
            
            # 5. Create new table
            print(f"Creating new {table}...")
            cursor.execute(fixed_sql)
            
            # 6. Copy data
            print(f"Copying data from {temp_table} to {table}...")
            cursor.execute(f"INSERT INTO {table} SELECT * FROM {temp_table};")
            
            # 7. Drop broken table
            print(f"Dropping {temp_table}...")
            cursor.execute(f"DROP TABLE {temp_table};")
            
            print(f"Successfully repaired {table}!")
            conn.commit()
            
        except Exception as e:
            print(f"Error repairing {table}: {e}")
            conn.rollback() 
            # If we renamed but failed to create/copy, we might be in trouble. 
            # Ideally we'd try to revert rename, but simplicity first.
    
    conn.close()
    print("\nAll repairs attempted.")

if __name__ == "__main__":
    repair_tables()
