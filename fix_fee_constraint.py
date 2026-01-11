"""
Fix fee_templates unique constraint
This script rebuilds the fee_templates table with the correct unique constraint including batch_year
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def fix_constraint():
    """Rebuild fee_templates table with correct constraint"""
    
    print("\n" + "="*70)
    print("FIX FEE_TEMPLATES CONSTRAINT")
    print("="*70)
    
    with app.app_context():
        try:
            # Step 1: Create backup table
            print("\n[1/5] Creating backup of fee_templates...")
            db.session.execute(text("""
                CREATE TABLE fee_templates_backup AS 
                SELECT * FROM fee_templates
            """))
            db.session.commit()
            print("✓ Backup created")
            
            # Step 2: Drop old table
            print("\n[2/5] Dropping old fee_templates table...")
            db.session.execute(text("DROP TABLE fee_templates"))
            db.session.commit()
            print("✓ Old table dropped")
            
            # Step 3: Create new table with correct constraint
            print("\n[3/5] Creating new fee_templates table...")
            db.session.execute(text("""
                CREATE TABLE fee_templates (
                    fee_template_id VARCHAR(36) PRIMARY KEY,
                    academic_year VARCHAR(20) NOT NULL,
                    batch_year VARCHAR(20) NOT NULL,
                    seat_type VARCHAR(20) NOT NULL,
                    quota_type VARCHAR(20),
                    base_fees REAL NOT NULL,
                    created_by_user_id VARCHAR(36) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    is_deleted INTEGER DEFAULT 0,
                    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id),
                    UNIQUE (academic_year, batch_year, seat_type, quota_type, is_deleted)
                )
            """))
            db.session.commit()
            print("✓ New table created with correct constraint")
            
            # Step 4: Restore data
            print("\n[4/5] Restoring data from backup...")
            db.session.execute(text("""
                INSERT INTO fee_templates 
                (fee_template_id, academic_year, batch_year, seat_type, quota_type, 
                 base_fees, created_by_user_id, description, created_at, updated_at, is_deleted)
                SELECT fee_template_id, academic_year, batch_year, seat_type, quota_type,
                       base_fees, created_by_user_id, description, created_at, updated_at, is_deleted
                FROM fee_templates_backup
            """))
            db.session.commit()
            print("✓ Data restored")
            
            # Step 5: Drop backup
            print("\n[5/5] Cleaning up backup...")
            db.session.execute(text("DROP TABLE fee_templates_backup"))
            db.session.commit()
            print("✓ Backup cleaned up")
            
            # Create indexes
            print("\n[BONUS] Creating indexes...")
            db.session.execute(text("""
                CREATE INDEX ix_fee_template_year_batch_seat 
                ON fee_templates(academic_year, batch_year, seat_type, quota_type)
            """))
            db.session.commit()
            print("✓ Indexes created")
            
            print("\n" + "="*70)
            print("CONSTRAINT FIX COMPLETED SUCCESSFULLY!")
            print("="*70)
            print("\nThe unique constraint now includes batch_year.")
            print("You can now create templates with same academic_year but different batch_year.")
            print("\nNext: Restart your app and try creating templates again.")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Fix failed: {e}")
            db.session.rollback()
            
            # Try to restore from backup if it exists
            try:
                print("\nAttempting to restore from backup...")
                db.session.execute(text("DROP TABLE IF EXISTS fee_templates"))
                db.session.execute(text("ALTER TABLE fee_templates_backup RENAME TO fee_templates"))
                db.session.commit()
                print("✓ Restored from backup")
            except:
                print("✗ Could not restore from backup")
            
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("\n⚠ WARNING: This will rebuild the fee_templates table!")
    print("A backup will be created automatically.")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        success = fix_constraint()
        sys.exit(0 if success else 1)
    else:
        print("Fix cancelled.")
        sys.exit(0)
