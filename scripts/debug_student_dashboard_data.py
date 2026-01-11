import sys
import os
# Add parent dir to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Student, Section, Subject, StudentSubjectEnrollment

def debug_dashboard(username):
    with app.app_context():
        print(f"--- Debugging for user: {username} ---")
        from models import User
        user = User.query.filter_by(username=username).first()
        if not user:
            print("User not found")
            return

        student = Student.query.filter_by(user_id=user.user_id).first()
        if not student:
            print("Student record not found")
            return
            
        print(f"Student: {student.name} (ID: {student.student_id})")
        
        section = Section.query.get(student.section_id)
        if not section:
            print("Section not found")
            return
            
        print(f"Section: {section.section_name} (ID: {section.section_id})")
        print(f"  Program ID: {section.program_id} (Type: {type(section.program_id)})")
        print(f"  Semester: {section.current_semester} (Type: {type(section.current_semester)})")
        print(f"  Academic Year: {section.academic_year}")
        
        # 1. Test Compulsory Subjects Query
        print("\n--- Compulsory Subjects Query ---")
        compulsory_subjects = Subject.query.filter(
            Subject.program_id == section.program_id,
            Subject.semester_id == section.current_semester,
            Subject.subject_category == 'compulsory'
        ).all()
        print(f"Found {len(compulsory_subjects)} compulsory subjects:")
        for s in compulsory_subjects:
            print(f"  - {s.subject_name} (ID: {s.subject_id}, Sem: {s.semester_id}, Prog: {s.program_id})")
            
        if len(compulsory_subjects) == 0:
            print("  [DEBUG] Checking why no compulsory subjects found...")
            # Check if any subjects exist for this program
            any_prog_subjects = Subject.query.filter_by(program_id=section.program_id).all()
            print(f"  Total subjects for Program {section.program_id}: {len(any_prog_subjects)}")
            if any_prog_subjects:
                print(f"  First 3 subjects semesters: {[s.semester_id for s in any_prog_subjects[:3]]}")
                print(f"  Categories: {[s.subject_category for s in any_prog_subjects]}")
                print(f"  Comparison: Subject Sem '{any_prog_subjects[0].semester_id}' vs Section Sem '{section.current_semester}'")
        
        # 2. Test Elective Subjects Query
        print("\n--- Elective Subjects Query ---")
        enrollments = StudentSubjectEnrollment.query.filter_by(
            student_id=student.student_id,
            semester=section.current_semester
        ).all()
        print(f"Found {len(enrollments)} enrollments matching semester {section.current_semester}")
        
        enrolled_electives = db.session.query(Subject).join(StudentSubjectEnrollment).filter(
            StudentSubjectEnrollment.student_id == student.student_id,
            StudentSubjectEnrollment.semester == section.current_semester
        ).all()
        print(f"Found {len(enrolled_electives)} enrolled electives:")
        for s in enrolled_electives:
            print(f"  - {s.subject_name}")

if __name__ == "__main__":
    username = "teststudent_subj" 
    if len(sys.argv) > 1:
        username = sys.argv[1]
    
    # Try to verify if this user is valid for debugging
    with app.app_context():
        from models import User
        user = User.query.filter_by(username=username).first()
        valid = False
        if user:
            stud = Student.query.filter_by(user_id=user.user_id).first()
            if stud and stud.section_id:
                valid = True
        
        if not valid:
            print(f"User '{username}' invalid or has no section. Searching for a valid student...")
            student = Student.query.filter(Student.section_id != None).first()
            if student:
                print(f"Found valid student: {student.name} (User: {student.user.username})")
                username = student.user.username
            else:
                print("No students with sections found in DB!")
                sys.exit(1)

    debug_dashboard(username)
