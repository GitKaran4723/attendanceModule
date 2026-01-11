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
        print("Starting schema fix...")
        
        # 1. Check if name exists
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'name' not in column_names:
            print("Error: 'name' column missing. Run migrate_student_names.py first.")
            return

        # 2. Create new table without first_name and last_name
        # We'll use a temporary name first
        print("Creating temporary student table...")
        cursor.execute("""
            CREATE TABLE students_new (
                student_id VARCHAR(36) NOT NULL PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL UNIQUE,
                roll_number VARCHAR(64) UNIQUE,
                name VARCHAR(205) NOT NULL,
                date_of_birth DATE,
                address TEXT,
                guardian_name VARCHAR(200),
                guardian_phone VARCHAR(20),
                usn VARCHAR(64),
                email VARCHAR(255),
                phone VARCHAR(20),
                program_id VARCHAR(36),
                section_id VARCHAR(36),
                admission_year INTEGER,
                joining_academic_year VARCHAR(20),
                current_academic_year VARCHAR(20),
                category VARCHAR(20),
                seat_type VARCHAR(20),
                quota_type VARCHAR(20),
                current_semester INTEGER,
                status VARCHAR(32) DEFAULT 'active',
                gender VARCHAR(10),
                created_at DATETIME,
                updated_at DATETIME,
                is_deleted BOOLEAN DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(program_id) REFERENCES programs(program_id),
                FOREIGN KEY(section_id) REFERENCES sections(section_id)
            )
        """)
        
        # 3. Copy data
        print("Copying data from old table to new...")
        cursor.execute("""
            INSERT INTO students_new (
                student_id, user_id, roll_number, name, date_of_birth, address, 
                guardian_name, guardian_phone, usn, email, phone, program_id, 
                section_id, admission_year, joining_academic_year, current_academic_year, 
                category, seat_type, quota_type, current_semester, status, gender, 
                created_at, updated_at, is_deleted
            )
            SELECT 
                student_id, user_id, roll_number, name, date_of_birth, address, 
                guardian_name, guardian_phone, usn, email, phone, program_id, 
                section_id, admission_year, joining_academic_year, current_academic_year, 
                category, seat_type, quota_type, current_semester, status, gender, 
                created_at, updated_at, is_deleted
            FROM students
        """)
        
        # 4. Swap tables
        print("Swapping tables...")
        cursor.execute("DROP TABLE students")
        cursor.execute("ALTER TABLE students_new RENAME TO students")
        
        # 5. Recreate indexes
        print("Recreating indexes...")
        cursor.execute("CREATE INDEX idx_students_user ON students(user_id)")
        cursor.execute("CREATE INDEX ix_students_roll_number ON students(roll_number)")
        cursor.execute("CREATE INDEX ix_students_usn ON students(usn)")
        cursor.execute("CREATE INDEX ix_students_academic_year ON students(current_academic_year)")
        
        conn.commit()
        print("Schema fix successful! 'first_name' and 'last_name' columns removed.")
        
    except Exception as e:
        conn.rollback()
        print(f"Schema fix failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
