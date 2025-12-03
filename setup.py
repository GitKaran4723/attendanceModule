"""
Complete Setup Script for BCA BUB Attendance System
This script will:
1. Install required dependencies
2. Initialize the database
3. Create sample users
4. Display setup instructions
"""

import subprocess
import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def install_dependencies():
    """Install Python dependencies"""
    print_header("STEP 1: Installing Dependencies")
    
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!\n")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def initialize_database():
    """Initialize database and create tables"""
    print_header("STEP 2: Initializing Database")
    
    print("🗄️  Creating database tables...")
    try:
        from app import app, db, create_default_roles
        with app.app_context():
            db.create_all()
            create_default_roles()
        print("✅ Database initialized successfully!\n")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}\n")
        return False

def create_sample_users():
    """Create sample users"""
    print_header("STEP 3: Creating Sample Users")
    
    print("👥 Creating admin, faculty, and student accounts...")
    try:
        from create_users import create_all_sample_users
        create_all_sample_users()
        return True
    except Exception as e:
        print(f"❌ User creation failed: {e}\n")
        return False

def display_success():
    """Display success message and instructions"""
    print_header("🎉 SETUP COMPLETED SUCCESSFULLY!")
    
    print("Your BCA BUB Attendance System is ready to use!\n")
    
    print("📝 Sample Login Credentials:")
    print("-" * 60)
    print("  Role      | Username  | Password")
    print("-" * 60)
    print("  Admin     | admin     | admin123")
    print("  HOD       | hod       | hod123")
    print("  Faculty   | faculty1  | faculty123")
    print("  Student   | student1  | student123")
    print("-" * 60)
    
    print("\n🚀 To start the application:")
    print("   python app.py")
    
    print("\n🌐 Access the application:")
    print("   Local:   http://localhost:5000")
    print("   Login:   http://localhost:5000/login")
    print("   Mobile:  http://YOUR_IP:5000")
    
    print("\n📚 Documentation:")
    print("   README.md              - Main documentation")
    print("   WORK_DIARY_GUIDE.md    - Work Diary & Auth guide")
    print("   QUICKSTART.md          - Quick start guide")
    
    print("\n📁 Sample Import Files:")
    print("   sample_imports/students_template.csv")
    print("   sample_imports/faculty_template.csv")
    print("   sample_imports/subjects_template.csv")
    print("   sample_imports/schedules_template.csv")
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("   1. Change all default passwords immediately")
    print("   2. Set a strong SECRET_KEY in production")
    print("   3. Use HTTPS in production environment")
    print("   4. Never commit passwords to version control")
    
    print("\n" + "="*60)
    print("  Ready to go! Run 'python app.py' to start the server")
    print("="*60 + "\n")

def main():
    """Main setup function"""
    print_header("BCA BUB Attendance System - Complete Setup")
    
    print("This script will set up your attendance system with:")
    print("  ✓ All required dependencies (Flask, SQLAlchemy, Pandas, etc.)")
    print("  ✓ Database with 16 tables")
    print("  ✓ Authentication system")
    print("  ✓ Work diary functionality")
    print("  ✓ Bulk import capability")
    print("  ✓ Sample users and data")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n⚠️  Setup failed at dependency installation")
        return
    
    # Step 2: Initialize database
    if not initialize_database():
        print("\n⚠️  Setup failed at database initialization")
        return
    
    # Step 3: Create sample users
    if not create_sample_users():
        print("\n⚠️  Setup failed at user creation")
        return
    
    # Display success message
    display_success()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        print("Please check the error and try again")
