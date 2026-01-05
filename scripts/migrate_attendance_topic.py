from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("Migrating database schema...")
        try:
            # Check if column exists
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(attendance_sessions)"))
                columns = [row.name for row in result]
                
                if 'topic_taught' not in columns:
                    print("Adding 'topic_taught' column to 'attendance_sessions' table...")
                    conn.execute(text("ALTER TABLE attendance_sessions ADD COLUMN topic_taught VARCHAR(255)"))
                    conn.commit()
                    print("Migration successful: Added 'topic_taught' column.")
                else:
                    print("Column 'topic_taught' already exists. No changes needed.")
                    
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    migrate()
