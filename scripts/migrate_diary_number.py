from app import app, db
from sqlalchemy import text
import uuid

def migrate():
    with app.app_context():
        print("Migrating database schema for diary_number...")
        try:
            # Check if column exists
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(attendance_sessions)"))
                columns = [row.name for row in result]
                
                if 'diary_number' not in columns:
                    print("Adding 'diary_number' column to 'attendance_sessions' table...")
                    # Add column as nullable first to avoid issues with existing rows
                    conn.execute(text("ALTER TABLE attendance_sessions ADD COLUMN diary_number VARCHAR(20)"))
                    conn.commit()
                    
                    # Optional: Generate diary numbers for existing rows
                    # For simplicity, we'll just use the ID or a sequence
                    # result = conn.execute(text("SELECT attendance_session_id FROM attendance_sessions"))
                    # sessions = result.fetchall()
                    # for s in sessions:
                    #     dn = f"DN-{s[0][:8].upper()}"
                    #     conn.execute(text("UPDATE attendance_sessions SET diary_number = :dn WHERE attendance_session_id = :id"), {"dn": dn, "id": s[0]})
                    # conn.commit()
                    
                    print("Migration successful: Added 'diary_number' column.")
                else:
                    print("Column 'diary_number' already exists. No changes needed.")
                    
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    migrate()
