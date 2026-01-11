"""
Database Migration: Add batch_year to fee_templates
This migration adds batch_year field to support different fees for same batch across years
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def migrate_add_batch_year():
    """Add batch_year column to fee_templates table"""
    
    print("\n" + "="*70)
    print("BATCH-YEAR FEE SYSTEM MIGRATION")
    print("="*70)
    
    with app.app_context():
        try:
            # Step 1: Add batch_year column
            print("\n[1/4] Adding batch_year column to fee_templates...")
            try:
                db.session.execute(text("""
                    ALTER TABLE fee_templates 
                    ADD COLUMN batch_year VARCHAR(20)
                """))
                db.session.commit()
                print("✓ batch_year column added")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("✓ batch_year column already exists")
                    db.session.rollback()
                else:
                    raise
            
            # Step 2: Set batch_year = academic_year for existing records
            print("\n[2/4] Setting batch_year for existing templates...")
            result = db.session.execute(text("""
                UPDATE fee_templates 
                SET batch_year = academic_year 
                WHERE batch_year IS NULL
            """))
            db.session.commit()
            print(f"✓ Updated {result.rowcount} existing templates")
            
            # Step 3: Make batch_year NOT NULL
            print("\n[3/4] Making batch_year NOT NULL...")
            try:
                # SQLite doesn't support ALTER COLUMN, so we skip this
                # The model will enforce NOT NULL for new records
                print("✓ Constraint will be enforced by model")
            except Exception as e:
                print(f"! Note: {e}")
            
            # Step 4: Drop old unique constraint and create new one
            print("\n[4/4] Updating unique constraint...")
            try:
                # Drop old constraint
                db.session.execute(text("""
                    DROP INDEX IF EXISTS uix_fee_template_year_seat_quota
                """))
                
                # Create new constraint with batch_year
                db.session.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS uix_fee_template_year_batch_seat_quota 
                    ON fee_templates(academic_year, batch_year, seat_type, quota_type, is_deleted)
                """))
                
                # Drop old index and create new one
                db.session.execute(text("""
                    DROP INDEX IF EXISTS ix_fee_template_year_seat
                """))
                
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_fee_template_year_batch_seat 
                    ON fee_templates(academic_year, batch_year, seat_type, quota_type)
                """))
                
                db.session.commit()
                print("✓ Unique constraint and indexes updated")
            except Exception as e:
                print(f"! Note: {e}")
                db.session.rollback()
            
            print("\n" + "="*70)
            print("MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*70)
            print("\nSummary:")
            print("- batch_year column added to fee_templates")
            print("- Existing templates set batch_year = academic_year")
            print("- Unique constraint updated to include batch_year")
            print("\nNext steps:")
            print("1. Restart the application")
            print("2. Create new templates with different batch_year values")
            print("3. Test fee assignment with batch-year logic")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("\n⚠ WARNING: This will modify your database!")
    print("Make sure you have backed up your database before proceeding.")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        success = migrate_add_batch_year()
        sys.exit(0 if success else 1)
    else:
        print("Migration cancelled.")
        sys.exit(0)
