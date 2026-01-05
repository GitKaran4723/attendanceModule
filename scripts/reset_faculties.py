from app import app, db
from models import Faculty, User, Role

def reset_faculties():
    """
    Hard deletes all Faculty records and their associated User accounts.
    """
    with app.app_context():
        try:
            print("Starting faculty data reset...")
            
            # 1. Delete all Faculty records (Hard Delete)
            deleted_faculties = Faculty.query.delete()
            print(f"Deleted {deleted_faculties} records from 'faculties' table.")
            
            # 2. Delete all User accounts with 'faculty' role
            faculty_role = Role.query.filter_by(role_name='faculty').first()
            if faculty_role:
                deleted_users = User.query.filter_by(role_id=faculty_role.role_id).delete()
                print(f"Deleted {deleted_users} records from 'users' table (Role: faculty).")
            else:
                print("Warning: 'faculty' role not found!")
            
            db.session.commit()
            print("✓ Successfully reset all faculty data.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting data: {e}")

if __name__ == "__main__":
    reset_faculties()
