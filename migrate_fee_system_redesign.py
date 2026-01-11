"""
Fee System Redesign Migration Script
=====================================
This script migrates the database to support the new fee management system with:
- Fee templates (base fees per seat type and quota)
- Student categories (caste categories)
- Seat types (Government/Management) and quota types (Merit/Category)
- Additional fees as JSON
- Auto-generation tracking

Run this script AFTER backing up your database!
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import FeeTemplate, Student, FeeStructure, User
from sqlalchemy import text
from datetime import datetime

def run_migration():
    """Execute the migration"""
    with app.app_context():
        print("=" * 70)
        print("FEE SYSTEM REDESIGN MIGRATION")
        print("=" * 70)
        print()
        
        # Step 1: Create fee_templates table
        print("[1/7] Creating fee_templates table...")
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS fee_templates (
                    fee_template_id VARCHAR(36) PRIMARY KEY,
                    academic_year VARCHAR(20) NOT NULL,
                    seat_type VARCHAR(20) NOT NULL,
                    quota_type VARCHAR(20),
                    base_fees REAL NOT NULL,
                    created_by_user_id VARCHAR(36) NOT NULL,
                    description TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_deleted INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
                )
            """))
            
            # Create unique index separately (SQLite doesn't support UNIQUE KEY in CREATE TABLE)
            db.session.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uix_fee_template_year_seat_quota 
                ON fee_templates(academic_year, seat_type, quota_type, is_deleted)
            """))
            
            # Create regular index
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_fee_template_year_seat 
                ON fee_templates(academic_year, seat_type, quota_type)
            """))
            
            db.session.commit()
            print("✓ fee_templates table created successfully")
        except Exception as e:
            print(f"✗ Error creating fee_templates table: {e}")
            db.session.rollback()
            return False
        
        # Step 2: Add new columns to students table
        print("\n[2/7] Adding new columns to students table...")
        columns_to_add = [
            ("category", "VARCHAR(20)"),
            ("seat_type", "VARCHAR(20)"),
            ("quota_type", "VARCHAR(20)")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                db.session.execute(text(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}"))
                db.session.commit()
                print(f"✓ Added column: {col_name}")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"  Column {col_name} already exists, skipping...")
                    db.session.rollback()
                else:
                    print(f"✗ Error adding column {col_name}: {e}")
                    db.session.rollback()
                    return False
        
        # Step 3: Add new columns to fee_structures table
        print("\n[3/7] Adding new columns to fee_structures table...")
        fee_structure_columns = [
            ("template_id", "VARCHAR(36)"),
            ("additional_fees", "TEXT"),  # SQLite doesn't have JSON type, use TEXT
            ("is_auto_generated", "INTEGER DEFAULT 0")  # SQLite uses INTEGER for BOOLEAN
        ]
        
        for col_name, col_type in fee_structure_columns:
            try:
                db.session.execute(text(f"ALTER TABLE fee_structures ADD COLUMN {col_name} {col_type}"))
                db.session.commit()
                print(f"✓ Added column: {col_name}")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"  Column {col_name} already exists, skipping...")
                    db.session.rollback()
                else:
                    print(f"✗ Error adding column {col_name}: {e}")
                    db.session.rollback()
                    return False
        
        # Step 4: Add foreign key for template_id
        print("\n[4/7] Adding foreign key constraint for template_id...")
        try:
            db.session.execute(text("""
                ALTER TABLE fee_structures 
                ADD CONSTRAINT fk_fee_structure_template 
                FOREIGN KEY (template_id) REFERENCES fee_templates(fee_template_id)
            """))
            db.session.commit()
            print("✓ Foreign key constraint added")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e):
                print("  Foreign key already exists, skipping...")
                db.session.rollback()
            else:
                print(f"⚠ Warning: Could not add foreign key: {e}")
                db.session.rollback()
                # Continue anyway - not critical
        
        # Step 5: Set default values for existing students
        print("\n[5/7] Setting default values for existing students...")
        try:
            # Set default category to GENERAL
            db.session.execute(text("""
                UPDATE students 
                SET category = 'GENERAL' 
                WHERE category IS NULL AND is_deleted = 0
            """))
            
            # Set default seat_type to GOVERNMENT
            db.session.execute(text("""
                UPDATE students 
                SET seat_type = 'GOVERNMENT' 
                WHERE seat_type IS NULL AND is_deleted = 0
            """))
            
            # Set default quota_type to MERIT for Government seats
            db.session.execute(text("""
                UPDATE students 
                SET quota_type = 'MERIT' 
                WHERE quota_type IS NULL AND seat_type = 'GOVERNMENT' AND is_deleted = 0
            """))
            
            db.session.commit()
            print("✓ Default values set for existing students")
        except Exception as e:
            print(f"✗ Error setting default values: {e}")
            db.session.rollback()
            return False
        
        # Step 6: Mark existing fee structures as not auto-generated
        print("\n[6/7] Marking existing fee structures...")
        try:
            db.session.execute(text("""
                UPDATE fee_structures 
                SET is_auto_generated = 0 
                WHERE is_auto_generated IS NULL
            """))
            db.session.commit()
            print("✓ Existing fee structures marked as manual")
        except Exception as e:
            print(f"✗ Error marking fee structures: {e}")
            db.session.rollback()
            return False
        
        # Step 7: Create default fee templates for 2025-2026
        print("\n[7/7] Creating default fee templates for 2025-2026...")
        try:
            # Get first admin user
            admin_user = User.query.join(User.role).filter(User.role.has(role_name='admin')).first()
            if not admin_user:
                print("⚠ No admin user found, using first user...")
                admin_user = User.query.first()
            
            if not admin_user:
                print("✗ No users found in database!")
                return False
            
            templates = [
                {
                    'academic_year': '2025-2026',
                    'seat_type': 'GOVERNMENT',
                    'quota_type': 'MERIT',
                    'base_fees': 25000.0,
                    'description': 'Government seat - Merit quota (General category meritorious students)'
                },
                {
                    'academic_year': '2025-2026',
                    'seat_type': 'GOVERNMENT',
                    'quota_type': 'CATEGORY',
                    'base_fees': 15000.0,
                    'description': 'Government seat - Category quota (Reserved categories: SC/ST/2A/2B/3A/3B/CAT1)'
                },
                {
                    'academic_year': '2025-2026',
                    'seat_type': 'MANAGEMENT',
                    'quota_type': None,
                    'base_fees': 75000.0,
                    'description': 'Management seat'
                }
            ]
            
            for template_data in templates:
                # Check if template already exists
                existing = FeeTemplate.query.filter_by(
                    academic_year=template_data['academic_year'],
                    seat_type=template_data['seat_type'],
                    quota_type=template_data['quota_type'],
                    is_deleted=False
                ).first()
                
                if existing:
                    print(f"  Template already exists: {template_data['seat_type']} - {template_data['quota_type']}")
                    continue
                
                template = FeeTemplate(
                    academic_year=template_data['academic_year'],
                    seat_type=template_data['seat_type'],
                    quota_type=template_data['quota_type'],
                    base_fees=template_data['base_fees'],
                    description=template_data['description'],
                    created_by_user_id=admin_user.user_id
                )
                db.session.add(template)
                print(f"✓ Created template: {template_data['seat_type']} - {template_data['quota_type']} (₹{template_data['base_fees']:,.0f})")
            
            db.session.commit()
            print("✓ Default fee templates created")
        except Exception as e:
            print(f"✗ Error creating fee templates: {e}")
            db.session.rollback()
            return False
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nSummary:")
        print("- fee_templates table created")
        print("- Students table updated with category, seat_type, quota_type")
        print("- FeeStructure table updated with template_id, additional_fees, is_auto_generated")
        print("- Default values set for existing students")
        print("- Default fee templates created for 2025-2026")
        print("\nNext steps:")
        print("1. Verify the migration by checking the database")
        print("2. Test the new fee management features")
        print("3. Update student categories and seat types as needed")
        print()
        
        return True

if __name__ == "__main__":
    print("\n⚠ WARNING: This will modify your database!")
    print("Make sure you have backed up your database before proceeding.\n")
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if response == "yes":
        success = run_migration()
        sys.exit(0 if success else 1)
    else:
        print("\nMigration cancelled.")
        sys.exit(0)
