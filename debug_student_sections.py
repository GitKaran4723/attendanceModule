"""
Debug student section assignments
Check what's actually in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Student, Section

def debug_student_sections():
    """Check student section assignments"""
    
    print("\n" + "="*70)
    print("DEBUG STUDENT SECTIONS")
    print("="*70)
    
    with app.app_context():
        # Get first 10 students
        students = Student.query.filter_by(is_deleted=False).limit(10).all()
        
        print(f"\nChecking {len(students)} students:\n")
        
        for student in students:
            section_name = "NONE"
            if student.section_id:
                section = Section.query.get(student.section_id)
                if section:
                    section_name = section.section_name
            
            print(f"Roll: {student.roll_number}")
            print(f"  Name: {student.name}")
            print(f"  Status: {student.status}")
            print(f"  Section ID: {student.section_id}")
            print(f"  Section Name: {section_name}")
            print(f"  Semester: {student.current_semester}")
            print()

if __name__ == "__main__":
    debug_student_sections()
