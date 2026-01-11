"""
Fee Management Permission Module
==================================
Handles permission checking for fee structure and receipt operations.
"""

from models import Student, Section, User


def can_set_fee_structure(student, current_user):
    """
    Check if current user can set fee structure for a student.
    
    Args:
        student: Student model instance
        current_user: User model instance
    
    Returns:
        bool: True if user has permission
    """
    if not current_user or not current_user.role:
        return False
    
    role = current_user.role.role_name
    
    # Admin can set for any student
    if role == 'admin':
        return True
    
    # Faculty can set for students in their sections (class teacher)
    if role == 'faculty':
        return is_class_teacher_of_student(current_user.faculty.faculty_id, student.student_id)
    
    return False


def can_edit_receipt(receipt, current_user):
    """
    Check if current user can edit a fee receipt.
    
    Students: Cannot edit once entered
    Class Teachers: Can edit any receipt (even approved) for students in their sections
    Admin: Can edit any receipt
    
    Args:
        receipt: FeeReceipt model instance
        current_user: User model instance
    
    Returns:
        bool: True if user has permission
    """
    if not current_user or not current_user.role:
        return False
    
    role = current_user.role.role_name
    
    # Admin can edit any receipt
    if role == 'admin':
        return True
    
    # Students cannot edit after entry
    if role == 'student':
        return False
    
    # Faculty can edit receipts for their section students (even if approved)
    if role == 'faculty':
        return is_class_teacher_of_student(current_user.faculty.faculty_id, receipt.student_id)
    
    return False


def can_approve_receipt(receipt, current_user):
    """
    Check if current user can approve a fee receipt.
    
    Only class teachers (for their section) and admin can approve.
    
    Args:
        receipt: FeeReceipt model instance
        current_user: User model instance
    
    Returns:
        bool: True if user has permission
    """
    if not current_user or not current_user.role:
        return False
    
    role = current_user.role.role_name
    
    # Admin can approve any receipt
    if role == 'admin':
        return True
    
    # Faculty can approve for their section students
    if role == 'faculty':
        return is_class_teacher_of_student(current_user.faculty.faculty_id, receipt.student_id)
    
    return False


def can_delete_receipt(receipt, current_user):
    """
    Check if current user can delete a fee receipt.
    
    Students: Cannot delete
    Class Teachers: Can delete receipts for students in their sections (even if approved)
    Admin: Can delete any receipt
    
    Args:
        receipt: FeeReceipt model instance
        current_user: User model instance
    
    Returns:
        bool: True if user has permission
    """
    if not current_user or not current_user.role:
        return False
    
    role = current_user.role.role_name
    
    # Admin can delete any receipt
    if role == 'admin':
        return True
    
    # Students cannot delete
    if role == 'student':
        return False
    
    # Faculty can delete receipts for their section students
    if role == 'faculty':
        return is_class_teacher_of_student(current_user.faculty.faculty_id, receipt.student_id)
    
    return False


def can_view_student_fees(student_id, current_user):
    """
    Check if current user can view fee details for a student.
    
    Args:
        student_id: Student ID
        current_user: User model instance
    
    Returns:
        bool: True if user has permission
    """
    if not current_user or not current_user.role:
        return False
    
    role = current_user.role.role_name
    
    # Admin can view any student's fees
    if role == 'admin':
        return True
    
    # Students can view their own fees
    if role == 'student':
        if current_user.student:
            return current_user.student.student_id == student_id
        return False
    
    # Parents can view fees (same logic as students for now)
    if role == 'parent':
        # Assuming parent is logged in with student credentials
        if current_user.student:
            return current_user.student.student_id == student_id
        return False
    
    # Faculty can view fees for students in their sections
    if role == 'faculty':
        return is_class_teacher_of_student(current_user.faculty.faculty_id, student_id)
    
    return False


def get_class_teacher_students(faculty_id):
    """
    Get list of student IDs for students in sections where faculty is class teacher.
    
    Args:
        faculty_id: Faculty ID
    
    Returns:
        list: List of student IDs
    """
    sections = Section.query.filter_by(class_teacher_id=faculty_id, is_deleted=False).all()
    student_ids = []
    
    for section in sections:
        students = section.students.filter_by(is_deleted=False).all()
        student_ids.extend([s.student_id for s in students])
    
    return student_ids


def is_class_teacher_of_student(faculty_id, student_id):
    """
    Check if faculty is class teacher of student's section.
    
    Args:
        faculty_id: Faculty ID
        student_id: Student ID
    
    Returns:
        bool: True if faculty is student's class teacher
    """
    student = Student.query.get(student_id)
    
    if student and student.section and not student.is_deleted:
        return student.section.class_teacher_id == faculty_id
    
    return False


def get_student_section(student_id):
    """
    Get the section details for a student.
    
    Args:
        student_id: Student ID
    
    Returns:
        Section object or None
    """
    student = Student.query.get(student_id)
    if student and not student.is_deleted:
        return student.section
    return None


def get_class_teacher_sections(faculty_id):
    """
    Get list of sections where faculty is class teacher.
    
    Args:
        faculty_id: Faculty ID
    
    Returns:
        list: List of Section objects
    """
    return Section.query.filter_by(class_teacher_id=faculty_id, is_deleted=False).all()
