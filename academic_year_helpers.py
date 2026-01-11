"""
Helper functions for academic year management
Auto-sync academic years from programs to students/faculty
"""

from models import db, Student, Faculty, Program, SystemSettings
from datetime import datetime

def sync_student_academic_years():
    """
    Sync academic years from programs to students
    Updates all students to match their program's current academic year
    """
    students = Student.query.filter_by(is_deleted=False).all()
    updated_count = 0
    
    for student in students:
        if student.program_id and student.program:
            # Set student's academic year to match their program
            if student.current_academic_year != student.program.current_academic_year:
                student.current_academic_year = student.program.current_academic_year
                updated_count += 1
    
    if updated_count > 0:
        db.session.commit()
    
    return updated_count

def sync_faculty_academic_years():
    """
    Sync academic years from programs to faculty
    Updates all faculty to match their program's current academic year
    """
    faculties = Faculty.query.filter_by(is_deleted=False).all()
    updated_count = 0
    
    current_year = datetime.now().year
    default_year = f"{current_year}-{current_year + 1}"
    
    for faculty in faculties:
        if faculty.program_id and faculty.program:
            # Set faculty's academic year to match their program
            if faculty.current_academic_year != faculty.program.current_academic_year:
                faculty.current_academic_year = faculty.program.current_academic_year
                updated_count += 1
        elif not faculty.current_academic_year:
            # Set default for faculty without programs
            faculty.current_academic_year = default_year
            updated_count += 1
    
    if updated_count > 0:
        db.session.commit()
    
    return updated_count

def get_current_academic_year(program_id=None):
    """
    Get current academic year for a program or system-wide default
    
    Args:
        program_id: Optional program ID to get specific program's year
        
    Returns:
        str: Academic year in format "YYYY-YYYY"
    """
    if program_id:
        program = Program.query.get(program_id)
        if program and program.current_academic_year:
            return program.current_academic_year
    
    # Default to current year
    current_year = datetime.now().year
    return f"{current_year}-{current_year + 1}"

def update_program_academic_year(program_id, academic_year):
    """
    Update program's academic year and sync to all students/faculty
    
    Args:
        program_id: Program ID to update
        academic_year: New academic year (e.g., "2024-2025")
        
    Returns:
        dict: Summary of updates
    """
    program = Program.query.get(program_id)
    if not program:
        return {'success': False, 'error': 'Program not found'}
    
    # Update program
    program.current_academic_year = academic_year
    
    # Update all students in this program
    students = Student.query.filter_by(
        program_id=program_id,
        is_deleted=False
    ).all()
    
    for student in students:
        student.current_academic_year = academic_year
    
    # Update all faculty in this program
    faculties = Faculty.query.filter_by(
        program_id=program_id,
        is_deleted=False
    ).all()
    
    for faculty in faculties:
        faculty.current_academic_year = academic_year
    
    db.session.commit()
    
    return {
        'success': True,
        'program': program.program_name,
        'academic_year': academic_year,
        'students_updated': len(students),
        'faculty_updated': len(faculties)
    }
