"""
Coordinator Dashboard Routes
Handles all coordinator-specific functionality including:
- Dashboard view with faculty timings and work diaries
- GPS distance calculation
- Holiday detection
- Department-specific data filtering
"""

from flask import render_template, request, jsonify, session
from datetime import date, datetime, timedelta
from math import radians, cos, sin, asin, sqrt
from models import (
    db, Faculty, Program, ProgramCoordinator, FacultyAttendance,
    AttendanceSession, ClassSchedule, Subject, Section, WorkDiary,
    Holiday, AttendanceRecord
)
from auth import coordinator_required, get_current_user


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of earth in meters
    return c * r


def get_accuracy_level(accuracy):
    """
    Determine accuracy level based on GPS accuracy in meters
    Returns: 'high', 'medium', or 'low'
    """
    if accuracy is None:
        return 'unknown'
    if accuracy <= 10:
        return 'high'
    elif accuracy <= 30:
        return 'medium'
    else:
        return 'low'


def register_coordinator_routes(app):
    """Register all coordinator routes with the Flask app"""
    
    @app.route('/coordinator/dashboard')
    @coordinator_required
    def coordinator_dashboard():
        """
        Main coordinator dashboard
        Shows faculty timings and work diaries for assigned programs
        """
        current_user = get_current_user()
        faculty = current_user.faculty
        
        # Get all programs where this faculty is coordinator
        coordinator_assignments = ProgramCoordinator.query.filter_by(
            faculty_id=faculty.faculty_id,
            is_deleted=False
        ).all()
        
        programs = [assignment.program for assignment in coordinator_assignments]
        
        # If coordinator of multiple programs, get selected program from session
        selected_program_id = request.args.get('program_id') or session.get('selected_program_id')
        
        if not selected_program_id and programs:
            selected_program_id = programs[0].program_id
            session['selected_program_id'] = selected_program_id
        
        selected_program = None
        if selected_program_id:
            selected_program = Program.query.get(selected_program_id)
        
        # Check if today is a holiday
        today = date.today()
        holiday = Holiday.query.filter_by(holiday_date=today).first()
        
        return render_template('coordinator_dashboard.html',
                             programs=programs,
                             selected_program=selected_program,
                             is_holiday=holiday is not None,
                             holiday=holiday)
    
    @app.route('/coordinator/select-department', methods=['POST'])
    @coordinator_required
    def coordinator_select_department():
        """Handle department/program selection"""
        program_id = request.json.get('program_id')
        session['selected_program_id'] = program_id
        return jsonify({'success': True})
    
    @app.route('/api/coordinator/faculty-timings')
    @coordinator_required
    def coordinator_faculty_timings():
        """
        API endpoint to get faculty attendance timings for the selected program
        Includes GPS data and distance calculations
        """
        current_user = get_current_user()
        program_id = request.args.get('program_id') or session.get('selected_program_id')
        
        if not program_id:
            return jsonify({'error': 'No program selected'}), 400
        
        # Verify coordinator has access to this program
        assignment = ProgramCoordinator.query.filter_by(
            faculty_id=current_user.faculty.faculty_id,
            program_id=program_id,
            is_deleted=False
        ).first()
        
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all faculties in this program's department
        program = Program.query.get(program_id)
        faculties = Faculty.query.filter_by(
            program_id=program_id,
            is_deleted=False
        ).all()
        
        # Get today's attendance for these faculties
        today = date.today()
        timings = []
        
        # Get department location (from college config or program)
        # For now, using a default location - should be configurable
        dept_lat = 12.9716  # Example: Bangalore
        dept_lon = 77.5946
        
        for faculty in faculties:
            attendance = FacultyAttendance.query.filter_by(
                faculty_id=faculty.faculty_id,
                date=today
            ).first()
            
            if attendance:
                # Calculate distance from department
                distance = None
                if attendance.check_in_latitude and attendance.check_in_longitude:
                    distance = calculate_distance(
                        dept_lat, dept_lon,
                        attendance.check_in_latitude,
                        attendance.check_in_longitude
                    )
                
                # Determine status
                if attendance.check_out_time:
                    status = "Checked Out"
                elif attendance.check_in_time:
                    status = "In Department"
                else:
                    status = "Not Checked In"
                
                timings.append({
                    'faculty_id': faculty.faculty_id,
                    'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                    'check_in_time': attendance.check_in_time.strftime('%I:%M %p') if attendance.check_in_time else None,
                    'check_in_latitude': attendance.check_in_latitude,
                    'check_in_longitude': attendance.check_in_longitude,
                    'check_in_accuracy': attendance.check_in_accuracy,
                    'accuracy_level': get_accuracy_level(attendance.check_in_accuracy),
                    'check_out_time': attendance.check_out_time.strftime('%I:%M %p') if attendance.check_out_time else None,
                    'distance_from_dept': round(distance, 2) if distance else None,
                    'status': status,
                    'hours_worked': attendance.get_hours_worked()
                })
            else:
                timings.append({
                    'faculty_id': faculty.faculty_id,
                    'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                    'check_in_time': None,
                    'check_in_latitude': None,
                    'check_in_longitude': None,
                    'check_in_accuracy': None,
                    'accuracy_level': 'unknown',
                    'check_out_time': None,
                    'distance_from_dept': None,
                    'status': "Not Checked In",
                    'hours_worked': 0
                })
        
        return jsonify({'timings': timings})
    
    @app.route('/api/coordinator/faculty-diary')
    @coordinator_required
    def coordinator_faculty_diary():
        """
        API endpoint to get today's faculty work diary/classes for the selected program
        """
        current_user = get_current_user()
        program_id = request.args.get('program_id') or session.get('selected_program_id')
        
        if not program_id:
            return jsonify({'error': 'No program selected'}), 400
        
        # Verify coordinator has access to this program
        assignment = ProgramCoordinator.query.filter_by(
            faculty_id=current_user.faculty.faculty_id,
            program_id=program_id,
            is_deleted=False
        ).first()
        
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get today's date
        today = date.today()
        
        # Get all attendance sessions for today in this program's sections
        program = Program.query.get(program_id)
        sections = Section.query.filter_by(program_id=program_id, is_deleted=False).all()
        section_ids = [s.section_id for s in sections]
        
        # Query attendance sessions for today
        sessions = db.session.query(
            AttendanceSession,
            ClassSchedule,
            Subject,
            Section,
            Faculty
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
        
        diary_entries = []
        for session, schedule, subject, section, faculty in sessions:
            # Count present/absent
            records = AttendanceRecord.query.filter_by(
                attendance_session_id=session.attendance_session_id
            ).all()
            present_count = sum(1 for r in records if r.status == 'present')
            total_count = len(records)
            
            # Calculate duration
            duration = 0
            if schedule.start_time and schedule.end_time:
                start_dt = datetime.combine(today, schedule.start_time)
                end_dt = datetime.combine(today, schedule.end_time)
                duration = (end_dt - start_dt).total_seconds() / 3600
            
            diary_entries.append({
                'session_id': session.attendance_session_id,
                'faculty_id': faculty.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                'subject_name': subject.subject_name,
                'subject_code': subject.subject_code,
                'section_name': section.section_name,
                'start_time': schedule.start_time.strftime('%I:%M %p') if schedule.start_time else None,
                'end_time': schedule.end_time.strftime('%I:%M %p') if schedule.end_time else None,
                'duration': round(duration, 2),
                'topic': session.topic_taught or 'N/A',
                'present_count': present_count,
                'total_count': total_count,
                'attendance_percentage': round((present_count / total_count * 100), 1) if total_count > 0 else 0
            })
        
        return jsonify({'diary_entries': diary_entries})
    
    @app.route('/api/coordinator/faculty/<faculty_id>/details')
    @coordinator_required
    def coordinator_faculty_details(faculty_id):
        """
        Get detailed information about a faculty's today's activities
        Including topics taught and student counts
        """
        current_user = get_current_user()
        
        # Get today's date
        today = date.today()
        
        # Get all sessions for this faculty today
        sessions = db.session.query(
            AttendanceSession,
            ClassSchedule,
            Subject,
            Section
        ).join(
            ClassSchedule, AttendanceSession.schedule_id == ClassSchedule.schedule_id
        ).join(
            Subject, ClassSchedule.subject_id == Subject.subject_id
        ).join(
            Section, ClassSchedule.section_id == Section.section_id
        ).filter(
            ClassSchedule.faculty_id == faculty_id,
            ClassSchedule.date == today,
            AttendanceSession.is_deleted == False
        ).all()
        
        classes = []
        for session, schedule, subject, section in sessions:
            # Count students
            records = AttendanceRecord.query.filter_by(
                attendance_session_id=session.attendance_session_id
            ).all()
            present_count = sum(1 for r in records if r.status == 'present')
            total_count = len(records)
            
            classes.append({
                'subject_name': subject.subject_name,
                'section_name': section.section_name,
                'topic': session.topic_taught or 'N/A',
                'start_time': schedule.start_time.strftime('%I:%M %p') if schedule.start_time else None,
                'present_count': present_count,
                'total_count': total_count,
                'attendance_percentage': round((present_count / total_count * 100), 1) if total_count > 0 else 0
            })
        
        faculty = Faculty.query.get(faculty_id)
        
        return jsonify({
            'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else 'Unknown',
            'classes': classes
        })
