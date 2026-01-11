
from app import app
from models import db, User, Faculty, SubjectAllocation, Subject, Section

with app.app_context():
    user = User.query.filter_by(username='karansj4723').first()
    if user and user.faculty:
        faculty = user.faculty
        allocations = SubjectAllocation.query.filter_by(faculty_id=faculty.faculty_id, is_deleted=False).all()
        print(f"--- ALLOCATIONS FOR {user.username} ---")
        for a in allocations:
            sub_name = a.subject.subject_name if a.subject else "N/A"
            sec_name = a.section.section_name if a.section else "N/A"
            print(f"Subject: {sub_name} (ID: {a.subject_id}), Section: {sec_name} (ID: {a.section_id})")
    else:
        print("Faculty not found or user has no faculty profile.")
    print("--- END ---")
