import sqlite3
import os

DB_PATH = os.path.join("instance", "attendance.db")

def fix_schema():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys=OFF;")
    
    try:
        # 1. Rename existing sections table
        print("Renaming sections table...")
        cursor.execute("ALTER TABLE sections RENAME TO sections_old;")
        
        # 2. Create new sections table with CORRECT ForeignKey
        print("Creating new sections table...")
        create_sql = """
        CREATE TABLE sections (
            created_at DATETIME WITHOUT TIME ZONE,
            updated_at DATETIME WITHOUT TIME ZONE,
            is_deleted BOOLEAN,
            section_id VARCHAR(36) NOT NULL,
            section_name VARCHAR(64) NOT NULL,
            program_id VARCHAR(36) NOT NULL,
            year_of_study INTEGER,
            academic_year VARCHAR(20),
            current_semester INTEGER,
            class_teacher_id VARCHAR(36),
            is_elective BOOLEAN DEFAULT 0,
            linked_subject_id VARCHAR(36),
            PRIMARY KEY (section_id),
            FOREIGN KEY(program_id) REFERENCES programs (program_id),
            FOREIGN KEY(class_teacher_id) REFERENCES faculties (faculty_id),
            FOREIGN KEY(linked_subject_id) REFERENCES subjects (subject_id),
            CONSTRAINT uix_section_program_semester UNIQUE (section_name, program_id, current_semester, academic_year)
        );
        """
        cursor.execute(create_sql)
        
        # 3. Copy data
        # Note: We need to handle the new columns 'is_elective' and 'linked_subject_id' which are not in old table.
        # We will set them to default (Null/False) implicitly by not selecting them from source.
        print("Copying data...")
        cursor.execute("""
            INSERT INTO sections (
                created_at, updated_at, is_deleted, 
                section_id, section_name, program_id, 
                year_of_study, academic_year, current_semester, 
                class_teacher_id
            )
            SELECT 
                created_at, updated_at, is_deleted, 
                section_id, section_name, program_id, 
                year_of_study, academic_year, current_semester, 
                class_teacher_id
            FROM sections_old;
        """)
        
        # 4. Create Index (if it existed)
        print("Recreating indices...")
        cursor.execute("CREATE INDEX ix_sections_class_teacher_id ON sections (class_teacher_id);")
        cursor.execute("CREATE INDEX ix_sections_program_id ON sections (program_id);")
        
        # 5. Drop old table
        print("Dropping old table...")
        cursor.execute("DROP TABLE sections_old;")
        
        conn.commit()
        print("Schema fix successful!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
