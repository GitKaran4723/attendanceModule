"""
Test configuration and fixtures for BCA BUB Attendance System
"""
import pytest
from app import app as flask_app
from models import db


@pytest.fixture
def app():
    """Create application for testing"""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Authentication headers for API testing"""
    # TODO: Implement actual authentication
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_admin(app):
    """Create sample admin user"""
    from models import User, Role
    
    with app.app_context():
        admin_role = Role(role_name="Admin", description="Administrator")
        db.session.add(admin_role)
        db.session.commit()
        
        admin_user = User(
            username="admin",
            email="admin@test.com",
            password_hash="hashed_password",  # TODO: Use proper hashing
            role_id=admin_role.role_id
        )
        db.session.add(admin_user)
        db.session.commit()
        
        return admin_user


@pytest.fixture
def sample_student(app):
    """Create sample student user"""
    from models import User, Role, Student, Program, Section
    
    with app.app_context():
        student_role = Role(role_name="Student", description="Student")
        db.session.add(student_role)
        db.session.commit()
        
        user = User(
            username="student1",
            email="student1@test.com",
            password_hash="hashed_password",
            role_id=student_role.role_id
        )
        db.session.add(user)
        db.session.commit()
        
        program = Program(
            program_code="BCA",
            program_name="Bachelor of Computer Applications",
            duration_years=3
        )
        db.session.add(program)
        db.session.commit()
        
        section = Section(
            section_name="Section A",
            program_id=program.program_id,
            year_of_study=3,
            current_semester=5
        )
        db.session.add(section)
        db.session.commit()
        
        student = Student(
            user_id=user.user_id,
            roll_number="BCA001",
            first_name="Test",
            last_name="Student",
            program_id=program.program_id,
            section_id=section.section_id
        )
        db.session.add(student)
        db.session.commit()
        
        return student


@pytest.fixture
def sample_faculty(app):
    """Create sample faculty user"""
    from models import User, Role, Faculty
    
    with app.app_context():
        faculty_role = Role(role_name="Faculty", description="Faculty")
        db.session.add(faculty_role)
        db.session.commit()
        
        user = User(
            username="faculty1",
            email="faculty1@test.com",
            password_hash="hashed_password",
            role_id=faculty_role.role_id
        )
        db.session.add(user)
        db.session.commit()
        
        faculty = Faculty(
            user_id=user.user_id,
            employee_id="FAC001",
            first_name="Test",
            last_name="Faculty",
            department="Computer Science"
        )
        db.session.add(faculty)
        db.session.commit()
        
        return faculty
