"""
Script to reset student passwords to DD-MM-YYYY format
"""
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

# Connect to database
conn = sqlite3.connect('instance/attendance.db')
cursor = conn.cursor()

# Get all students with their user accounts
cursor.execute("""
    SELECT s.student_id, s.roll_number, s.date_of_birth, u.user_id, u.username
    FROM students s
    JOIN users u ON s.user_id = u.user_id
    WHERE s.is_deleted = 0
""")

students = cursor.fetchall()
print(f"Processing {len(students)} students...")
print("=" * 60)

updated = 0
skipped = 0

for student_id, roll_number, dob, user_id, username in students:
    if not dob:
        print(f"SKIP: No DOB for {roll_number}")
        skipped += 1
        continue
        
    try:
        # Parse DOB (Stored as YYYY-MM-DD)
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        
        # Format as DD-MM-YYYY
        new_password = dob_date.strftime('%d-%m-%Y')
        
        # Hash password
        password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        # Update user
        cursor.execute("""
            UPDATE users 
            SET password_hash = ? 
            WHERE user_id = ?
        """, (password_hash, user_id))
        
        print(f"✓ Updated {roll_number}: Password set to {new_password}")
        updated += 1
        
    except ValueError:
        print(f"ERROR: Invalid DOB format for {roll_number}: {dob}")
        skipped += 1
    except Exception as e:
        print(f"ERROR: {str(e)} for {roll_number}")
        skipped += 1

conn.commit()
conn.close()

print("=" * 60)
print(f"Done! Updated {updated} passwords. Skipped {skipped}.")
