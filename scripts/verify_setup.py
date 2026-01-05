"""
Installation Verification Script
Run this to check if everything is set up correctly
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version {version.major}.{version.minor} is too old")
        print("  Please install Python 3.7 or higher")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required = ['flask', 'flask_sqlalchemy', 'werkzeug', 'pandas', 'openpyxl']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print("\n⚠️  Missing packages. Run: pip install -r requirements.txt")
        return False
    return True


def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'models.py',
        'config.py',
        'auth.py',
        'requirements.txt',
        'static/manifest.json',
        'static/service-worker.js',
        'static/css/style.css',
        'static/js/app.js',
        'templates/index.html',
        'templates/faculty.html',
        'templates/students.html',
        'templates/attendance.html',
        'templates/login.html',
        'templates/work_diary.html',
        'templates/work_diary_form.html',
        'templates/admin_import.html',
        'sample_imports/students_template.csv',
        'sample_imports/faculty_template.csv'
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} is missing")
            missing.append(file_path)
    
    if missing:
        print("\n⚠️  Some files are missing!")
        return False
    return True


def check_database():
    """Check if database can be created"""
    try:
        from models import db
        from app import app
        
        with app.app_context():
            db.create_all()
        
        if os.path.exists('instance/attendance.db'):
            print("✓ Database created successfully")
            return True
        else:
            print("✗ Database creation failed")
            return False
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False


def main():
    """Run all checks"""
    print("="*50)
    print("BCA BUB - Installation Verification")
    print("="*50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_dependencies),
        ("File Structure", check_file_structure),
        ("Database Setup", check_database)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        results.append(check_func())
    
    print("\n" + "="*50)
    if all(results):
        print("✅ All checks passed!")
        print("="*50)
        print("\n🚀 You're ready to go!")
        print("   Run: python app.py")
    else:
        print("❌ Some checks failed!")
        print("="*50)
        print("\n⚠️  Please fix the issues above before running the app")
    print()


if __name__ == '__main__':
    main()
