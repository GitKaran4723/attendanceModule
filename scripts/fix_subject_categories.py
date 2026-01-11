import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Subject

def fix_categories():
    with app.app_context():
        print("Checking for subjects with NULL subject_category...")
        null_subjects = Subject.query.filter(Subject.subject_category == None).all()
        print(f"Found {len(null_subjects)} subjects with NULL category.")
        
        if len(null_subjects) > 0:
            print("Updating them to 'compulsory'...")
            for s in null_subjects:
                s.subject_category = 'compulsory'
                # Also set elective_group to None just in case (though it's text)
            
            db.session.commit()
            print("Update complete.")
        else:
            print("No updates needed.")

if __name__ == "__main__":
    fix_categories()
