from app import app, db
from sqlalchemy import text

def fix_schema():
    """
    Drops and recreates the subject_allocations table to apply schema changes.
    """
    with app.app_context():
        try:
            print("Applying schema fix for SubjectAllocation...")
            
            # Drop table
            # Using raw SQL to be sure, or metadata.
            # db.metadata.tables['subject_allocations'].drop(db.engine)
            # But let's use raw sql for safety against metadata mismatch
            
            db.session.execute(text("DROP TABLE IF EXISTS subject_allocations"))
            print("Dropped table 'subject_allocations'.")
            
            # Recreate
            db.create_all()
            print("Recreated database tables (including subject_allocations).")
            
            db.session.commit()
            print("✓ Schema fix applied successfully.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error applying fix: {e}")

if __name__ == "__main__":
    fix_schema()
