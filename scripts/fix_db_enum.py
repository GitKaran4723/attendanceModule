
import sqlite3
import os

# Path to DB
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'attendance.db')
print(f"Connecting to database at: {db_path}")

try:
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for 'completed' status
    cursor.execute("SELECT count(*) FROM attendance_sessions WHERE status = 'completed'")
    count = cursor.fetchone()[0]
    print(f"Found {count} records with status='completed'")
    
    if count > 0:
        cursor.execute("UPDATE attendance_sessions SET status = 'finalized' WHERE status = 'completed'")
        conn.commit()
        print(f"Successfully updated {cursor.rowcount} records to 'finalized'")
    else:
        print("No records need fixing.")
        
    conn.close()

except Exception as e:
    print(f"Error: {e}")
