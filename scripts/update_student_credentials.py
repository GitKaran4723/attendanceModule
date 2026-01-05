"""
Script to update student login credentials
Username: USN (roll_number)
Password: Date of Birth in DDMMYYYY format
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

print(f"Found {len(students)} students to update")
print("=" * 80)

updated_count = 0
skipped_count = 0

for student_id, roll_number, dob, user_id, current_username in students:
    # Skip if no roll number
    if not roll_number:
        print(f"SKIP: Student {student_id} has no roll number")
        skipped_count += 1
        continue
    
    # Parse date of birth
    if dob:
        try:
            # Try to parse the date (assuming it's stored as YYYY-MM-DD or similar)
            if isinstance(dob, str):
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']:
                    try:
                        dob_date = datetime.strptime(dob, fmt)
                        break
                    except:
                        continue
                else:
                    print(f"SKIP: Could not parse DOB for {roll_number}: {dob}")
                    skipped_count += 1
                    continue
            else:
                print(f"SKIP: Invalid DOB format for {roll_number}")
                skipped_count += 1
                continue
            
            # Format as DDMMYYYY
            password = dob_date.strftime('%d%m%Y')
        except Exception as e:
            print(f"SKIP: Error parsing DOB for {roll_number}: {e}")
            skipped_count += 1
            continue
    else:
        # Default password if no DOB
        password = "01012000"  # Default: 01/01/2000
        print(f"WARN: No DOB for {roll_number}, using default password: {password}")
    
    # Hash the password
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Update username to roll_number and password
    cursor.execute("""
        UPDATE users
        SET username = ?, password_hash = ?
        WHERE user_id = ?
    """, (roll_number, password_hash, user_id))
    
    print(f"✓ Updated: {roll_number} | Password: {password}")
    updated_count += 1

# Commit changes
conn.commit()
conn.close()

print("=" * 80)
print(f"\n✓ Updated {updated_count} student accounts")
print(f"⊘ Skipped {skipped_count} accounts")
print("\nStudents can now login with:")
print("  Username: Their USN (e.g., U03NK25S0180)")
print("  Password: Their DOB in DDMMYYYY format (e.g., 15032003)")
