"""
Department Routes for Faculty Coordinators
Integrated into faculty interface as "My Department" tab
"""

from flask import render_template, request, jsonify, session
from datetime import date, datetime, timedelta
from math import radians, cos, sin, asin, sqrt
from models import (
    db, Faculty, Program, ProgramCoordinator, FacultyAttendance,
    AttendanceSession, ClassSchedule, Subject, Section, WorkDiary,
    Holiday, AttendanceRecord, Student, FeeReceipt
)
from auth import coordinator_required, get_current_user


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in meters"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371000  # Earth radius in meters


def get_accuracy_level(accuracy):
    """Determine GPS accuracy level"""
    if accuracy is None or accuracy == 0:
        return 'unknown'
    if accuracy <= 10:
        return 'high'
    elif accuracy <= 30:
        return 'medium'
    else:
        return 'low'


def register_department_routes(app):
    """Register department management routes"""
    
    @app.route('/faculty/department')
    @coordinator_required
    def faculty_department():
        """My Department tab - main view"""
        current_user = get_current_user()
        faculty = current_user.faculty
        
        # Get coordinator assignments
        assignments = ProgramCoordinator.query.filter_by(
            faculty_id=faculty.faculty_id,
            is_deleted=False
        ).all()
        
        programs = [a.program for a in assignments]
        
        # Get selected program
        selected_program_id = request.args.get('program_id') or session.get('dept_program_id')
        if not selected_program_id and programs:
            selected_program_id = programs[0].program_id
            session['dept_program_id'] = selected_program_id
        
        selected_program = Program.query.get(selected_program_id) if selected_program_id else None
        
        # Check holiday
        today = date.today()
        holiday = Holiday.query.filter_by(holiday_date=today).first()
        
        return render_template('faculty_department.html',
                             programs=programs,
                             selected_program=selected_program,
                             is_holiday=holiday is not None,
                             holiday=holiday)
    
    @app.route('/api/faculty/department/faculty-attendance')
    @coordinator_required
    def dept_faculty_attendance():
        """API: Get faculty attendance for department"""
        current_user = get_current_user()
        program_id = request.args.get('program_id') or session.get('dept_program_id')
        
        if not program_id:
            return jsonify({'error': 'No program selected'}), 400
        
        # Verify access
        assignment = ProgramCoordinator.query.filter_by(
            faculty_id=current_user.faculty.faculty_id,
            program_id=program_id,
            is_deleted=False
        ).first()
        
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get faculties
        faculties = Faculty.query.filter_by(program_id=program_id, is_deleted=False).all()
        today = date.today()
        
        dept_lat, dept_lon = 12.9716, 77.5946  # Default location
        
        timings = []
        for fac in faculties:
            attendance = FacultyAttendance.query.filter_by(faculty_id=fac.faculty_id, date=today).first()
            
            if attendance:
                distance = None
                if attendance.check_in_latitude and attendance.check_in_longitude:
                    distance = calculate_distance(dept_lat, dept_lon, 
                                                 attendance.check_in_latitude, 
                                                 attendance.check_in_longitude)
                
                status = "Checked Out" if attendance.check_out_time else "In Department" if attendance.check_in_time else "Not Checked In"
                
                timings.append({
                    'faculty_id': fac.faculty_id,
                    'faculty_name': f"{fac.first_name} {fac.last_name}",
                    'check_in_time': attendance.check_in_time.strftime('%I:%M %p') if attendance.check_in_time else None,
                    'check_in_accuracy': attendance.check_in_accuracy,
                    'accuracy_level': get_accuracy_level(attendance.check_in_accuracy),
                    'check_out_time': attendance.check_out_time.strftime('%I:%M %p') if attendance.check_out_time else None,
                    'distance_from_dept': round(distance, 2) if distance else None,
                    'status': status,
                    'hours_worked': attendance.get_hours_worked()
                })
            else:
                timings.append({
                    'faculty_id': fac.faculty_id,
                    'faculty_name': f"{fac.first_name} {fac.last_name}",
                    'status': "Not Checked In",
                    'hours_worked': 0
                })
        
        return jsonify({'timings': timings})
    
    @app.route('/api/faculty/department/todays-classes')
    @coordinator_required
    def dept_todays_classes():
        """API: Get today's classes in department"""
        current_user = get_current_user()
        program_id = request.args.get('program_id') or session.get('dept_program_id')
        
        if not program_id:
            return jsonify({'error': 'No program selected'}), 400
        
        # Verify access
        assignment = ProgramCoordinator.query.filter_by(
            faculty_id=current_user.faculty.faculty_id,
            program_id=program_id,
            is_deleted=False
        ).first()
        
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403
        
        today = date.today()
        sections = Section.query.filter_by(program_id=program_id, is_deleted=False).all()
        section_ids = [s.section_id for s in sections]
        
        sessions = db.session.query(
            AttendanceSession, ClassSchedule, Subject, Section, Faculty
        ).join(
            ClassSchedule, AttendanceSession.schedule_id == ClassSchedule.schedule_id
        ).join(
            Subject, ClassSchedule.subject_id == Subject.subject_id
        ).join(
            Section, ClassSchedule.section_id == Section.section_id
        ).join(
            Faculty, ClassSchedule.faculty_id == Faculty.faculty_id
        ).filter(
            ClassSchedule.date == today,
            ClassSchedule.section_id.in_(section_ids),
            AttendanceSession.is_deleted == False
        ).all()
        
        classes = []
        for session, schedule, subject, section, faculty in sessions:
            records = AttendanceRecord.query.filter_by(
                attendance_session_id=session.attendance_session_id
            ).all()
            present = sum(1 for r in records if r.status == 'present')
            total = len(records)
            
            classes.append({
                'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                'subject_name': subject.subject_name,
                'section_name': section.section_name,
                'start_time': schedule.start_time.strftime('%I:%M %p') if schedule.start_time else None,
                'topic': session.topic_taught or 'N/A',
                'present_count': present,
                'total_count': total,
                'attendance_percentage': round((present / total * 100), 1) if total > 0 else 0
            })
        
        return jsonify({'classes': classes})
    
    @app.route('/api/faculty/department/summary')
    @coordinator_required
    def dept_summary():
        """API: Get department summary including fees"""
        current_user = get_current_user()
        program_id = request.args.get('program_id') or session.get('dept_program_id')
        
        if not program_id:
            return jsonify({'error': 'No program selected'}), 400
        
        # Verify access
        assignment = ProgramCoordinator.query.filter_by(
            faculty_id=current_user.faculty.faculty_id,
            program_id=program_id,
            is_deleted=False
        ).first()
        
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get students in program
        sections = Section.query.filter_by(program_id=program_id, is_deleted=False).all()
        section_ids = [s.section_id for s in sections]
        students = Student.query.filter(Student.section_id.in_(section_ids), Student.is_deleted == False).all()
        
        total_students = len(students)
        
        # Calculate fees
        total_fees_collected = 0
        total_fees_pending = 0
        
        for student in students:
            receipts = FeeReceipt.query.filter_by(student_id=student.student_id, is_deleted=False).all()
            collected = sum(r.amount_paid for r in receipts)
            total_fees_collected += collected
            
            # Get expected fees (simplified - you may need to adjust based on your fee structure)
            # This is a placeholder - integrate with your actual fee calculation
            expected = 50000  # Example amount
            pending = max(0, expected - collected)
            total_fees_pending += pending
        
        return jsonify({
            'total_students': total_students,
            'fees_collected': total_fees_collected,
            'fees_pending': total_fees_pending,
            'sections_count': len(sections)
        })
