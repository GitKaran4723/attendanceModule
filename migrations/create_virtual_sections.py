"""Create virtual sections for existing subjects with carries_section=False"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, get_or_create_virtual_section
from models import Subject

def create_virtual_sections():
    """Create virtual sections for all subjects that don't carry sections"""
    with app.app_context():
        try:
            # Find all subjects with carries_section=False
            subjects = Subject.query.filter_by(carries_section=False, is_deleted=False).all()
            
            print(f"Found {len(subjects)} subjects without section requirement")
            
            created_count = 0
            for subject in subjects:
                print(f"Processing: {subject.subject_code} - {subject.subject_name}")
                virtual_section = get_or_create_virtual_section(subject)
                if virtual_section:
                    print(f"  ✓ Virtual section created/found: {virtual_section.section_name}")
                    created_count += 1
            
            print(f"\n✓ Processed {created_count} virtual sections")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            raise

if __name__ == '__main__':
    create_virtual_sections()
