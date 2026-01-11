import sys
import os
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Student, Subject, Section, StudentSubjectEnrollment, User, Role
from werkzeug.security import generate_password_hash
import uuid

def setup_test_data():
    with app.app_context():
        # Create Role
        role = Role.query.filter_by(role_name='admin').first()
        if not role:
            role = Role(role_id=str(uuid.uuid4()), role_name='admin')
            db.session.add(role)

        # Create Admin User
        admin_user = User.query.filter_by(username='testadmin_subject').first()
        if not admin_user:
            admin_user = User(
                username='testadmin_subject',
                password_hash=generate_password_hash('password'),
                email='testadmin_subject@example.com',
                role_id=role.role_id,
                is_active=True,
                is_deleted=False
            )
            db.session.add(admin_user)
        else:
            admin_user.is_deleted = False # Ensure not deleted
            
        # Create Student
        student_user = User.query.filter_by(username='teststudent_subj').first()
        if not student_user:
             student_role = Role.query.filter_by(role_name='student').first()
             student_user = User(
                username='teststudent_subj',
                password_hash=generate_password_hash('password'),
                email='teststudent_subj@example.com',
                role_id=student_role.role_id,
                is_active=True,
                is_deleted=False
            )
             db.session.add(student_user)
             db.session.flush()
             
             student = Student(
                 user_id=student_user.user_id,
                 roll_number='TESTSUBJ001',
                 name='Test Subject Student'
             )
             db.session.add(student)
             
        # Create Subject
        subject = Subject.query.filter_by(subject_code='TESTSUBJ101').first()
        if not subject:
            subject = Subject(
                subject_id=str(uuid.uuid4()),
                subject_code='TESTSUBJ101',
                subject_name='Test Subject 101',
                semester_id=1,
                credits=4,
                subject_type='theory',
                program_id=1 
            )
            # Try to link to a program if possible
            from models import Program
            program = Program.query.first()
            if program:
                subject.program_id = program.program_id
            db.session.add(subject)
            
        db.session.commit()
        return admin_user.username, 'password', subject.subject_id, Student.query.filter_by(roll_number='TESTSUBJ001').first().student_id

def test_flow():
    client = app.test_client()
    
    # 1. Login
    print("[TEST] Logging in as Admin...")
    username, password, subject_id, student_id = setup_test_data()
    
    login_resp = client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)
    if login_resp.status_code != 200:
        print("Login Failed")
        return
    print("Login Successful")
    
    # 2. GET Page
    print(f"[TEST] Fetching Enrollment Page for Subject {subject_id}...")
    resp = client.get(f"/admin/subjects/{subject_id}/enroll-students")
    if resp.status_code == 200:
        print("Page Load Successful")
    else:
        print(f"Page Load Failed: {resp.status_code}")
        print(resp.data.decode('utf-8')[:500])
        return

    # 3. Enroll Student (POST)
    print(f"[TEST] Enrolling Student {student_id}...")
    payload = {
        "subject_id": subject_id,
        "student_ids": [student_id]
    }
    resp = client.post("/api/admin/enrollments/add", json=payload)
    data = resp.json
    if data and data.get('success'):
        print(f"Enrollment Successful: {data}")
    else:
        print(f"Enrollment Failed: {data}")
        print(resp.data)
        return

    # 4. Verify Virtual Section Exists
    with app.app_context():
        enrollment = StudentSubjectEnrollment.query.filter_by(subject_id=subject_id, student_id=student_id).first()
        if enrollment:
            print(f"[VERIFY] Enrollment Record Found: {enrollment.enrollment_id}")
            if enrollment.section and enrollment.section.is_elective:
                 print(f"[VERIFY] Virtual Section Created: {enrollment.section.section_name}")
            else:
                 print(f"[VERIFY] FAIL: Section Link Issue. Section: {enrollment.section} IsElective: {enrollment.section.is_elective if enrollment.section else 'N/A'}")
        else:
            print("[VERIFY] FAIL: Enrollment Record NOT Found")

    # 5. Unenroll (DELETE)
    if enrollment:
        print(f"[TEST] Unenrolling Student...")
        resp = client.delete(f"/api/admin/enrollments/{enrollment.enrollment_id}")
        data = resp.json
        if data and data.get('success'):
            print("Unenrollment Successful")
        else:
            print(f"Unenrollment Failed: {data}")
            
    # Verify Gone
    with app.app_context():
        gone = StudentSubjectEnrollment.query.filter_by(subject_id=subject_id, student_id=student_id).first()
        if not gone:
            print("[VERIFY] Student Successfully Removed from DB")
        else:
            print("[VERIFY] FAIL: Student still exists in DB")

if __name__ == "__main__":
    test_flow()
