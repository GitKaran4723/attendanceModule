"""
Database Models for BCA BUB Attendance System
==============================================
This module contains all database models using SQLAlchemy ORM.
The models are organized into:
- Core models (User, Role, Faculty, Student, Program, Section)
- Academic models (Semester, Subject, SubjectAllocation, ClassSchedule)
- Attendance models (AttendanceSession, AttendanceRecord)
- Assessment models (Test, TestResult)
"""

import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, UniqueConstraint

db = SQLAlchemy()


def gen_uuid():
    """Generate a UUID string for primary keys"""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------
# Mixins - Reusable model components
# ---------------------------------------------------------------------
class TimestampMixin:
    """
    Adds created_at and updated_at timestamp fields to models.
    These are automatically managed by SQLAlchemy.
    """
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SoftDeleteMixin:
    """
    Adds soft delete capability to models.
    Records are marked as deleted rather than being physically removed.
    """
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)


# ---------------------------------------------------------------------
# Core Models - User Management & Authentication
# ---------------------------------------------------------------------
class Role(db.Model, TimestampMixin):
    """
    Defines user roles (e.g., Admin, Faculty, Student, HOD)
    """
    __tablename__ = "roles"

    role_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    role_name = db.Column(db.String(64), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)

    # Relationships
    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def to_dict(self):
        """Convert role object to dictionary for JSON responses"""
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Role {self.role_name}>"


class User(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Core user model for authentication and authorization.
    Linked to Faculty or Student based on role.
    """
    __tablename__ = "users"

    user_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    username = db.Column(db.String(128), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey("roles.role_id"), nullable=False)

    # Account status fields
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime)

    # Relationships
    role = db.relationship("Role", back_populates="users")
    faculty = db.relationship("Faculty", back_populates="user", uselist=False)
    student = db.relationship("Student", back_populates="user", uselist=False)

    def to_dict(self):
        """Convert user object to dictionary for JSON responses"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role.role_name if self.role else None,
            'is_active': self.is_active,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User {self.username}>"


class Faculty(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Faculty/Teacher information and profile.
    Linked to User for authentication.
    """
    __tablename__ = "faculties"

    faculty_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    
    # New detailed fields
    employee_id = db.Column(db.String(50), unique=True, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=True, index=True)
    qualification = db.Column(db.String(200))
    
    # Legacy field for backward compatibility
    name = db.Column(db.String(200), nullable=True)
    
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    employment_type = db.Column(db.Enum("full_time", "part_time", name="employment_type_enum"), nullable=True)
    join_date = db.Column(db.Date)
    designation = db.Column(db.String(128))
    workload_hours_per_week = db.Column(db.Integer, default=0)  # Teaching hours per week
    is_hod = db.Column(db.Boolean, nullable=False, default=False)  # Legacy field for backward compatibility
    is_coordinator = db.Column(db.Boolean, nullable=False, default=False)  # Program coordinator status
    status = db.Column(db.String(32), default="active")
    current_academic_year = db.Column(db.String(20))  # e.g., "2024-2025" - current year for reports

    # Relationships
    user = db.relationship("User", back_populates="faculty")
    program = db.relationship("Program")
    allocations = db.relationship("SubjectAllocation", back_populates="faculty", lazy="dynamic")
    schedules = db.relationship("ClassSchedule", back_populates="faculty", lazy="dynamic")
    tests = db.relationship("Test", back_populates="faculty", lazy="dynamic")

    def to_dict(self):
        """Convert faculty object to dictionary for JSON responses"""
        return {
            'faculty_id': self.faculty_id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'name': self.name or f"{self.first_name} {self.last_name}",  # Backward compatibility
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'program_id': self.program_id,
            'program': self.program.program_name if self.program else None,
            'qualification': self.qualification,
            'designation': self.designation,
            'employment_type': self.employment_type,
            'is_hod': self.is_hod,
            'is_coordinator': self.is_coordinator,
            'status': self.status,
            'join_date': self.join_date.isoformat() if self.join_date else None
        }

    def __repr__(self):
        return f"<Faculty {self.first_name} {self.last_name}>"


# ---------------------------------------------------------------------
# Program Coordinator Association Table
# ---------------------------------------------------------------------
class ProgramCoordinator(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Association table for many-to-many relationship between Faculty and Program.
    A faculty can be coordinator of multiple programs, and a program can have multiple coordinators.
    """
    __tablename__ = "program_coordinators"
    
    assignment_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    faculty_id = db.Column(db.String(36), db.ForeignKey("faculties.faculty_id"), nullable=False, index=True)
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=False, index=True)
    assigned_by = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=True)  # Admin who assigned
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    faculty = db.relationship("Faculty", backref=db.backref("coordinator_assignments", lazy="dynamic", cascade="all, delete-orphan"))
    program = db.relationship("Program", backref=db.backref("coordinator_assignments", lazy="dynamic", cascade="all, delete-orphan"))
    assigned_by_user = db.relationship("User", foreign_keys=[assigned_by])
    
    __table_args__ = (
        UniqueConstraint("faculty_id", "program_id", "is_deleted", name="uix_faculty_program_coordinator"),
    )
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'assignment_id': self.assignment_id,
            'faculty_id': self.faculty_id,
            'faculty_name': f"{self.faculty.first_name} {self.faculty.last_name}" if self.faculty else None,
            'program_id': self.program_id,
            'program_name': self.program.program_name if self.program else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'assigned_by': self.assigned_by_user.username if self.assigned_by_user else None
        }
    
    def __repr__(self):
        return f"<ProgramCoordinator {self.faculty_id} -> {self.program_id}>"


class Program(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Academic programs (e.g., BCA, MCA, B.Sc Computer Science)
    """
    __tablename__ = "programs"

    program_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    program_code = db.Column(db.String(50), unique=True, index=True)
    program_name = db.Column(db.String(150), nullable=False)
    
    # Legacy field for backward compatibility
    name = db.Column(db.String(150), nullable=True)
    
    duration = db.Column(db.Integer)  # duration in years/semesters
    duration_years = db.Column(db.Integer)  # For templates
    
    # Academic year tracking (per program)
    current_academic_year = db.Column(db.String(20))  # e.g., "2024-2025"

    # Relationships
    sections = db.relationship("Section", back_populates="program", lazy="dynamic")

    def to_dict(self):
        """Convert program object to dictionary for JSON responses"""
        return {
            'program_id': self.program_id,
            'program_code': self.program_code,
            'program_name': self.program_name,
            'name': self.program_name or self.name,  # Backward compatibility
            'duration': self.duration,
            'duration_years': self.duration_years or self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Program {self.program_name or self.name}>"


class Section(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Class sections within a program (e.g., BCA 3rd Year Section A)
    """
    __tablename__ = "sections"

    section_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    section_name = db.Column(db.String(64), nullable=False)
    
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=False, index=True)
    year_of_study = db.Column(db.Integer)
    academic_year = db.Column(db.String(20))  # e.g., "2024-2025"
    current_semester = db.Column(db.Integer)  # Which semester they're in
    
    # Elective Support (Virtual Sections)
    is_elective = db.Column(db.Boolean, default=False)
    linked_subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=True)
    
    # Class Teacher - Faculty assigned as class teacher for this section
    class_teacher_id = db.Column(db.String(36), db.ForeignKey("faculties.faculty_id"), nullable=True, index=True)

    # Relationships
    program = db.relationship("Program", back_populates="sections")
    class_teacher = db.relationship("Faculty", foreign_keys=[class_teacher_id], backref="class_teacher_sections")
    linked_subject = db.relationship("Subject", foreign_keys=[linked_subject_id])
    students = db.relationship("Student", back_populates="section", lazy="dynamic")
    allocations = db.relationship("SubjectAllocation", back_populates="section", lazy="dynamic")
    schedules = db.relationship("ClassSchedule", back_populates="section", lazy="dynamic")
    tests = db.relationship("Test", back_populates="section", lazy="dynamic")

    __table_args__ = (
        UniqueConstraint("section_name", "program_id", "current_semester", "academic_year", name="uix_section_program_semester"),
    )

    def get_students(self):
        """
        Get all students for this section.
        For virtual sections (linked to a subject), fetch students from StudentSubjectEnrollment.
        For regular sections, fetch students directly by section_id.
        """
        from models import StudentSubjectEnrollment
        
        if self.is_elective and self.linked_subject_id:
            # Virtual section - get students enrolled in the linked subject
            enrollments = StudentSubjectEnrollment.query.filter_by(
                subject_id=self.linked_subject_id,
                is_deleted=False
            ).all()
            return [enrollment.student for enrollment in enrollments if enrollment.student and not enrollment.student.is_deleted]
        else:
            # Regular section - get students directly
            return self.students.filter_by(is_deleted=False).all()

    def to_dict(self):
        """Convert section object to dictionary for JSON responses"""
        return {
            'section_id': self.section_id,
            'name': self.section_name,  # For backward compatibility
            'section_name': self.section_name,
            'program_id': self.program_id,
            'program_name': self.program.name if self.program else None,
            'year_of_study': self.year_of_study,
            'academic_year': self.academic_year,
            'current_semester': self.current_semester,
            'class_teacher_id': self.class_teacher_id,
            'class_teacher_name': f"{self.class_teacher.first_name} {self.class_teacher.last_name}" if self.class_teacher else None,
            'student_count': self.students.count()
        }

    def __repr__(self):
        return f"<Section {self.section_name}>"


class Student(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Student information and academic details.
    Linked to User for authentication.
    """
    __tablename__ = "students"

    student_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    
    # Student details
    roll_number = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(205), nullable=False) # Full name as in 10th marksheet
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    guardian_name = db.Column(db.String(200))
    guardian_phone = db.Column(db.String(20))
    usn = db.Column(db.String(64), nullable=True, index=True)  # University Seat Number
    
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=True)
    admission_year = db.Column(db.Integer)
    joining_academic_year = db.Column(db.String(20))  # e.g., "2023-2024" - for fee tracking
    current_academic_year = db.Column(db.String(20))  # e.g., "2024-2025" - current year for reports
    
    # Fee-related fields
    category = db.Column(db.String(20), nullable=True)  # 'CAT1', 'SC', 'ST', '2A', '2B', '3A', '3B', 'GENERAL', 'OTHER'
    seat_type = db.Column(db.String(20), nullable=True)  # 'GOVERNMENT', 'MANAGEMENT'
    quota_type = db.Column(db.String(20), nullable=True)  # 'MERIT', 'CATEGORY', NULL (for Management)
    
    current_semester = db.Column(db.Integer)  # Which semester (1-8)
    status = db.Column(db.String(32), default="active")
    gender = db.Column(db.String(10))  # M, F, or Other

    # Relationships
    user = db.relationship("User", back_populates="student")
    program = db.relationship("Program")
    section = db.relationship("Section", back_populates="students")
    attendance_records = db.relationship("AttendanceRecord", back_populates="student", lazy="dynamic", cascade="all, delete-orphan")
    test_results = db.relationship("TestResult", back_populates="student", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert student object to dictionary for JSON responses"""
        return {
            'student_id': self.student_id,
            'roll_number': self.roll_number,
            'usn': self.roll_number or self.usn,  # Backward compatibility
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'dob': self.date_of_birth.isoformat() if self.date_of_birth else None,  # Backward compatibility
            'address': self.address,
            'guardian_name': self.guardian_name,
            'guardian_phone': self.guardian_phone,
            'program': self.program.name if self.program else None,
            'section': self.section.name if self.section else None,
            'admission_year': self.admission_year,
            'current_semester': self.current_semester,
            'status': self.status
        }

    def __repr__(self):
        return f"<Student {self.roll_number or self.usn} - {self.name}>"


# ---------------------------------------------------------------------
# Academic Structure Models
# ---------------------------------------------------------------------
class Semester(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Academic semester/term information
    """
    __tablename__ = "semesters"

    semester_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(64), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    academic_year = db.Column(db.String(32))

    # Relationships
    schedules = db.relationship("ClassSchedule", back_populates="semester", lazy="dynamic")
    tests = db.relationship("Test", back_populates="semester", lazy="dynamic")

    def to_dict(self):
        """Convert semester object to dictionary for JSON responses"""
        return {
            'semester_id': self.semester_id,
            'name': self.name,
            'academic_year': self.academic_year,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

    def __repr__(self):
        return f"<Semester {self.name}>"


class Subject(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Subject/Course information
    """
    __tablename__ = "subjects"

    subject_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    subject_code = db.Column(db.String(64), nullable=False, index=True)  # Updated from 'code'
    subject_name = db.Column(db.String(255), nullable=False)
    credits = db.Column(db.Float, default=0)  # Changed to Float for decimal credits
    subject_type = db.Column(db.String(64))  # Theory, Practical, Project, etc
    
    # Elective Support
    subject_category = db.Column(db.Enum('compulsory', 'language', 'specialization', 'elective', name='subject_category_enum'), default='compulsory')
    elective_group = db.Column(db.String(100)) # e.g., "Language II", "Specialization I" - for grouping options
    
    # Academic details
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=True, index=True)
    semester_id = db.Column(db.Integer, nullable=True)  # Which semester (1-8)
    description = db.Column(db.Text)
    total_hours = db.Column(db.Integer)  # Total teaching hours
    is_specialization = db.Column(db.Boolean, default=False)  # True for elective/specialization subjects
    carries_section = db.Column(db.Boolean, default=True)  # Does this subject have section-based attendance?

    # Legacy field for backward compatibility
    code = db.Column(db.String(64), nullable=True)  # Old field kept for compatibility
    type = db.Column(db.Enum("theory", "practical", "mixed", name="subject_type_enum"), 
                     nullable=True, default="theory")

    # Relationships
    program = db.relationship("Program", backref=db.backref("subjects", lazy="dynamic"))
    allocations = db.relationship("SubjectAllocation", back_populates="subject", lazy="dynamic")
    schedules = db.relationship("ClassSchedule", back_populates="subject", lazy="dynamic")
    tests = db.relationship("Test", back_populates="subject", lazy="dynamic")

    __table_args__ = (
        UniqueConstraint("subject_code", name="uix_subject_code"),
    )

    def to_dict(self):
        """Convert subject object to dictionary for JSON responses"""
        return {
            'subject_id': self.subject_id,
            'subject_code': self.subject_code,
            'code': self.subject_code,  # For backward compatibility
            'subject_name': self.subject_name,
            'credits': self.credits,
            'subject_type': self.subject_type,
            'type': self.type,  # For backward compatibility
            'semester_id': self.semester_id,
            'program_id': self.program_id,
            'description': self.description,
            'total_hours': self.total_hours,
            'carries_section': self.carries_section
        }

    def __repr__(self):
        return f"<Subject {self.code} - {self.subject_name}>"


class Unit(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Units within a subject (e.g., Unit 1, Unit 2)
    """
    __tablename__ = "units"

    unit_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False, index=True)
    unit_number = db.Column(db.Integer, nullable=False)
    unit_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    subject = db.relationship("Subject", backref=db.backref("units", lazy="dynamic", cascade="all, delete-orphan"))
    chapters = db.relationship("Chapter", back_populates="unit", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("subject_id", "unit_number", name="uix_subject_unit"),
    )

    def to_dict(self):
        """Convert unit object to dictionary for JSON responses"""
        return {
            'unit_id': self.unit_id,
            'subject_id': self.subject_id,
            'unit_number': self.unit_number,
            'unit_name': self.unit_name,
            'description': self.description,
            'chapters': [chapter.to_dict() for chapter in self.chapters] if self.chapters else []
        }

    def __repr__(self):
        return f"<Unit {self.unit_number}: {self.unit_name}>"


class Chapter(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Chapters within a unit
    """
    __tablename__ = "chapters"

    chapter_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    unit_id = db.Column(db.String(36), db.ForeignKey("units.unit_id"), nullable=False, index=True)
    chapter_number = db.Column(db.Float, nullable=False)
    chapter_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    unit = db.relationship("Unit", back_populates="chapters")
    concepts = db.relationship("Concept", back_populates="chapter", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("unit_id", "chapter_number", name="uix_unit_chapter"),
    )

    def to_dict(self):
        """Convert chapter object to dictionary for JSON responses"""
        return {
            'chapter_id': self.chapter_id,
            'unit_id': self.unit_id,
            'chapter_number': self.chapter_number,
            'chapter_name': self.chapter_name,
            'description': self.description,
            'concepts': [concept.to_dict() for concept in self.concepts] if self.concepts else []
        }

    def __repr__(self):
        return f"<Chapter {self.chapter_number}: {self.chapter_name}>"


class Concept(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Concepts within a chapter (smallest unit of curriculum)
    """
    __tablename__ = "concepts"

    concept_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    chapter_id = db.Column(db.String(36), db.ForeignKey("chapters.chapter_id"), nullable=False, index=True)
    concept_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    chapter = db.relationship("Chapter", back_populates="concepts")

    def to_dict(self):
        """Convert concept object to dictionary for JSON responses"""
        return {
            'concept_id': self.concept_id,
            'chapter_id': self.chapter_id,
            'concept_name': self.concept_name,
            'description': self.description
        }

    def __repr__(self):
        return f"<Concept {self.concept_name}>"


class SubjectAllocation(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Allocation of subjects to faculty for specific sections
    """
    __tablename__ = "subject_allocations"

    allocation_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False, index=True)
    faculty_id = db.Column(db.String(36), db.ForeignKey("faculties.faculty_id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=True, index=True)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.semester_id"), nullable=True)
    allocation_type = db.Column(db.String(64))  # e.g. "primary", "co-teacher"

    # Relationships
    subject = db.relationship("Subject", back_populates="allocations")
    faculty = db.relationship("Faculty", back_populates="allocations")
    section = db.relationship("Section", back_populates="allocations")
    semester = db.relationship("Semester")

    __table_args__ = (
        UniqueConstraint("subject_id", "faculty_id", "section_id", name="uix_sub_fac_sec"),
    )

    def to_dict(self):
        """Convert allocation object to dictionary for JSON responses"""
        return {
            'allocation_id': self.allocation_id,
            'subject': self.subject.subject_name if self.subject else None,
            'subject_code': self.subject.code if self.subject else None,
            'faculty': self.faculty.name if self.faculty else None,
            'section': self.section.name if self.section else None,
            'allocation_type': self.allocation_type
        }

    def __repr__(self):
        return f"<Allocation {self.subject_id} -> {self.faculty_id}>"


class ClassSchedule(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Class schedule/timetable entries - represents a scheduled class session.
    Can be either:
    1. Permanent schedule: Pre-planned timetable entries
    2. Temporary schedule: Created during ad-hoc attendance taking
    
    IMPORTANT: start_time and end_time are used to calculate teaching hours for faculty dashboard.
    """
    __tablename__ = "class_schedules"

    schedule_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)  # Unique identifier for this schedule
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False)  # Which subject is being taught
    faculty_id = db.Column(db.String(36), db.ForeignKey("faculties.faculty_id"), nullable=False)  # Which faculty is teaching
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=False)  # Which section is attending
    room_id = db.Column(db.String(64))  # Optional: Room/location where class is held
    date = db.Column(db.Date, nullable=False, index=True)  # Date of the class (REQUIRED for tracking)
    start_time = db.Column(db.Time)  # Class start time (CRITICAL: Used for duration calculation)
    end_time = db.Column(db.Time)  # Class end time (CRITICAL: Used for duration calculation)
    class_type = db.Column(db.String(16))  # Type of class: theory/practical/lab
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.semester_id"), nullable=True)  # Optional: Academic semester reference

    # Relationships
    subject = db.relationship("Subject", back_populates="schedules")
    faculty = db.relationship("Faculty", back_populates="schedules")
    section = db.relationship("Section", back_populates="schedules")
    semester = db.relationship("Semester", back_populates="schedules")
    attendance_sessions = db.relationship("AttendanceSession", back_populates="schedule", lazy="dynamic")

    __table_args__ = (
        Index("ix_schedule_section_date", "section_id", "date"),
    )

    def to_dict(self):
        """Convert schedule object to dictionary for JSON responses"""
        return {
            'schedule_id': self.schedule_id,
            'subject': self.subject.subject_name if self.subject else None,
            'subject_code': self.subject.code if self.subject else None,
            'faculty': self.faculty.name if self.faculty else None,
            'section': self.section.name if self.section else None,
            'room_id': self.room_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'class_type': self.class_type
        }

    def __repr__(self):
        return f"<Schedule {self.section_id} {self.subject_id} on {self.date}>"


# ---------------------------------------------------------------------
# Attendance Management Models
# ---------------------------------------------------------------------
class AttendanceSession(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    An attendance session represents one instance of taking attendance for a scheduled class.
    Multiple students will have AttendanceRecord entries under this session.
    
    RELATIONSHIP WITH SCHEDULE:
    - Every session MUST be linked to a ClassSchedule (schedule_id is NOT NULL)
    - The schedule provides: subject, section, faculty, date, start_time, end_time
    - Duration for teaching hours is calculated from schedule.start_time and schedule.end_time
    
    WORKFLOW:
    1. Faculty takes attendance → ClassSchedule is created/found
    2. AttendanceSession is created and linked to the schedule
    3. Individual student records (AttendanceRecord) are created under this session
    """
    __tablename__ = "attendance_sessions"

    attendance_session_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)  # Unique identifier for this attendance session
    schedule_id = db.Column(db.String(36), db.ForeignKey("class_schedules.schedule_id"), 
                           nullable=False, index=True)  # REQUIRED: Links to ClassSchedule (provides subject, section, times)
    taken_by_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)  # Faculty who took attendance
    taken_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # When attendance was recorded (timestamp)
    status = db.Column(db.Enum("draft", "finalized", name="attendance_status_enum"), 
                      nullable=False, default="draft")  # Status: draft (in-progress) or finalized (submitted)
    approved_by = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=True)  # Optional: Admin/HOD who approved
    approved_at = db.Column(db.DateTime)  # Optional: When attendance was approved
    topic_taught = db.Column(db.String(255))  # Optional: Topic/content covered in this class
    diary_number = db.Column(db.String(20), unique=True, index=True)  # Unique diary entry number (e.g., BCA-1, BCA-2)

    # Relationships
    schedule = db.relationship("ClassSchedule", back_populates="attendance_sessions")
    taken_by = db.relationship("User", foreign_keys=[taken_by_user_id])
    approved_user = db.relationship("User", foreign_keys=[approved_by])
    records = db.relationship("AttendanceRecord", back_populates="attendance_session", 
                            lazy="dynamic", cascade="all, delete-orphan")

    @staticmethod
    def generate_diary_number(program_code=None):
        """
        Generate unique diary number for attendance sessions per program.
        Format: PROGRAM-NUMBER (e.g., BCA-1, BCA-2, MCA-1, MCA-2)
        If no program_code provided, falls back to simple sequential number.
        
        Args:
            program_code: Program code (e.g., 'BCA', 'MCA')
        
        Returns:
            str: Unique diary number
        """
        if program_code:
            # Get the last attendance session diary number for this program
            last_session = AttendanceSession.query.filter(
                AttendanceSession.diary_number.like(f'{program_code}-%')
            ).order_by(
                AttendanceSession.created_at.desc()
            ).first()
            
            if last_session and last_session.diary_number:
                try:
                    # Extract number from diary_number (e.g., "BCA-5" -> 5)
                    last_num = int(last_session.diary_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    # If parsing fails, count all sessions for this program and add 1
                    new_num = AttendanceSession.query.filter(
                        AttendanceSession.diary_number.like(f'{program_code}-%')
                    ).count() + 1
            else:
                new_num = 1
            
            return f"{program_code}-{new_num}"
        else:
            # Fallback: global sequential number
            last_session = AttendanceSession.query.filter(
                AttendanceSession.diary_number.isnot(None)
            ).order_by(
                AttendanceSession.created_at.desc()
            ).first()
            
            if last_session and last_session.diary_number:
                try:
                    last_num = int(last_session.diary_number.split('-')[-1]) if '-' in last_session.diary_number else int(last_session.diary_number)
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = AttendanceSession.query.filter(AttendanceSession.diary_number.isnot(None)).count() + 1
            else:
                new_num = 1
            
            return str(new_num)

    def to_dict(self):
        """Convert attendance session object to dictionary for JSON responses"""
        return {
            'attendance_session_id': self.attendance_session_id,
            'schedule_id': self.schedule_id,
            'taken_by': self.taken_by.username if self.taken_by else None,
            'taken_at': self.taken_at.isoformat() if self.taken_at else None,
            'status': self.status,
            'total_records': self.records.count()
        }

    def __repr__(self):
        return f"<AttendanceSession {self.attendance_session_id} schedule={self.schedule_id}>"


class AttendanceRecord(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Individual student attendance record for a session
    """
    __tablename__ = "attendance_records"

    record_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    attendance_session_id = db.Column(db.String(36), 
                                     db.ForeignKey("attendance_sessions.attendance_session_id"), 
                                     nullable=False, index=True)
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), 
                          nullable=False, index=True)
    status = db.Column(db.Enum("present", "absent", "late", "excused", 
                              name="attendance_record_status_enum"), nullable=False)
    remarks = db.Column(db.String(400))

    # Relationships
    attendance_session = db.relationship("AttendanceSession", back_populates="records")
    student = db.relationship("Student", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint("attendance_session_id", "student_id", name="uix_session_student"),
        Index("ix_attendance_student_date", "student_id", "attendance_session_id"),
    )

    def to_dict(self):
        """Convert attendance record object to dictionary for JSON responses"""
        return {
            'record_id': self.record_id,
            'student_usn': self.student.usn if self.student else None,
            'student_name': self.student.name if self.student else None,
            'status': self.status,
            'remarks': self.remarks
        }

    def __repr__(self):
        return f"<AttendanceRecord student={self.student_id} status={self.status}>"


# ---------------------------------------------------------------------
# Assessment/Test Management Models
# ---------------------------------------------------------------------
class Test(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Test/Exam information
    """
    __tablename__ = "tests"

    test_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    test_name = db.Column(db.String(255), nullable=False)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False)
    faculty_id = db.Column(db.String(36), db.ForeignKey("faculties.faculty_id"), nullable=False)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=False)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.semester_id"), nullable=True)
    test_date = db.Column(db.Date)
    max_marks = db.Column(db.Float)
    
    # Internal Marks System fields
    component_type = db.Column(db.Enum('test', 'assignment', 'project', 'quiz', 'presentation', 'other', 
                                       name='component_type_enum'), nullable=False, default='test')
    weightage = db.Column(db.Float, nullable=True)  # Percentage contribution to final marks
    description = db.Column(db.Text, nullable=True)  # Detailed description
    is_published = db.Column(db.Boolean, nullable=False, default=False)  # Visibility to students

    # Relationships
    subject = db.relationship("Subject", back_populates="tests")
    faculty = db.relationship("Faculty", back_populates="tests")
    section = db.relationship("Section", back_populates="tests")
    semester = db.relationship("Semester", back_populates="tests")
    results = db.relationship("TestResult", back_populates="test", lazy="dynamic", 
                            cascade="all, delete-orphan")

    def to_dict(self):
        """Convert test object to dictionary for JSON responses"""
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'subject': self.subject.subject_name if self.subject else None,
            'subject_code': self.subject.code if self.subject else None,
            'subject_id': self.subject_id,
            'faculty': self.faculty.name if self.faculty else None,
            'section': self.section.section_name if self.section else None,
            'section_id': self.section_id,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'max_marks': self.max_marks,
            'component_type': self.component_type,
            'weightage': self.weightage,
            'description': self.description,
            'is_published': self.is_published,
            'total_students': self.results.count(),
            'marked_students': self.results.filter(TestResult.marks_obtained.isnot(None)).count()
        }

    def __repr__(self):
        return f"<Test {self.test_name} - {self.subject_id}>"


class TestResult(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Individual student test results
    """
    __tablename__ = "test_results"

    result_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    test_id = db.Column(db.String(36), db.ForeignKey("tests.test_id"), nullable=False, index=True)
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), nullable=False, index=True)
    marks_obtained = db.Column(db.Float)
    remarks = db.Column(db.String(400))

    # Relationships
    test = db.relationship("Test", back_populates="results")
    student = db.relationship("Student", back_populates="test_results")

    __table_args__ = (
        UniqueConstraint("test_id", "student_id", name="uix_test_student"),
    )

    def to_dict(self):
        """Convert test result object to dictionary for JSON responses"""
        return {
            'result_id': self.result_id,
            'test_name': self.test.test_name if self.test else None,
            'student_usn': self.student.usn if self.student else None,
            'student_name': self.student.name if self.student else None,
            'marks_obtained': self.marks_obtained,
            'max_marks': self.test.max_marks if self.test else None,
            'remarks': self.remarks
        }

    def __repr__(self):
        return f"<TestResult test={self.test_id} student={self.student_id}>"


# ---------------------------------------------------------------------
# Work Diary System - Faculty Activity Tracking
# ---------------------------------------------------------------------
class WorkDiary(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Faculty work diary entries - automatically generated from attendance sessions
    or manually entered for special activities like invigilation, meetings, etc.
    
    Each diary entry represents a work activity with auto-generated diary number.
    """
    __tablename__ = "work_diaries"

    diary_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    diary_number = db.Column(db.String(64), unique=True, nullable=False, index=True)  # Auto-generated: WD-2025-0001
    
    # Faculty information
    faculty_id = db.Column(db.String(36), db.ForeignKey("faculties.faculty_id"), nullable=False, index=True)
    
    # Academic context
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=True)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.semester_id"), nullable=True)
    academic_year = db.Column(db.String(32))  # e.g., "2024-2025"
    
    # Activity details
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_hours = db.Column(db.Float)  # Calculated: end_time - start_time in hours
    
    # Activity type and details
    activity_type = db.Column(
        db.Enum("theory_class", "practical_class", "tutorial", "invigilation", 
                "meeting", "seminar", "workshop", "exam_duty", "other", 
                name="work_activity_type_enum"), 
        nullable=False
    )
    
    # Class-specific information (for regular classes)
    attendance_session_id = db.Column(db.String(36), 
                                      db.ForeignKey("attendance_sessions.attendance_session_id"), 
                                      nullable=True, index=True)
    students_present = db.Column(db.Integer, default=0)  # From attendance if linked
    total_students = db.Column(db.Integer, default=0)    # Section strength
    
    # Non-class activity details (invigilation, meetings, etc.)
    activity_title = db.Column(db.String(255))  # e.g., "Mid-term Exam Invigilation", "Department Meeting"
    activity_description = db.Column(db.Text)    # Detailed description
    location = db.Column(db.String(128))         # Room/venue
    
    # Topics covered (for classes)
    topics_covered = db.Column(db.Text)          # What was taught/discussed
    
    # Status and approval
    status = db.Column(
        db.Enum("draft", "submitted", "approved", "rejected", name="diary_status_enum"),
        nullable=False, default="draft"
    )
    submitted_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=True)
    approved_at = db.Column(db.DateTime)
    approval_remarks = db.Column(db.Text)
    
    # Attachments/evidence (optional)
    attachment_url = db.Column(db.String(500))  # Path to uploaded file if any
    
    # Relationships
    faculty = db.relationship("Faculty", backref="work_diaries")
    subject = db.relationship("Subject")
    section = db.relationship("Section")
    semester = db.relationship("Semester")
    attendance_session = db.relationship("AttendanceSession")
    approved_user = db.relationship("User", foreign_keys=[approved_by])

    def calculate_duration(self):
        """Calculate duration in hours from start_time to end_time"""
        if self.start_time and self.end_time:
            start = datetime.combine(datetime.today(), self.start_time)
            end = datetime.combine(datetime.today(), self.end_time)
            duration = (end - start).total_seconds() / 3600
            self.duration_hours = round(duration, 2)

    @staticmethod
    def generate_diary_number(year=None):
        """
        Generate unique diary number as simple sequential number: 1, 2, 3, etc.
        """
        # Get the last diary number overall
        last_diary = WorkDiary.query.order_by(
            WorkDiary.created_at.desc()
        ).first()
        
        if last_diary and last_diary.diary_number:
            try:
                # Try to extract number from diary_number
                last_num = int(last_diary.diary_number.split('-')[-1]) if '-' in last_diary.diary_number else int(last_diary.diary_number)
                new_num = last_num + 1
            except (ValueError, IndexError):
                # If parsing fails, count all diaries and add 1
                new_num = WorkDiary.query.count() + 1
        else:
            new_num = 1
        
        return str(new_num)


    def to_dict(self):
        """Convert work diary object to dictionary for JSON responses"""
        return {
            'diary_id': self.diary_id,
            'diary_number': self.diary_number,
            'faculty_name': self.faculty.name if self.faculty else None,
            'subject': self.subject.subject_name if self.subject else None,
            'subject_code': self.subject.code if self.subject else None,
            'section': self.section.name if self.section else None,
            'academic_year': self.academic_year,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_hours': self.duration_hours,
            'activity_type': self.activity_type,
            'activity_title': self.activity_title,
            'activity_description': self.activity_description,
            'location': self.location,
            'students_present': self.students_present,
            'total_students': self.total_students,
            'topics_covered': self.topics_covered,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<WorkDiary {self.diary_number} - {self.faculty.name if self.faculty else 'N/A'}>"


# ---------------------------------------------------------------------
# Bulk Import Tracking
# ---------------------------------------------------------------------
class ImportLog(db.Model, TimestampMixin):
    """
    Track bulk import operations for audit and rollback purposes
    """
    __tablename__ = "import_logs"

    import_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    import_type = db.Column(
        db.Enum("faculty", "student", "subject", "schedule", "work_diary", "other",
                name="import_type_enum"),
        nullable=False
    )
    imported_by = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    file_name = db.Column(db.String(255))
    total_rows = db.Column(db.Integer, default=0)
    successful_rows = db.Column(db.Integer, default=0)
    failed_rows = db.Column(db.Integer, default=0)
    status = db.Column(
        db.Enum("processing", "completed", "failed", "partial", name="import_status_enum"),
        nullable=False, default="processing"
    )
    error_log = db.Column(db.Text)  # JSON string of errors
    import_data = db.Column(db.Text)  # JSON backup of imported data
    
    # Relationships
    imported_user = db.relationship("User")

    def to_dict(self):
        """Convert import log to dictionary"""
        return {
            'import_id': self.import_id,
            'import_type': self.import_type,
            'imported_by': self.imported_user.username if self.imported_user else None,
            'file_name': self.file_name,
            'total_rows': self.total_rows,
            'successful_rows': self.successful_rows,
            'failed_rows': self.failed_rows,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<ImportLog {self.import_type} - {self.status}>"


# ---------------------------------------------------------------------
# Student Subject Enrollment - For specialization/elective subjects
# ---------------------------------------------------------------------
class StudentSubjectEnrollment(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Individual student enrollment in specialization/elective subjects.
    For regular subjects, students are enrolled based on their section.
    For specialization subjects, students enroll individually.
    """
    __tablename__ = "student_subject_enrollments"

    enrollment_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=True, index=True) # Link to Virtual Section
    academic_year = db.Column(db.String(20))  # e.g., "2024-2025"
    semester = db.Column(db.Integer)  # 1-8

    # Relationships
    student = db.relationship("Student", backref=db.backref("subject_enrollments", lazy="dynamic", cascade="all, delete-orphan"))
    subject = db.relationship("Subject", backref=db.backref("student_enrollments", lazy="dynamic"))
    section = db.relationship("Section")

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "academic_year", name="uix_student_subject_year"),
    )

    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'student_name': f"{self.student.name}" if self.student else None,
            'student_usn': self.student.roll_number if self.student else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else None,
            'subject_code': self.subject.subject_code if self.subject else None,
            'academic_year': self.academic_year,
            'semester': self.semester
        }

    def __repr__(self):
        return f"<StudentSubjectEnrollment {self.student_id} -> {self.subject_id}>"


# ---------------------------------------------------------------------
# Campus Check-In System - Geo-fenced student attendance
# ---------------------------------------------------------------------
class CampusCheckIn(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Student daily campus check-in with location verification.
    Students can check in once per day when they are within campus premises.
    """
    __tablename__ = "campus_checkins"

    checkin_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), nullable=False, index=True)
    checkin_date = db.Column(db.Date, nullable=False, index=True)
    checkin_time = db.Column(db.Time, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Check-out fields (nullable as initally not checked out)
    checkout_time = db.Column(db.Time, nullable=True)
    checkout_latitude = db.Column(db.Float, nullable=True)
    checkout_longitude = db.Column(db.Float, nullable=True)
    
    is_valid_location = db.Column(db.Boolean, default=True)  # Within campus bounds
    device_info = db.Column(db.String(255))  # Optional: browser/device info

    # Relationships
    student = db.relationship("Student", backref=db.backref("campus_checkins", lazy="dynamic", cascade="all, delete-orphan"))

    __table_args__ = (
        UniqueConstraint("student_id", "checkin_date", name="uix_student_daily_checkin"),
        Index("ix_checkin_date_section", "checkin_date"),
    )

    def to_dict(self):
        """Convert campus check-in to dictionary for JSON responses"""
        return {
            'checkin_id': self.checkin_id,
            'student_id': self.student_id,
            'student_name': f"{self.student.name}" if self.student else None,
            'student_roll': self.student.roll_number if self.student else None,
            'checkin_date': self.checkin_date.isoformat() if self.checkin_date else None,
            'checkin_time': self.checkin_time.isoformat() if self.checkin_time else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_valid_location': self.is_valid_location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<CampusCheckIn {self.student_id} on {self.checkin_date}>"


class CollegeConfig(db.Model, TimestampMixin):
    """
    System configuration including campus location coordinates.
    Used to validate student check-in locations.
    """
    __tablename__ = "college_config"

    config_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    config_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # Campus location settings
    campus_latitude = db.Column(db.Float, nullable=True)
    campus_longitude = db.Column(db.Float, nullable=True)
    campus_radius_meters = db.Column(db.Integer, default=100)  # Check-in radius
    
    # College information
    college_name = db.Column(db.String(255))
    
    # Check-in time restrictions
    checkin_start_time = db.Column(db.Time)  # e.g., 07:00
    checkin_end_time = db.Column(db.Time)    # e.g., 18:00
    
    # General config value (for other settings)
    config_value = db.Column(db.Text)

    def to_dict(self):
        """Convert config to dictionary"""
        return {
            'config_id': self.config_id,
            'config_key': self.config_key,
            'campus_latitude': self.campus_latitude,
            'campus_longitude': self.campus_longitude,
            'campus_radius_meters': self.campus_radius_meters,
            'college_name': self.college_name,
            'checkin_start_time': self.checkin_start_time.isoformat() if self.checkin_start_time else None,
            'checkin_end_time': self.checkin_end_time.isoformat() if self.checkin_end_time else None,
            'config_value': self.config_value
        }

    def __repr__(self):
        return f"<CollegeConfig {self.config_key}>"


# ---------------------------------------------------------------------
# Faculty Attendance - Check-In/Checkout Tracking
# ---------------------------------------------------------------------
class FacultyAttendance(db.Model, TimestampMixin):
    """
    Track faculty check-in and checkout times with GPS validation
    """
    __tablename__ = 'faculty_attendance'
    
    attendance_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    faculty_id = db.Column(db.String(36), nullable=False)  # Foreign key removed - table already created
    date = db.Column(db.Date, nullable=False)
    
    # Check-in details
    check_in_time = db.Column(db.DateTime)
    check_in_latitude = db.Column(db.Float)
    check_in_longitude = db.Column(db.Float)
    check_in_accuracy = db.Column(db.Float)  # GPS accuracy in meters
    
    # Check-out details
    check_out_time = db.Column(db.DateTime)
    check_out_latitude = db.Column(db.Float)
    check_out_longitude = db.Column(db.Float)
    check_out_accuracy = db.Column(db.Float)  # GPS accuracy in meters
    check_out_valid = db.Column(db.Boolean, default=False)  # True if checkout was within campus radius
    
    # Relationships
    
    # Indexes
    __table_args__ = (
        Index('idx_faculty_date', 'faculty_id', 'date'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        from timezone_utils import format_ist_time
        return {
            'attendance_id': self.attendance_id,
            'faculty_id': self.faculty_id,
            'date': self.date.isoformat() if self.date else None,
            'check_in_time': format_ist_time(self.check_in_time, '%Y-%m-%dT%H:%M:%S') if self.check_in_time else None,
            'check_in_latitude': self.check_in_latitude,
            'check_in_longitude': self.check_in_longitude,
            'check_in_accuracy': self.check_in_accuracy,
            'check_out_time': format_ist_time(self.check_out_time, '%Y-%m-%dT%H:%M:%S') if self.check_out_time else None,
            'check_out_latitude': self.check_out_latitude,
            'check_out_longitude': self.check_out_longitude,
            'check_out_accuracy': self.check_out_accuracy,
            'check_out_valid': self.check_out_valid,
            'hours_worked': self.get_hours_worked()
        }
    
    def get_hours_worked(self):
        """Calculate hours worked"""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            return round(delta.total_seconds() / 3600, 2)
        return 0
    
    def __repr__(self):
        return f"<FacultyAttendance {self.faculty_id} {self.date}>"


# =====================================================
# Student Enrollment Model
# =====================================================

class StudentEnrollment(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Track which students are enrolled in which subjects
    Handles both core (auto) and elective (manual) enrollments
    """
    __tablename__ = "student_enrollments"
    
    enrollment_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=True, index=True)
    
    enrollment_type = db.Column(db.Enum("core", "elective", "specialization", name="enrollment_type_enum"), default="core")
    enrollment_status = db.Column(db.Enum("active", "dropped", "completed", name="enrollment_status_enum"), default="active")
    
    # Academic tracking
    semester_enrolled = db.Column(db.Integer)  # Which semester they enrolled
    academic_year = db.Column(db.String(20))  # e.g., "2023-24"
    
    # Relationships
    student = db.relationship("Student", backref=db.backref("enrollments", lazy="dynamic", cascade="all, delete-orphan"))
    subject = db.relationship("Subject", backref=db.backref("enrollments", lazy="dynamic"))
    section = db.relationship("Section")
    
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "is_deleted", name="uix_student_subject_enrollment"),
    )
    
    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'section_id': self.section_id,
            'enrollment_type': self.enrollment_type,
            'enrollment_status': self.enrollment_status,
            'semester_enrolled': self.semester_enrolled,
            'academic_year': self.academic_year,
            'student_name': self.student.name if self.student else None,
            'subject_name': self.subject.subject_name if self.subject else None
        }
    
    def __repr__(self):
        return f"<StudentEnrollment {self.student_id} -> {self.subject_id}>"


# ---------------------------------------------------------------------
# Fee Management Models
# ---------------------------------------------------------------------
class FeeTemplate(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Fee template defining base fees for different seat types and quotas per academic year.
    Admin creates these templates, which are then used to auto-assign fees to students.
    """
    __tablename__ = "fee_templates"
    
    # Primary key
    fee_template_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    
    # Academic year
    academic_year = db.Column(db.String(20), nullable=False, index=True)  # e.g., "2025-2026" (current year)
    batch_year = db.Column(db.String(20), nullable=False, index=True)  # e.g., "2024-2025" (joining year)
    
    # Seat type and quota
    seat_type = db.Column(db.String(20), nullable=False)  # 'GOVERNMENT', 'MANAGEMENT'
    quota_type = db.Column(db.String(20), nullable=True)  # 'MERIT', 'CATEGORY', NULL (for Management)
    
    # Fee amount
    base_fees = db.Column(db.Float, nullable=False)
    
    # Created by admin
    created_by_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    
    # Metadata
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])
    
    __table_args__ = (
        UniqueConstraint("academic_year", "batch_year", "seat_type", "quota_type", "is_deleted", 
                        name="uix_fee_template_year_batch_seat_quota"),
        Index("ix_fee_template_year_batch_seat", "academic_year", "batch_year", "seat_type", "quota_type"),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'fee_template_id': self.fee_template_id,
            'academic_year': self.academic_year,
            'batch_year': self.batch_year,
            'seat_type': self.seat_type,
            'quota_type': self.quota_type,
            'base_fees': self.base_fees,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        quota_str = f"-{self.quota_type}" if self.quota_type else ""
        return f"<FeeTemplate Batch:{self.batch_year} Year:{self.academic_year} {self.seat_type}{quota_str}: ₹{self.base_fees:,.0f}>"



class FeeStructure(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Total fees assigned to a student for a specific academic year.
    Set by class teacher. Can include carry forward from previous year.
    """
    __tablename__ = "fee_structures"
    
    # Primary key
    fee_structure_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    
    # Foreign keys
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=False, index=True)
    template_id = db.Column(db.String(36), db.ForeignKey("fee_templates.fee_template_id"), nullable=True)  # Link to template used
    
    # Academic year tracking
    academic_year = db.Column(db.String(20), nullable=False, index=True)  # e.g., "2023-2024"
    
    # Fee breakdown
    base_fees = db.Column(db.Float, nullable=False, default=0)  # Current year fees (from template)
    carry_forward = db.Column(db.Float, nullable=False, default=0)  # From previous year
    additional_charges = db.Column(db.Float, nullable=False, default=0)  # Late fees, etc. (deprecated - use additional_fees)
    total_fees = db.Column(db.Float, nullable=False)  # Total to be paid
    
    # Additional fees (new system)
    additional_fees = db.Column(db.JSON, nullable=True)  # Array of {description, amount}
    
    # Auto-generation tracking
    is_auto_generated = db.Column(db.Boolean, default=False)  # True if created automatically from template
    
    # Set by class teacher or auto-assigned
    set_by_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    
    # Retention tracking
    is_retained = db.Column(db.Boolean, default=False)  # True if student retained in same year
    previous_year = db.Column(db.String(20), nullable=True)  # Previous academic year if retained
    
    # Metadata
    remarks = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    # Relationships
    student = db.relationship("Student", backref=db.backref("fee_structures", lazy="dynamic", cascade="all, delete-orphan"))
    section = db.relationship("Section")
    template = db.relationship("FeeTemplate", foreign_keys=[template_id])
    set_by = db.relationship("User", foreign_keys=[set_by_user_id])
    fee_receipts = db.relationship("FeeReceipt", back_populates="fee_structure", lazy="dynamic")
    
    __table_args__ = (
        UniqueConstraint("student_id", "academic_year", "is_deleted", name="uix_student_year_fee"),
        Index("ix_fee_structure_student_year", "student_id", "academic_year"),
    )
    
    @property
    def amount_paid(self):
        """Calculate total amount paid (sum of approved receipts)"""
        approved_receipts = self.fee_receipts.filter_by(approved=True, is_deleted=False).all()
        return sum(receipt.amount_paid for receipt in approved_receipts)
    
    @property
    def balance(self):
        """Calculate outstanding fees (total - total_paid)"""
        return self.total_fees - self.amount_paid

    def calculate_outstanding(self):
        """Calculate outstanding fees (total - sum of approved receipts)"""
        approved_receipts = self.fee_receipts.filter_by(approved=True, is_deleted=False).all()
        total_paid = sum(receipt.amount_paid for receipt in approved_receipts)
        return self.total_fees - total_paid
    
    def calculate_total_paid(self):
        """Calculate total amount paid (sum of approved receipts)"""
        approved_receipts = self.fee_receipts.filter_by(approved=True, is_deleted=False).all()
        return sum(receipt.amount_paid for receipt in approved_receipts)
    
    def to_dict(self):
        """Convert fee structure object to dictionary for JSON responses"""
        return {
            'fee_structure_id': self.fee_structure_id,
            'student_id': self.student_id,
            'student_name': f"{self.student.name}" if self.student else None,
            'roll_number': self.student.roll_number if self.student else None,
            'section_id': self.section_id,
            'section_name': self.section.section_name if self.section else None,
            'academic_year': self.academic_year,
            'base_fees': self.base_fees,
            'carry_forward': self.carry_forward,
            'additional_charges': self.additional_charges,
            'total_fees': self.total_fees,
            'total_paid': self.calculate_total_paid(),
            'outstanding': self.calculate_outstanding(),
            'is_retained': self.is_retained,
            'previous_year': self.previous_year,
            'status': self.status,
            'remarks': self.remarks,
            'set_by': self.set_by.username if self.set_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<FeeStructure {self.student_id} {self.academic_year} - ?{self.total_fees}>"


class FeeReceipt(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Individual fee payment receipts (installments).
    Students can make multiple payments per academic year.
    Requires class teacher approval to be counted towards total paid.
    """
    __tablename__ = "fee_receipts"
    
    # Primary key
    fee_receipt_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    
    # Foreign keys
    fee_structure_id = db.Column(db.String(36), db.ForeignKey("fee_structures.fee_structure_id"), 
                                 nullable=False, index=True)
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), nullable=False, index=True)
    
    # Receipt details (entered by student or class teacher)
    receipt_number = db.Column(db.String(100), nullable=False, unique=True, index=True)
    receipt_phone = db.Column(db.String(20), nullable=False)  # Phone on receipt
    amount_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, index=True)
    payment_mode = db.Column(db.String(50), nullable=True)  # cash, online, cheque, DD, etc.
    
    # Entry tracking
    entered_by_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    entered_by_role = db.Column(db.String(20), nullable=False)  # 'student' or 'faculty'
    
    # Approval workflow
    approved = db.Column(db.Boolean, default=False, nullable=False)
    approved_by_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Additional metadata
    remarks = db.Column(db.Text, nullable=True)
    
    # Relationships
    fee_structure = db.relationship("FeeStructure", back_populates="fee_receipts")
    student = db.relationship("Student", backref=db.backref("fee_receipts", lazy="dynamic", cascade="all, delete-orphan"))
    entered_by = db.relationship("User", foreign_keys=[entered_by_user_id])
    approved_by = db.relationship("User", foreign_keys=[approved_by_user_id])
    
    __table_args__ = (
        Index("ix_fee_receipt_student_structure", "student_id", "fee_structure_id"),
        Index("ix_fee_receipt_approved", "approved"),
    )
    
    def can_edit_by_student(self):
        """Students cannot edit receipts after submission"""
        return False
    
    def can_edit_by_teacher(self, faculty_id):
        """Teachers can edit receipts for their section students (even if approved)"""
        if self.student and self.student.section:
            return self.student.section.class_teacher_id == faculty_id
        return False
    
    def to_dict(self):
        """Convert fee receipt object to dictionary for JSON responses"""
        return {
            'fee_receipt_id': self.fee_receipt_id,
            'fee_structure_id': self.fee_structure_id,
            'student_id': self.student_id,
            'student_name': f"{self.student.name}" if self.student else None,
            'roll_number': self.student.roll_number if self.student else None,
            'receipt_number': self.receipt_number,
            'receipt_phone': self.receipt_phone,
            'amount_paid': self.amount_paid,
            'payment_date': self.payment_date.strftime('%d %b %Y') if self.payment_date else None,
            'payment_mode': self.payment_mode,
            'entered_by_role': self.entered_by_role,
            'entered_by': self.entered_by.username if self.entered_by else None,
            'approved': self.approved,
            'approved_by': self.approved_by.username if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<FeeReceipt {self.receipt_number} - ?{self.amount_paid} {'' if self.approved else ''}>"


class Holiday(db.Model, TimestampMixin):
    """
    Academic holidays including Sundays, 2nd/4th Saturdays, public holidays, and special holidays.
    """
    __tablename__ = "holidays"
    
    holiday_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    holiday_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    holiday_name = db.Column(db.String(100), nullable=False)
    holiday_type = db.Column(db.String(20), nullable=False) # sunday, saturday, public, special
    academic_year = db.Column(db.String(20), nullable=False, index=True) # e.g., "2024-2025"
    
    def to_dict(self):
        return {
            'holiday_id': self.holiday_id,
            'holiday_date': self.holiday_date.strftime('%d %b %Y'),
            'raw_date': self.holiday_date.isoformat(),
            'holiday_name': self.holiday_name,
            'holiday_type': self.holiday_type,
            'academic_year': self.academic_year,
            'day_name': self.holiday_date.strftime('%A')
        }

    def __repr__(self):
        return f"<Holiday {self.holiday_name} on {self.holiday_date}>"


# =====================================================
# SYSTEM SETTINGS
# =====================================================

class SystemSettings(db.Model):
    """
    Global system configuration settings
    Stores key-value pairs for system-wide settings like current academic year
    """
    __tablename__ = "system_settings"
    
    setting_key = db.Column(db.String(50), primary_key=True)
    setting_value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)
    updated_by = db.Column(db.String(36), db.ForeignKey("users.user_id"))
    
    # Relationships
    updated_by_user = db.relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<SystemSettings {self.setting_key}={self.setting_value}>"
    
    @staticmethod
    def get_current_academic_year():
        """Get the current academic year from settings"""
        setting = SystemSettings.query.get('current_academic_year')
        if setting:
            return setting.setting_value
        # Default to current year if not set
        from datetime import datetime
        current_year = datetime.now().year
        return f"{current_year}-{current_year + 1}"
    
    @staticmethod
    def set_current_academic_year(year, user_id=None):
        """Set the current academic year"""
        from datetime import datetime
        setting = SystemSettings.query.get('current_academic_year')
        if setting:
            setting.setting_value = year
            setting.updated_at = datetime.now()
            setting.updated_by = user_id
        else:
            setting = SystemSettings(
                setting_key='current_academic_year',
                setting_value=year,
                description='Current academic year for the entire system',
                updated_at=datetime.now(),
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting
