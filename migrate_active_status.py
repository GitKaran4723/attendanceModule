from app import app, db
from sqlalchemy import text, inspect

def migrate():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Existing tables: {tables}")
            
            target_table = None
            for t in tables:
                if t.lower() in ['student', 'students']:
                    target_table = t
                    break
            
            if not target_table:
                print(f"Error: Could not find student table. Tables found: {tables}")
                return

            columns = [c['name'] for c in inspector.get_columns(target_table)]
            if 'is_active' in columns:
                print("Column 'is_active' already exists.")
            else:
                print(f"Adding 'is_active' column to {target_table}...")
                with db.engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE {target_table} ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                    conn.commit()
                print("Column added successfully.")
                
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
