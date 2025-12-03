"""
User Creation Script - BCA BUB Attendance System

This script helps you create initial users for the system.
Run this after initializing the database.

Usage:
    python create_users.py
"""

from app import app, db
from models import User, Role, Faculty, Student
from auth import hash_password
from datetime import datetime
import uuid


def initialize_database():
    """Create all database tables"""
    with app.app_context():
        print("🔧 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")


def create_default_roles():
    """Create default roles if they don't exist"""
    with app.app_context():
        print("\n🔧 Creating default roles...")
        
        default_roles = ['admin', 'hod', 'faculty', 'student', 'parent']
        
        for role_name in default_roles:
            existing_role = Role.query.filter_by(role_name=role_name).first()
            if not existing_role:
                role = Role(role_name=role_name, description=f'{role_name.capitalize()} role')
                db.session.add(role)
                print(f"  ✅ Created role: {role_name}")
            else:
                print(f"  ℹ️  Role already exists: {role_name}")
        
        db.session.commit()
        print("✅ All roles created successfully!")


def create_admin():
    """Create default admin user"""
    with app.app_context():
        # Check if admin already exists
        existing = User.query.filter_by(username='admin').first()
        if existing:
            print("❌ Admin user already exists!")
            return
        
        admin_role = Role.query.filter_by(role_name='admin').first()
        if not admin_role:
            print("❌ Admin role not found! Run app.py first to initialize database.")
            return
        
        admin = User(
            username='admin',
            email='admin@bcabub.edu',
            password_hash=hash_password('admin123'),
            role_id=admin_role.role_id,
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ Admin user created successfully!")
        print("="*50)
        print("Username: admin")
        print("Password: admin123")
        print("⚠️  IMPORTANT: Change this password immediately after first login!")
        print("="*50 + "\n")


def create_hod():
    """Create HOD user"""
    with app.app_context():
        # Check if HOD already exists
        existing = User.query.filter_by(username='hod').first()
        if existing:
            print("ℹ️  HOD user already exists")
            return
        
        hod_role = Role.query.filter_by(role_name='hod').first()
        if not hod_role:
            print("❌ HOD role not found!")
            return
        
        hod_user = User(
            username='hod',
            email='hod@bcabub.edu',
            password_hash=hash_password('hod123'),
            role_id=hod_role.role_id,
            is_active=True
        )
        
        db.session.add(hod_user)
        db.session.commit()
        
        print("✅ HOD user created: hod / hod123")


def create_sample_faculty():
    """Create sample faculty user"""
    with app.app_context():
        # Check if faculty already exists
        existing = User.query.filter_by(username='faculty1').first()
        if existing:
            print("ℹ️  Faculty user already exists")
            return
        
        faculty_role = Role.query.filter_by(role_name='faculty').first()
        if not faculty_role:
            print("❌ Faculty role not found!")
            return
        
        # Create user account
        faculty_user = User(
            username='faculty1',
            email='faculty1@bcabub.edu',
            password_hash=hash_password('faculty123'),
            role_id=faculty_role.role_id,
            is_active=True
        )
        
        db.session.add(faculty_user)
        db.session.flush()
        
        # Create faculty record
        faculty_record = Faculty(
            employee_id='FAC001',
            first_name='Rajesh',
            last_name='Kumar',
            name='Rajesh Kumar',
            email='faculty1@bcabub.edu',
            phone='9876543210',
            designation='Assistant Professor',
            department='Computer Science',
            user_id=faculty_user.user_id
        )
        
        db.session.add(faculty_record)
        db.session.commit()
        
        print("✅ Faculty user created: faculty1 / faculty123")


def create_sample_student():
    """Create sample student user"""
    with app.app_context():
        # Check if student already exists
        existing = User.query.filter_by(username='student1').first()
        if existing:
            print("ℹ️  Student user already exists")
            return
        
        student_role = Role.query.filter_by(role_name='student').first()
        if not student_role:
            print("❌ Student role not found!")
            return
        
        # Create user account
        student_user = User(
            username='student1',
            email='student1@bcabub.edu',
            password_hash=hash_password('student123'),
            role_id=student_role.role_id,
            is_active=True
        )
        
        db.session.add(student_user)
        db.session.flush()
        
        # Create student record
        student_record = Student(
            roll_number='BCA2021001',
            usn='BCA2021001',
            first_name='Amit',
            last_name='Sharma',
            name='Amit Sharma',
            email='student1@bcabub.edu',
            phone='9876543211',
            date_of_birth=datetime(2003, 5, 15).date(),
            user_id=student_user.user_id
        )
        
        db.session.add(student_record)
        db.session.commit()
        
        print("✅ Student user created: student1 / student123")


def create_sample_parent():
    """Create sample parent user"""
    with app.app_context():
        # Check if parent already exists
        existing = User.query.filter_by(username='parent1').first()
        if existing:
            print("ℹ️  Parent user already exists")
            return
        
        parent_role = Role.query.filter_by(role_name='parent').first()
        if not parent_role:
            print("❌ Parent role not found!")
            return
        
        # Create user account
        parent_user = User(
            username='parent1',
            email='parent1@bcabub.edu',
            password_hash=hash_password('parent123'),
            role_id=parent_role.role_id,
            is_active=True
        )
        
        db.session.add(parent_user)
        db.session.commit()
        
        print("✅ Parent user created: parent1 / parent123")


def create_all_sample_users():
    """Create all sample users"""
    print("\n" + "="*60)
    print("  BCA BUB - Database Initialization & User Creation")
    print("="*60 + "\n")
    
    try:
        # Step 1: Initialize database
        initialize_database()
        
        # Step 2: Create default roles
        create_default_roles()
        
        # Step 3: Create sample users
        print("\n🚀 Creating sample users...\n")
        create_admin()
        create_hod()
        create_sample_faculty()
        create_sample_student()
        create_sample_parent()
        
        print("\n" + "="*50)
        print("✅ All sample users created successfully!")
        print("="*50)
        print("\nLogin credentials:")
        print("-" * 50)
        print("Admin:   admin / admin123")
        print("HOD:     hod / hod123")
        print("Faculty: faculty1 / faculty123")
        print("Student: student1 / student123")
        print("Parent:  parent1 / parent123")
        print("-" * 50)
        print("\n⚠️  Change all passwords after first login!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error creating users: {e}")
        print("Make sure you've run the app once to initialize the database.\n")


if __name__ == '__main__':
    create_all_sample_users()
