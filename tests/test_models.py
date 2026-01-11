"""
Test cases for database models
Run with: pytest tests/test_models.py
"""
import pytest
from models import User, Role, Student, Faculty, Program, Section


class TestRoleModel:
    """Test Role model"""
    
    def test_create_role(self, app):
        """Test creating a role"""
        with app.app_context():
            role = Role(role_name="TestRole", description="Test Description")
            assert role.role_name == "TestRole"
            assert role.description == "Test Description"
    
    def test_role_to_dict(self, app):
        """Test role serialization"""
        with app.app_context():
            from models import db
            role = Role(role_name="Admin", description="Administrator")
            db.session.add(role)
            db.session.commit()
            
            role_dict = role.to_dict()
            assert role_dict['role_name'] == "Admin"
            assert role_dict['description'] == "Administrator"
            assert 'role_id' in role_dict


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, app, sample_admin):
        """Test creating a user"""
        with app.app_context():
            assert sample_admin.username == "admin"
            assert sample_admin.email == "admin@test.com"
            assert sample_admin.is_active is True
    
    def test_user_role_relationship(self, app, sample_admin):
        """Test user-role relationship"""
        with app.app_context():
            assert sample_admin.role is not None
            assert sample_admin.role.role_name == "Admin"


class TestStudentModel:
    """Test Student model"""
    
    def test_create_student(self, app, sample_student):
        """Test creating a student"""
        with app.app_context():
            assert sample_student.name == "Test"
            assert sample_student.roll_number == "BCA001"
    
    def test_student_program_relationship(self, app, sample_student):
        """Test student-program relationship"""
        with app.app_context():
            assert sample_student.program is not None
            assert sample_student.program.program_code == "BCA"
    
    def test_student_section_relationship(self, app, sample_student):
        """Test student-section relationship"""
        with app.app_context():
            assert sample_student.section is not None
            assert sample_student.section.section_name == "Section A"


class TestFacultyModel:
    """Test Faculty model"""
    
    def test_create_faculty(self, app, sample_faculty):
        """Test creating a faculty"""
        with app.app_context():
            assert sample_faculty.first_name == "Test"
            assert sample_faculty.last_name == "Faculty"
            assert sample_faculty.employee_id == "FAC001"
    
    def test_faculty_user_relationship(self, app, sample_faculty):
        """Test faculty-user relationship"""
        with app.app_context():
            assert sample_faculty.user is not None
            assert sample_faculty.user.username == "faculty1"


# TODO: Add more test cases for:
# - Attendance models
# - Work diary models
# - Test models
# - Validation constraints
# - Cascade deletes
# - Unique constraints
