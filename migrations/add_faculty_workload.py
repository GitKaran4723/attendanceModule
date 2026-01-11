"""Add workload_hours_per_week to Faculty table"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def upgrade():
    """Add workload_hours_per_week column to faculties table"""
    with app.app_context():
        try:
            # Use text() for raw SQL with SQLAlchemy 2.0+
            from sqlalchemy import text
            
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(faculties)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'workload_hours_per_week' not in columns:
                db.session.execute(text(
                    "ALTER TABLE faculties ADD COLUMN workload_hours_per_week INTEGER DEFAULT 0"
                ))
                db.session.commit()
                print("✓ Added workload_hours_per_week column to faculties table")
            else:
                print("✓ Column workload_hours_per_week already exists")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            raise

if __name__ == '__main__':
    upgrade()
