"""
Fix Section Unique Constraint - Complete Fix
This script completely removes the old constraint and updates the database properly.
"""

from app import app, db
from sqlalchemy import text, inspect

def fix_constraint():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            indexes = inspector.get_indexes('sections')
            
            print("🔍 Current indexes on sections table:")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx['column_names']}")
            
            # Drop ALL unique constraints/indexes
            print("\n🔧 Dropping all old constraints...")
            constraints_to_drop = ['uix_section_program', 'uix_section_program_semester']
            
            for constraint in constraints_to_drop:
                try:
                    db.session.execute(text(f"DROP INDEX IF EXISTS {constraint}"))
                    print(f"  ✅ Dropped {constraint}")
                except:
                    print(f"  ℹ️  {constraint} doesn't exist")
            
            db.session.commit()
            
            # Create new proper constraint that allows same section name in different semesters
            print("\n🔧 Creating new unique constraint...")
            db.session.execute(text(
                "CREATE UNIQUE INDEX uix_section_unique "
                "ON sections(section_name, program_id, COALESCE(current_semester, -1), COALESCE(academic_year, '')) "
                "WHERE is_deleted = 0"
            ))
            db.session.commit()
            print("✅ New constraint created successfully!")
            
            print("\n✅ Database updated! You can now:")
            print("  - Add Section A for Semester 1")
            print("  - Add Section A for Semester 4")
            print("  - Add Section A for different academic years")
            print("  All in the same program!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_constraint()
