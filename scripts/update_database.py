"""
Database Update Script for Admin Interface
===========================================
This script adds new fields to existing tables to support the admin interface.
Run this BEFORE using the admin interface if you have existing data.

If you have a fresh database, just run:
    python create_users.py

For existing databases, run this script first:
    python update_database.py
"""

from app import app, db
from models import (
    Faculty, Student, Subject, Program, Section,
    Unit, Chapter, Concept
)
from sqlalchemy import text

def update_database():
    """Add new columns to existing tables"""
    with app.app_context():
        print("🔄 Updating database schema...")
        
        try:
            # Get database connection
            connection = db.engine.connect()
            
            # Update Faculty table
            print("\n📚 Updating Faculty table...")
            try:
                connection.execute(text("ALTER TABLE faculties ADD COLUMN employee_id VARCHAR(50)"))
                print("  ✅ Added employee_id column")
            except:
                print("  ℹ️  employee_id column already exists")
            
            try:
                connection.execute(text("ALTER TABLE faculties ADD COLUMN first_name VARCHAR(100)"))
                print("  ✅ Added first_name column")
            except:
                print("  ℹ️  first_name column already exists")
            
            try:
                connection.execute(text("ALTER TABLE faculties ADD COLUMN last_name VARCHAR(100)"))
                print("  ✅ Added last_name column")
            except:
                print("  ℹ️  last_name column already exists")
            
            try:
                connection.execute(text("ALTER TABLE faculties ADD COLUMN department VARCHAR(100)"))
                print("  ✅ Added department column")
            except:
                print("  ℹ️  department column already exists")
            
            try:
                connection.execute(text("ALTER TABLE faculties ADD COLUMN qualification VARCHAR(200)"))
                print("  ✅ Added qualification column")
            except:
                print("  ℹ️  qualification column already exists")
            
            # Update Student table
            print("\n👥 Updating Student table...")
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN roll_number VARCHAR(64)"))
                print("  ✅ Added roll_number column")
            except:
                print("  ℹ️  roll_number column already exists")
            
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN first_name VARCHAR(100)"))
                print("  ✅ Added first_name column")
            except:
                print("  ℹ️  first_name column already exists")
            
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN last_name VARCHAR(100)"))
                print("  ✅ Added last_name column")
            except:
                print("  ℹ️  last_name column already exists")
            
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN date_of_birth DATE"))
                print("  ✅ Added date_of_birth column")
            except:
                print("  ℹ️  date_of_birth column already exists")
            
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN address TEXT"))
                print("  ✅ Added address column")
            except:
                print("  ℹ️  address column already exists")
            
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN guardian_name VARCHAR(200)"))
                print("  ✅ Added guardian_name column")
            except:
                print("  ℹ️  guardian_name column already exists")
            
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN guardian_phone VARCHAR(20)"))
                print("  ✅ Added guardian_phone column")
            except:
                print("  ℹ️  guardian_phone column already exists")
            
            try:
                connection.execute(text("ALTER TABLE students ADD COLUMN current_semester INTEGER"))
                print("  ✅ Added current_semester column")
            except:
                print("  ℹ️  current_semester column already exists")
            
            # Update Subject table
            print("\n📖 Updating Subject table...")
            try:
                connection.execute(text("ALTER TABLE subjects ADD COLUMN subject_code VARCHAR(64)"))
                print("  ✅ Added subject_code column")
            except:
                print("  ℹ️  subject_code column already exists")
            
            try:
                connection.execute(text("ALTER TABLE subjects ADD COLUMN subject_type VARCHAR(64)"))
                print("  ✅ Added subject_type column")
            except:
                print("  ℹ️  subject_type column already exists")
            
            try:
                connection.execute(text("ALTER TABLE subjects ADD COLUMN program_id VARCHAR(36)"))
                print("  ✅ Added program_id column")
            except:
                print("  ℹ️  program_id column already exists")
            
            try:
                connection.execute(text("ALTER TABLE subjects ADD COLUMN semester_id INTEGER"))
                print("  ✅ Added semester_id column")
            except:
                print("  ℹ️  semester_id column already exists")
            
            try:
                connection.execute(text("ALTER TABLE subjects ADD COLUMN description TEXT"))
                print("  ✅ Added description column")
            except:
                print("  ℹ️  description column already exists")
            
            try:
                connection.execute(text("ALTER TABLE subjects ADD COLUMN total_hours INTEGER"))
                print("  ✅ Added total_hours column")
            except:
                print("  ℹ️  total_hours column already exists")
            
            # Update Program table
            print("\n🎓 Updating Program table...")
            try:
                connection.execute(text("ALTER TABLE programs ADD COLUMN program_code VARCHAR(50)"))
                print("  ✅ Added program_code column")
            except:
                print("  ℹ️  program_code column already exists")
            
            try:
                connection.execute(text("ALTER TABLE programs ADD COLUMN program_name VARCHAR(150)"))
                print("  ✅ Added program_name column")
            except:
                print("  ℹ️  program_name column already exists")
            
            try:
                connection.execute(text("ALTER TABLE programs ADD COLUMN duration_years INTEGER"))
                print("  ✅ Added duration_years column")
            except:
                print("  ℹ️  duration_years column already exists")
            
            # Update Section table
            print("\n📋 Updating Section table...")
            try:
                connection.execute(text("ALTER TABLE sections ADD COLUMN section_name VARCHAR(64)"))
                print("  ✅ Added section_name column")
            except:
                print("  ℹ️  section_name column already exists")
            
            try:
                connection.execute(text("ALTER TABLE sections ADD COLUMN academic_year VARCHAR(20)"))
                print("  ✅ Added academic_year column")
            except:
                print("  ℹ️  academic_year column already exists")
            
            try:
                connection.execute(text("ALTER TABLE sections ADD COLUMN current_semester INTEGER"))
                print("  ✅ Added current_semester column")
            except:
                print("  ℹ️  current_semester column already exists")
            
            connection.close()
            
            # Create new tables for curriculum hierarchy
            print("\n🏗️  Creating new tables for curriculum hierarchy...")
            db.create_all()
            print("  ✅ Created Units, Chapters, Concepts tables")
            
            print("\n✅ Database update completed successfully!")
            print("\n📝 Next steps:")
            print("  1. Copy data from old fields to new fields if needed")
            print("  2. Run the application: python app.py")
            print("  3. Login as admin and test the interface")
            
        except Exception as e:
            print(f"\n❌ Error updating database: {str(e)}")
            print("If you have a fresh database, just run: python create_users.py")
            raise


def copy_legacy_data():
    """Copy data from legacy fields to new fields"""
    with app.app_context():
        print("\n📋 Copying legacy data to new fields...")
        
        # Update Faculties
        faculties = Faculty.query.all()
        for faculty in faculties:
            if faculty.name and not faculty.first_name:
                parts = faculty.name.split(' ', 1)
                faculty.first_name = parts[0]
                faculty.last_name = parts[1] if len(parts) > 1 else ''
                print(f"  ✅ Updated faculty: {faculty.name}")
        
        # Update Students
        students = Student.query.all()
        for student in students:
            if student.name and not student.name:
                parts = student.name.split(' ', 1)
                student.name = parts[0]
                student.name = parts[1] if len(parts) > 1 else ''
                print(f"  ✅ Updated student: {student.name}")
            
            if student.usn and not student.roll_number:
                student.roll_number = student.usn
                print(f"  ✅ Copied USN to roll_number: {student.usn}")
            
            if student.dob and not student.date_of_birth:
                student.date_of_birth = student.dob
                print(f"  ✅ Copied dob to date_of_birth")
        
        # Update Subjects
        subjects = Subject.query.all()
        for subject in subjects:
            if subject.code and not subject.subject_code:
                subject.subject_code = subject.code
                print(f"  ✅ Updated subject: {subject.code}")
        
        # Update Programs
        programs = Program.query.all()
        for program in programs:
            if program.name and not program.program_name:
                program.program_name = program.name
                # Generate program code from name
                if not program.program_code:
                    program.program_code = ''.join([word[0].upper() for word in program.name.split()[:3]])
                print(f"  ✅ Updated program: {program.name}")
        
        # Update Sections
        sections = Section.query.all()
        for section in sections:
            if section.name and not section.section_name:
                section.section_name = section.name
                print(f"  ✅ Updated section: {section.name}")
        
        db.session.commit()
        print("\n✅ Legacy data copied successfully!")


if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         BCA BUB - Admin Interface Database Updater            ║
║                                                               ║
║  This script will update your database schema to support     ║
║  the new admin interface features.                           ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    response = input("Do you want to update the database? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        update_database()
        
        copy_response = input("\nDo you want to copy legacy data to new fields? (yes/no): ")
        if copy_response.lower() in ['yes', 'y']:
            copy_legacy_data()
        
        print("\n✅ All done! You can now start the application.")
        print("   Run: python app.py")
    else:
        print("❌ Update cancelled.")
