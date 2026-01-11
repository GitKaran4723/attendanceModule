"""
Assign fees to students who don't have fee structures
This script finds students without fee structures and creates them based on templates
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Student, FeeTemplate, FeeStructure
import uuid

def assign_missing_fees():
    """Assign fees to students who don't have fee structures"""
    
    print("\n" + "="*70)
    print("ASSIGN MISSING FEE STRUCTURES")
    print("="*70)
    
    with app.app_context():
        # Get all students
        students = Student.query.filter_by(is_deleted=False).all()
        
        print(f"\nFound {len(students)} active students")
        
        assigned_count = 0
        skipped_count = 0
        
        for student in students:
            # Check if student already has fee structure
            existing = FeeStructure.query.filter_by(
                student_id=student.student_id,
                is_deleted=False
            ).first()
            
            if existing:
                print(f"  ✓ {student.roll_number} - Already has fees")
                skipped_count += 1
                continue
            
            # Find matching template
            template = FeeTemplate.query.filter_by(
                academic_year=student.joining_academic_year,
                batch_year=student.joining_academic_year,
                seat_type=student.seat_type,
                quota_type=student.quota_type,
                is_deleted=False
            ).first()
            
            if not template:
                print(f"  ✗ {student.roll_number} - No matching template found")
                print(f"    Looking for: {student.joining_academic_year}, {student.seat_type}, {student.quota_type}")
                continue
            
            # Create fee structure
            fee_structure = FeeStructure(
                fee_structure_id=str(uuid.uuid4()),
                student_id=student.student_id,
                academic_year=student.joining_academic_year,
                base_fees=template.base_fees,
                total_fees=template.base_fees,
                additional_fees=None,
                fee_template_id=template.fee_template_id
            )
            
            db.session.add(fee_structure)
            assigned_count += 1
            print(f"  ✓ {student.roll_number} - Assigned ₹{template.base_fees}")
        
        # Commit all changes
        if assigned_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully assigned fees to {assigned_count} students")
        else:
            print(f"\n✓ No new fee assignments needed")
        
        print(f"  - Already had fees: {skipped_count}")
        print("="*70)

if __name__ == "__main__":
    assign_missing_fees()
