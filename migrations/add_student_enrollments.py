"""
Add Student Enrollment System
------------------------------
1. Create student_enrollments table
2. Add carries_section column to subjects
3. Optionally auto-create enrollments for existing students based on their program/semester match with subjects

Usage:
    python migrations/add_student_enrollments.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Student, Subject, StudentEnrollment
from datetime import datetime

def run_migration():
    """Run the migration"""
    with app.app_context():
        print("=" * 60)
        print("Student Enrollment System Migration")
        print("=" * 60)
        
        # Step 1: Add carries_section column to subjects table
        print("\n[1/3] Adding carries_section column to subjects table...")
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    "ALTER TABLE subjects ADD COLUMN carries_section BOOLEAN DEFAULT 1"
                ))
                conn.commit()
            print("✓ Added carries_section column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✓ Column already exists, skipping...")
            else:
                print(f"✗ Error adding column: {e}")
                return
        
        # Step 2: Create student_enrollments table
        print("\n[2/3] Creating student_enrollments table...")
        try:
            db.create_all()
            print("✓ Created student_enrollments table")
        except Exception as e:
            print(f"✗ Error creating table: {e}")
            return
        
        # Step 3: Optional - Create enrollments for existing students
        print("\n[3/3] Creating enrollments for existing students...")
        create_enrollments = input("Auto-create core subject enrollments? (y/n): ").strip().lower()
        
        if create_enrollments == 'y':
            try:
                # Get all active students
                students = Student.query.filter_by(
                    status='active',
                    is_deleted=False
                ).all()
                
                # Get all core subjects (non-elective)
                core_subjects = Subject.query.filter_by(
                    is_specialization=False,
                    is_deleted=False
                ).all()
                
                enrolled_count = 0
                for student in students:
                    # Find subjects matching student's program and current semester
                    matching_subjects = [
                        s for s in core_subjects
                        if s.program_id == student.program_id
                        and s.semester_id == student.current_semester
                    ]
                    
                    for subject in matching_subjects:
                        # Check if enrollment already exists
                        existing = StudentEnrollment.query.filter_by(
                            student_id=student.student_id,
                            subject_id=subject.subject_id,
                            is_deleted=False
                        ).first()
                        
                        if not existing:
                            enrollment = StudentEnrollment(
                                student_id=student.student_id,
                                subject_id=subject.subject_id,
                                section_id=student.section_id,
                                enrollment_type='core',
                                enrollment_status='active',
                                semester_enrolled=student.current_semester,
                                academic_year=get_academic_year()
                            )
                            db.session.add(enrollment)
                            enrolled_count += 1
                
                db.session.commit()
                print(f"✓ Created {enrolled_count} enrollments")
                
            except Exception as e:
                print(f"✗ Error creating enrollments: {e}")
                db.session.rollback()
        else:
            print("⊘ Skipped enrollment creation")
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Manually assign elective subjects to students via admin panel")
        print("3. Configure which subjects carry sections (default: all)")

def get_academic_year():
    """Get current academic year in format YYYY-YY"""
    now = datetime.now()
    if now.month >= 6:  # June onwards is new academic year
        return f"{now.year}-{str(now.year + 1)[-2:]}"
    else:
        return f"{now.year - 1}-{str(now.year)[-2:]}"

if __name__ == "__main__":
    run_migration()
