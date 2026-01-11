"""
Add Fee Management Tables
==========================
Migration to add:
1. joining_academic_year field to students table
2. fee_structures table
3. fee_receipts table

Run this migration with: python migrations/add_fee_management.py
"""

from sqlalchemy import create_engine, text
from datetime import datetime
import os

# Get database path from environment or use default
db_path = os.getenv('DATABASE_URL', 'sqlite:///instance/attendance.db')
engine = create_engine(db_path)


def run_migration():
    """Execute the fee management migration"""
    
    with engine.begin() as conn:
        print("Starting fee management migration...")
        
        # Step 1: Add joining_academic_year to students table
        print("\n1. Adding joining_academic_year column to students table...")
        try:
            conn.execute(text("""
                ALTER TABLE students 
                ADD COLUMN joining_academic_year VARCHAR(20)
            """))
            print("   ✓ Column added successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠ Column already exists, skipping...")
            else:
                raise
        
        # Step 2: Populate joining_academic_year from admission_year for existing students
        print("\n2. Populating joining_academic_year for existing students...")
        conn.execute(text("""
            UPDATE students 
            SET joining_academic_year = 
                CAST(admission_year AS TEXT) || '-' || CAST((admission_year + 1) AS TEXT)
            WHERE admission_year IS NOT NULL 
              AND joining_academic_year IS NULL
        """))
        updated_count = conn.execute(text("SELECT COUNT(*) FROM students WHERE joining_academic_year IS NOT NULL")).scalar()
        print(f"   ✓ Updated {updated_count} student records")
        
        # Step 3: Create fee_structures table
        print("\n3. Creating fee_structures table...")
        try:
            conn.execute(text("""
                CREATE TABLE fee_structures (
                    fee_structure_id VARCHAR(36) PRIMARY KEY,
                    student_id VARCHAR(36) NOT NULL,
                    section_id VARCHAR(36) NOT NULL,
                    academic_year VARCHAR(20) NOT NULL,
                    base_fees FLOAT NOT NULL DEFAULT 0,
                    carry_forward FLOAT NOT NULL DEFAULT 0,
                    additional_charges FLOAT NOT NULL DEFAULT 0,
                    total_fees FLOAT NOT NULL,
                    set_by_user_id VARCHAR(36) NOT NULL,
                    is_retained BOOLEAN DEFAULT 0,
                    previous_year VARCHAR(20),
                    remarks TEXT,
                    status VARCHAR(20) DEFAULT 'active',
                    is_deleted BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (section_id) REFERENCES sections(section_id),
                    FOREIGN KEY (set_by_user_id) REFERENCES users(user_id),
                    CONSTRAINT uix_student_year_fee UNIQUE (student_id, academic_year, is_deleted)
                )
            """))
            print("   ✓ Table created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("   ⚠ Table already exists, skipping...")
            else:
                raise
        
        # Step 4: Create indexes for fee_structures
        print("\n4. Creating indexes for fee_structures...")
        try:
            conn.execute(text("""
                CREATE INDEX ix_fee_structure_student_year 
                ON fee_structures(student_id, academic_year)
            """))
            conn.execute(text("""
                CREATE INDEX ix_fee_structures_student_id 
                ON fee_structures(student_id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_fee_structures_academic_year 
                ON fee_structures(academic_year)
            """))
            print("   ✓ Indexes created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("   ⚠ Indexes already exist, skipping...")
            else:
                print(f"   ⚠ Warning: {str(e)}")
        
        # Step 5: Create fee_receipts table
        print("\n5. Creating fee_receipts table...")
        try:
            conn.execute(text("""
                CREATE TABLE fee_receipts (
                    fee_receipt_id VARCHAR(36) PRIMARY KEY,
                    fee_structure_id VARCHAR(36) NOT NULL,
                    student_id VARCHAR(36) NOT NULL,
                    receipt_number VARCHAR(100) NOT NULL UNIQUE,
                    receipt_phone VARCHAR(20) NOT NULL,
                    amount_paid FLOAT NOT NULL,
                    payment_date DATE NOT NULL,
                    payment_mode VARCHAR(50),
                    entered_by_user_id VARCHAR(36) NOT NULL,
                    entered_by_role VARCHAR(20) NOT NULL,
                    approved BOOLEAN NOT NULL DEFAULT 0,
                    approved_by_user_id VARCHAR(36),
                    approved_at DATETIME,
                    remarks TEXT,
                    is_deleted BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(fee_structure_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (entered_by_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (approved_by_user_id) REFERENCES users(user_id)
                )
            """))
            print("   ✓ Table created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("   ⚠ Table already exists, skipping...")
            else:
                raise
        
        # Step 6: Create indexes for fee_receipts
        print("\n6. Creating indexes for fee_receipts...")
        try:
            conn.execute(text("""
                CREATE INDEX ix_fee_receipt_student_structure 
                ON fee_receipts(student_id, fee_structure_id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_fee_receipt_approved 
                ON fee_receipts(approved)
            """))
            conn.execute(text("""
                CREATE INDEX ix_fee_receipts_fee_structure_id 
                ON fee_receipts(fee_structure_id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_fee_receipts_student_id 
                ON fee_receipts(student_id)
            """))
            conn.execute(text("""
                CREATE INDEX ix_fee_receipts_payment_date 
                ON fee_receipts(payment_date)
            """))
            conn.execute(text("""
                CREATE INDEX ix_fee_receipts_receipt_number 
                ON fee_receipts(receipt_number)
            """))
            print("   ✓ Indexes created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("   ⚠ Indexes already exist, skipping...")
            else:
                print(f"   ⚠ Warning: {str(e)}")
        
        print("\n✅ Fee management migration completed successfully!")
        print("\nSummary:")
        print("  - Added joining_academic_year column to students")
        print("  - Created fee_structures table")
        print("  - Created fee_receipts table")
        print("  - Created all necessary indexes")


def rollback_migration():
    """Rollback the fee management migration (USE WITH CAUTION!)"""
    
    response = input("\n⚠️  WARNING: This will delete all fee data. Are you sure? (type 'YES' to confirm): ")
    if response != 'YES':
        print("Rollback cancelled.")
        return
    
    with engine.begin() as conn:
        print("\nRolling back fee management migration...")
        
        # Drop tables in reverse order (to respect foreign keys)
        print("1. Dropping fee_receipts table...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS fee_receipts"))
            print("   ✓ Table dropped")
        except Exception as e:
            print(f"   ⚠ Error: {str(e)}")
        
        print("\n2. Dropping fee_structures table...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS fee_structures"))
            print("   ✓ Table dropped")
        except Exception as e:
            print(f"   ⚠ Error: {str(e)}")
        
        print("\n3. Removing joining_academic_year column from students...")
        try:
            # SQLite doesn't support DROP COLUMN directly, so we'd need to recreate the table
            print("   ⚠ Manual intervention required for SQLite")
            print("   Column 'joining_academic_year' will remain but will not be used")
        except Exception as e:
            print(f"   ⚠ Error: {str(e)}")
        
        print("\n✅ Rollback completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback_migration()
    else:
        run_migration()
