"""
Fix Student Current Semester
-----------------------------
Updates all students' current_semester based on their section data
This is needed for the enrollment system to work properly.

Usage:
    python migrations/fix_student_semesters.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Student, Section

def run_fix():
    """Update all students with their section's semester"""
    with app.app_context():
        print("=" * 60)
        print("Fixing Student Current Semester")
        print("=" * 60)
        
        # Get all active students
        students = Student.query.filter_by(is_deleted=False).all()
        
        updated_count = 0
        for student in students:
            if student.section_id:
                # Get section
                section = Section.query.get(student.section_id)
                if section and section.semester:
                    # Update student's current_semester to match section semester
                    student.current_semester = section.semester
                    updated_count += 1
                    print(f"  {student.name or student.usn}: Semester set to {section.semester}")
            else:
                # If no section, try to infer from admission year or set to 1
                if not student.current_semester:
                    student.current_semester = 1  # Default to semester 1
                    updated_count += 1
                    print(f"  {student.name or student.usn}: Default set to Semester 1")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✓ Updated {updated_count} students")
        print("=" * 60)
        print("\nStudents are now ready for enrollment!")

if __name__ == "__main__":
    run_fix()
