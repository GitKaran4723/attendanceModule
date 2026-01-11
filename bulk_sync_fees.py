"""
Bulk Fee Assignment Script
Processes all existing students and assigns/updates their fee structures
based on Joining Year, Current Academic Year, and Seat Type.
"""

import os
import sys
from datetime import datetime

# Add the current directory to path so it can find models and fee_helpers
sys.path.append(os.getcwd())

from app import app
from models import db, Student
from fee_helpers import assign_fee_to_student

def bulk_assign_fees():
    """Loop through all students and assign fees"""
    with app.app_context():
        print("\n" + "="*70)
        print("BULK FEE ASSIGNMENT PROCESS")
        print("="*70)
        
        # Get all active students who are not deleted
        students = Student.query.filter_by(is_deleted=False).all()
        total_students = len(students)
        
        print(f"Found {total_students} students to process.")
        
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for i, student in enumerate(students):
            # Log progress every 10 students
            if i % 10 == 0:
                print(f"Processing... {i}/{total_students}")
                
            # Basic validation check
            if not student.joining_academic_year or not student.current_academic_year or not student.seat_type:
                # print(f"   ⚠ Skipping {student.name} (Missing required fields)")
                skip_count += 1
                continue
                
            # Call the assignment helper
            result = assign_fee_to_student(student.student_id)
            
            if result['success']:
                success_count += 1
            else:
                print(f"   ✗ Error for {student.name}: {result['error']}")
                error_count += 1
        
        print("\n" + "="*70)
        print("PROCESS COMPLETE")
        print("="*70)
        print(f"Total Students:    {total_students}")
        print(f"Successfully Set:  {success_count}")
        print(f"Skipped (Missing): {skip_count}")
        print(f"Errors:            {error_count}")
        print("="*70 + "\n")

if __name__ == "__main__":
    bulk_assign_fees()
