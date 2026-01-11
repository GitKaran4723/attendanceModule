from app import db, app
from models import Student, AttendanceRecord, AttendanceSession, ClassSchedule, Subject

app.app_context().push()

# Get student with 200% attendance
student = Student.query.filter_by(roll_number='U03NK24S0108').first()
if not student:
    print("Student not found!")
    exit()

print(f"Student: {student.name}")
print(f"Section ID: {student.section_id}")
print(f"Student ID: {student.student_id}")
print()

# Get all sessions for this student's section
sessions = db.session.query(
    AttendanceSession, 
    ClassSchedule,
    Subject
).join(
    ClassSchedule, AttendanceSession.schedule_id == ClassSchedule.schedule_id
).join(
    Subject, ClassSchedule.subject_id == Subject.subject_id
).filter(
    ClassSchedule.section_id == student.section_id,
    AttendanceSession.is_deleted == False
).all()

print(f"Total query results: {len(sessions)}")
print()

# Check for duplicates
from collections import defaultdict
session_subject_map = defaultdict(list)

for session, schedule, subject in sessions:
    key = (session.attendance_session_id, subject.subject_id, subject.subject_name)
    session_subject_map[key].append(schedule.schedule_id)

print("Sessions grouped by (session_id, subject_id, subject_name):")
for (sess_id, subj_id, subj_name), schedule_ids in session_subject_map.items():
    if len(schedule_ids) > 1:
        print(f"  DUPLICATE: {subj_name} - Session {sess_id[:8]}... has {len(schedule_ids)} schedules: {schedule_ids}")
    else:
        print(f"  OK: {subj_name} - Session {sess_id[:8]}...")

print()
print(f"Total unique (session, subject) pairs: {len(session_subject_map)}")
print(f"Duplicate pairs: {sum(1 for v in session_subject_map.values() if len(v) > 1)}")
