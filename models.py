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
    qualification = db.Column(db.String(200))
    
    # Legacy field for backward compatibility
    name = db.Column(db.String(200), nullable=True)
    
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    employment_type = db.Column(db.Enum("full_time", "part_time", name="employment_type_enum"), nullable=True)
    join_date = db.Column(db.Date)
    designation = db.Column(db.String(128))
    is_hod = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(32), default="active")

    # Relationships
    user = db.relationship("User", back_populates="faculty")
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
            'qualification': self.qualification,
            'designation': self.designation,
            'employment_type': self.employment_type,
            'is_hod': self.is_hod,
            'status': self.status,
            'join_date': self.join_date.isoformat() if self.join_date else None
        }

    def __repr__(self):
        return f"<Faculty {self.first_name} {self.last_name}>"


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
    
    # Legacy field for backward compatibility
    name = db.Column(db.String(64), nullable=True)
    
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=False, index=True)
    year_of_study = db.Column(db.Integer)
    academic_year = db.Column(db.String(20))  # e.g., "2024-2025"
    current_semester = db.Column(db.Integer)  # Which semester they're in

    # Relationships
    program = db.relationship("Program", back_populates="sections")
    students = db.relationship("Student", back_populates="section", lazy="dynamic")
    allocations = db.relationship("SubjectAllocation", back_populates="section", lazy="dynamic")
    schedules = db.relationship("ClassSchedule", back_populates="section", lazy="dynamic")
    tests = db.relationship("Test", back_populates="section", lazy="dynamic")

    __table_args__ = (
        UniqueConstraint("section_name", "program_id", "current_semester", "academic_year", name="uix_section_program_semester"),
    )

    def to_dict(self):
        """Convert section object to dictionary for JSON responses"""
        return {
            'section_id': self.section_id,
            'name': self.name,
            'program_id': self.program_id,
            'program_name': self.program.name if self.program else None,
            'year_of_study': self.year_of_study,
            'student_count': self.students.count()
        }

    def __repr__(self):
        return f"<Section {self.name}>"


class Student(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Student information and academic details.
    Linked to User for authentication.
    """
    __tablename__ = "students"

    student_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    
    # New detailed fields
    roll_number = db.Column(db.String(64), unique=True, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    guardian_name = db.Column(db.String(200))
    guardian_phone = db.Column(db.String(20))
    
    # Legacy fields for backward compatibility
    usn = db.Column(db.String(64), nullable=True, index=True)  # University Seat Number
    name = db.Column(db.String(200), nullable=True)
    dob = db.Column(db.Date)
    
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=True)
    admission_year = db.Column(db.Integer)
    current_semester = db.Column(db.Integer)  # Which semester (1-8)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.semester_id"), nullable=True)
    status = db.Column(db.String(32), default="active")

    # Relationships
    user = db.relationship("User", back_populates="student")
    program = db.relationship("Program")
    section = db.relationship("Section", back_populates="students")
    semester = db.relationship("Semester")
    attendance_records = db.relationship("AttendanceRecord", back_populates="student", lazy="dynamic")
    test_results = db.relationship("TestResult", back_populates="student", lazy="dynamic")

    def to_dict(self):
        """Convert student object to dictionary for JSON responses"""
        return {
            'student_id': self.student_id,
            'roll_number': self.roll_number,
            'usn': self.roll_number or self.usn,  # Backward compatibility
            'first_name': self.first_name,
            'last_name': self.last_name,
            'name': self.name or f"{self.first_name} {self.last_name}",  # Backward compatibility
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'dob': (self.date_of_birth or self.dob).isoformat() if (self.date_of_birth or self.dob) else None,
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
        return f"<Student {self.roll_number or self.usn} - {self.first_name} {self.last_name}>"


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
    
    # Academic details
    program_id = db.Column(db.String(36), db.ForeignKey("programs.program_id"), nullable=True, index=True)
    semester_id = db.Column(db.Integer, nullable=True)  # Which semester (1-8)
    description = db.Column(db.Text)
    total_hours = db.Column(db.Integer)  # Total teaching hours

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
            'total_hours': self.total_hours
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
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=False, index=True)
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
    Class schedule/timetable entries
    """
    __tablename__ = "class_schedules"

    schedule_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False)
    faculty_id = db.Column(db.String(36), db.ForeignKey("faculties.faculty_id"), nullable=False)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=False)
    room_id = db.Column(db.String(64))
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    class_type = db.Column(db.String(16))  # theory/practical
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.semester_id"), nullable=True)

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
    An attendance session represents one instance of taking attendance
    for a scheduled class. Multiple students will have records under this session.
    """
    __tablename__ = "attendance_sessions"

    attendance_session_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    schedule_id = db.Column(db.String(36), db.ForeignKey("class_schedules.schedule_id"), 
                           nullable=False, index=True)
    taken_by_user_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    taken_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum("draft", "finalized", name="attendance_status_enum"), 
                      nullable=False, default="draft")
    approved_by = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=True)
    approved_at = db.Column(db.DateTime)

    # Relationships
    schedule = db.relationship("ClassSchedule", back_populates="attendance_sessions")
    taken_by = db.relationship("User", foreign_keys=[taken_by_user_id])
    approved_user = db.relationship("User", foreign_keys=[approved_by])
    records = db.relationship("AttendanceRecord", back_populates="attendance_session", 
                            lazy="dynamic", cascade="all, delete-orphan")

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
            'faculty': self.faculty.name if self.faculty else None,
            'section': self.section.name if self.section else None,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'max_marks': self.max_marks
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
        Generate unique diary number in format: WD-YYYY-NNNN
        Example: WD-2025-0001, WD-2025-0002, etc.
        """
        if year is None:
            year = datetime.now().year
        
        # Get the last diary number for this year
        prefix = f"WD-{year}-"
        last_diary = WorkDiary.query.filter(
            WorkDiary.diary_number.like(f"{prefix}%")
        ).order_by(WorkDiary.diary_number.desc()).first()
        
        if last_diary:
            # Extract number and increment
            last_num = int(last_diary.diary_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"

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
