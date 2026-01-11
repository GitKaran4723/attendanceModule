"""
Update student semester values based on their joining year
This script calculates the current semester for each student
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import app to use the correct database path (instance/attendance.db)
from app import app, db
from models import Student

def calculate_semester(joining_year):
    """Calculate current semester based on joining academic year"""
    # Parse joining year (e.g., "2024-2025" -> 2024)
    if not joining_year:
        return None
    
    try:
        start_year = int(joining_year.split('-')[0])
    except:
        return None
    
    # Get current year
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    # Academic year starts in June/July
    # If current month is Jan-May, we're in second half of academic year
    if current_month <= 5:
        academic_year = current_year - 1
    else:
        academic_year = current_year
    
    # Calculate years since joining
    years_since_joining = academic_year - start_year
    
    # Each year has 2 semesters
    # If we're in Jan-May (second half), add 1 to semester
    base_semester = (years_since_joining * 2) + 1
    if current_month <= 5:
        base_semester += 1
    
    # Cap at 8 semesters (4 years)
    return min(base_semester, 8)

def update_student_semesters():
    """Update all students' current_semester field"""
    
    print("\n" + "="*70)
    print("UPDATE STUDENT SEMESTERS")
    print("="*70)
    
    with app.app_context():
        students = Student.query.filter_by(is_deleted=False, status='active').all()
        
        print(f"\nFound {len(students)} active students")
        
        updated_count = 0
        
        for student in students:
            old_semester = student.current_semester
            new_semester = calculate_semester(student.joining_academic_year)
            
            if new_semester is None:
                print(f"  ⚠ {student.roll_number}: No joining year, skipping")
                continue
            
            if old_semester != new_semester:
                student.current_semester = new_semester
                updated_count += 1
                print(f"  ✓ {student.roll_number}: {old_semester} → {new_semester} (joined {student.joining_academic_year})")
            else:
                print(f"  - {student.roll_number}: Already correct (semester {new_semester})")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ Updated {updated_count} students")
        else:
            print(f"\n✓ All students already have correct semesters")
        
        print("="*70)

if __name__ == "__main__":
    update_student_semesters()
