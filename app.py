"""
Flask PWA Application - Main Entry Point
This is a Progressive Web App (PWA) built with Flask that can be installed on mobile devices.
The app uses SQLite database and is designed with a mobile-first approach.

Project Structure:
- app.py: Main application file with routes
- models.py: Database models and schema
- config.py: Configuration settings
- routes/: Modular route blueprints (for students to work on)
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import os

# Import configuration
from config import Config

# Import database instance from models
from models import db

# Initialize Flask application
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Configure session for PWA persistence (for localhost/development)
app.config['SESSION_COOKIE_NAME'] = 'bca_bub_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Use Lax for local development
app.config['SESSION_COOKIE_SECURE'] = False  # False for HTTP (local), True for HTTPS (production)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000  # 30 days in seconds

# Create instance folder if it doesn't exist
instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Initialize database with app
db.init_app(app)

# Import models after db initialization
from models import (
    User, Role, Faculty, Student, Program, Section,
    Semester, Subject, SubjectAllocation, ClassSchedule,
    AttendanceSession, AttendanceRecord, Test, TestResult,
    WorkDiary, ImportLog, Unit, Chapter, Concept
)

# Import authentication utilities
from auth import (
    login_required, admin_required, faculty_required, role_required,
    login_user, logout_user, get_current_user, hash_password, verify_password,
    can_edit_work_diary, can_approve_work_diary, can_view_all_diaries
)


# ============================================
# Routes
# ============================================

# ============================================
# Authentication Routes
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page and handler
    """
    # If already logged in, redirect to appropriate dashboard
    current_user = get_current_user()
    if current_user:
        # Check if user is admin
        if current_user.role and current_user.role.role_name.lower() == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_active=True, is_deleted=False).first()
        
        if user and verify_password(user.password_hash, password):
            login_user(user)
            
            # Redirect to next page or appropriate dashboard based on role
            next_page = request.args.get('next')
            # Validate next_page to prevent open redirect
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            # Admin users go to admin dashboard
            if user.role and user.role.role_name.lower() == 'admin':
                return redirect(url_for('admin_dashboard'))
            
            # Student users go to student dashboard
            if user.role and user.role.role_name.lower() == 'student':
                return redirect(url_for('student_dashboard'))
            
            # Parent users also go to student dashboard (to view their child's data)
            if user.role and user.role.role_name.lower() == 'parent':
                return redirect(url_for('student_dashboard'))
            
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')



@app.route('/logout')
def logout():
    """
    User logout handler
    """
    logout_user()
    return redirect(url_for('login'))


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    """
    Student Dashboard - Shows student's subjects and attendance
    Also used for parent view
    """
    current_user = get_current_user()
    
    if not current_user:
        return redirect(url_for('login'))
    
    # Get the student record for this user
    student = None
    subjects = []
    attendance_percentage = 0
    
    if current_user.role.role_name.lower() == 'student':
        student = Student.query.filter_by(user_id=current_user.user_id, is_deleted=False).first()
    elif current_user.role.role_name.lower() == 'parent':
        # For parent, find the linked student (username is roll_number_parent)
        roll_number = current_user.username.replace('_parent', '')
        student = Student.query.filter_by(roll_number=roll_number, is_deleted=False).first()
    
    if student:
        # Get subjects for this student's section
        if student.section_id:
            # Get subjects allocated to the student's section
            allocations = SubjectAllocation.query.filter_by(
                section_id=student.section_id, 
                is_deleted=False
            ).all()
            subjects = [alloc.subject for alloc in allocations if alloc.subject and not alloc.subject.is_deleted]
        elif student.program_id:
            # Fallback: Get subjects for the student's program
            subjects = Subject.query.filter_by(
                program_id=student.program_id, 
                is_deleted=False
            ).all()
        
        # Calculate overall attendance (placeholder - can be enhanced)
        total_sessions = AttendanceSession.query.count()
        if total_sessions > 0:
            present_count = AttendanceRecord.query.filter_by(
                student_id=student.student_id,
                status='present'
            ).count()
            attendance_percentage = round((present_count / total_sessions) * 100) if total_sessions else 0
    
    return render_template('student_dashboard.html',
                         current_user=current_user,
                         student=student,
                         subjects=subjects,
                         attendance_percentage=attendance_percentage)


@app.route('/')
@login_required
def index():
    """
    Home page - displays main dashboard
    Shows different data based on user role
    """
    current_user = get_current_user()
    
    # If user is not logged in properly, redirect to login
    if not current_user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('login'))
    
    # Common stats
    faculty_count = Faculty.query.filter_by(is_deleted=False).count()
    student_count = Student.query.filter_by(is_deleted=False).count()
    
    # Role-specific data
    if current_user.role and current_user.role.role_name == 'faculty':
        # Get faculty's own work diaries
        faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
        if faculty_record:
            pending_diaries = WorkDiary.query.filter_by(
                faculty_id=faculty_record.faculty_id,
                status='draft',
                is_deleted=False
            ).count()
        else:
            pending_diaries = 0
    else:
        pending_diaries = 0
    
    return render_template('index.html', 
                         faculty_count=faculty_count,
                         student_count=student_count,
                         pending_diaries=pending_diaries,
                         current_user=current_user)


@app.route('/manifest.json')
def manifest():
    """
    Serve PWA manifest file for app installation
    """
    return app.send_static_file('manifest.json')


@app.route('/service-worker.js')
def service_worker():
    """
    Serve service worker JavaScript file for PWA functionality
    """
    return app.send_static_file('service-worker.js')


# ============================================
# Public Pages (No Authentication Required)
# ============================================

@app.route('/welcome')
def public_home():
    """
    Public landing page showcasing the department
    Accessible without login
    """
    faculty_count = Faculty.query.filter_by(is_deleted=False).count()
    student_count = Student.query.filter_by(is_deleted=False).count()
    
    return render_template('public_home.html',
                         faculty_count=faculty_count,
                         student_count=student_count)


@app.route('/admissions')
def admissions():
    """
    Admission process page
    Shows eligibility, steps, dates, and contact info
    """
    return render_template('admissions.html')


@app.route('/about')
def about():
    """
    About us page
    Shows department info, team members, and history
    """
    return render_template('about.html')


@app.route('/faculty')
def faculty():
    """
    Display all faculty members
    TODO for students: Add pagination, search, filters
    """
    faculties = Faculty.query.filter_by(is_deleted=False).all()
    return render_template('faculty.html', faculties=faculties)


@app.route('/students')
def students():
    """
    Display all students
    TODO for students: Add pagination, search, filters by section/program
    """
    students = Student.query.filter_by(is_deleted=False).limit(50).all()
    return render_template('students.html', students=students)


@app.route('/attendance')
def attendance():
    """
    Display attendance management page
    TODO for students: Implement full attendance taking workflow
    """
    # Get recent attendance sessions
    sessions = AttendanceSession.query.order_by(AttendanceSession.taken_at.desc()).limit(10).all()
    return render_template('attendance.html', sessions=sessions)


# ============================================
# API Endpoints - For Students to Expand
# ============================================

@app.route('/api/faculty', methods=['GET', 'POST'])
def api_faculty():
    """
    API endpoint for faculty management
    GET: List all faculty
    POST: Create new faculty
    TODO for students: Add filtering, pagination, validation
    """
    if request.method == 'POST':
        data = request.get_json()
        try:
            # This is simplified - students should add proper validation
            new_faculty = Faculty(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone')
            )
            db.session.add(new_faculty)
            db.session.commit()
            return jsonify({'success': True, 'faculty': new_faculty.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # GET request
    faculties = Faculty.query.filter_by(is_deleted=False).all()
    return jsonify([f.to_dict() for f in faculties])


@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    """
    API endpoint for student management
    GET: List all students
    POST: Create new student
    TODO for students: Add validation, handle user creation, assign to sections
    """
    if request.method == 'POST':
        data = request.get_json()
        try:
            # Simplified version - students should expand this
            new_student = Student(
                usn=data.get('usn'),
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone')
            )
            db.session.add(new_student)
            db.session.commit()
            return jsonify({'success': True, 'student': new_student.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # GET request
    students = Student.query.filter_by(is_deleted=False).limit(100).all()
    return jsonify([s.to_dict() for s in students])


@app.route('/api/attendance/session', methods=['POST'])
@faculty_required
def api_create_attendance_session():
    """
    Create a new attendance session and automatically generate work diary entry
    TODO for students: Implement full attendance workflow
    - Validate schedule exists
    - Auto-populate student list
    - Handle bulk status updates
    """
    data = request.get_json()
    try:
        current_user = get_current_user()
        
        # Create attendance session
        session = AttendanceSession(
            schedule_id=data.get('schedule_id'),
            taken_by_user_id=current_user.user_id,
            status='draft'
        )
        db.session.add(session)
        db.session.flush()  # Get session ID without committing
        
        # Auto-generate work diary entry if schedule exists
        if session.schedule:
            auto_create_work_diary_from_attendance(session)
        
        db.session.commit()
        return jsonify({'success': True, 'session': session.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================
# Work Diary Routes
# ============================================

@app.route('/work-diary')
@faculty_required
def work_diary_list():
    """
    Display work diary entries
    Faculty see their own, Admin/HOD see all
    """
    current_user = get_current_user()
    
    if can_view_all_diaries():
        # Admin/HOD view all diaries
        diaries = WorkDiary.query.filter_by(is_deleted=False).order_by(
            WorkDiary.date.desc(), WorkDiary.start_time.desc()
        ).limit(50).all()
    else:
        # Faculty view only their own
        faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
        if faculty_record:
            diaries = WorkDiary.query.filter_by(
                faculty_id=faculty_record.faculty_id,
                is_deleted=False
            ).order_by(WorkDiary.date.desc(), WorkDiary.start_time.desc()).limit(50).all()
        else:
            diaries = []
    
    return render_template('work_diary.html', diaries=diaries)


@app.route('/work-diary/create', methods=['GET', 'POST'])
@faculty_required
def create_work_diary():
    """
    Create new work diary entry (for non-class activities)
    """
    if request.method == 'POST':
        return handle_work_diary_creation()
    
    # GET - show form
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    return render_template('work_diary_form.html', 
                         faculty=faculty_record,
                         action='create')


@app.route('/work-diary/<diary_id>/edit', methods=['GET', 'POST'])
@faculty_required
def edit_work_diary(diary_id):
    """
    Edit existing work diary entry
    """
    diary = WorkDiary.query.get_or_404(diary_id)
    
    if not can_edit_work_diary(diary):
        return jsonify({'error': 'Permission denied'}), 403
    
    if request.method == 'POST':
        return handle_work_diary_update(diary)
    
    return render_template('work_diary_form.html', 
                         diary=diary,
                         action='edit')


@app.route('/api/work-diary', methods=['GET', 'POST'])
@faculty_required
def api_work_diary():
    """
    API endpoint for work diary management
    GET: List work diaries (filtered by permissions)
    POST: Create new work diary entry
    """
    if request.method == 'POST':
        data = request.get_json()
        try:
            # Create work diary entry
            diary = create_work_diary_entry(data)
            return jsonify({'success': True, 'diary': diary.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # GET - retrieve diaries
    current_user = get_current_user()
    
    if can_view_all_diaries():
        diaries = WorkDiary.query.filter_by(is_deleted=False).order_by(
            WorkDiary.date.desc()
        ).limit(100).all()
    else:
        faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
        if faculty_record:
            diaries = WorkDiary.query.filter_by(
                faculty_id=faculty_record.faculty_id,
                is_deleted=False
            ).order_by(WorkDiary.date.desc()).limit(100).all()
        else:
            diaries = []
    
    return jsonify([d.to_dict() for d in diaries])


@app.route('/api/work-diary/<diary_id>', methods=['GET', 'PUT', 'DELETE'])
@faculty_required
def api_work_diary_detail(diary_id):
    """
    API endpoint for individual work diary operations
    """
    diary = WorkDiary.query.get_or_404(diary_id)
    
    if request.method == 'GET':
        return jsonify(diary.to_dict())
    
    elif request.method == 'PUT':
        if not can_edit_work_diary(diary):
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        try:
            update_work_diary_entry(diary, data)
            return jsonify({'success': True, 'diary': diary.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        if not can_edit_work_diary(diary):
            return jsonify({'error': 'Permission denied'}), 403
        
        try:
            diary.is_deleted = True
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/work-diary/<diary_id>/submit', methods=['POST'])
@faculty_required
def submit_work_diary(diary_id):
    """
    Submit work diary entry for approval
    """
    diary = WorkDiary.query.get_or_404(diary_id)
    
    if not can_edit_work_diary(diary):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        diary.status = 'submitted'
        diary.submitted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Diary submitted for approval'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/work-diary/<diary_id>/approve', methods=['POST'])
@role_required('admin', 'hod')
def approve_work_diary(diary_id):
    """
    Approve work diary entry (Admin/HOD only)
    """
    diary = WorkDiary.query.get_or_404(diary_id)
    current_user = get_current_user()
    
    data = request.get_json()
    
    try:
        diary.status = 'approved'
        diary.approved_by = current_user.user_id
        diary.approved_at = datetime.utcnow()
        diary.approval_remarks = data.get('remarks', '')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Diary approved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/work-diary/<diary_id>/reject', methods=['POST'])
@role_required('admin', 'hod')
def reject_work_diary(diary_id):
    """
    Reject work diary entry (Admin/HOD only)
    """
    diary = WorkDiary.query.get_or_404(diary_id)
    current_user = get_current_user()
    
    data = request.get_json()
    
    try:
        diary.status = 'rejected'
        diary.approved_by = current_user.user_id
        diary.approved_at = datetime.utcnow()
        diary.approval_remarks = data.get('remarks', 'Entry rejected')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Diary rejected'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================
# Admin Management Routes
# ============================================

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    from models import Unit, Chapter, Concept
    
    faculty_count = Faculty.query.filter_by(is_deleted=False).count()
    student_count = Student.query.filter_by(is_deleted=False).count()
    subject_count = Subject.query.filter_by(is_deleted=False).count()
    section_count = Section.query.filter_by(is_deleted=False).count()
    
    return render_template('admin_dashboard.html',
                         faculty_count=faculty_count,
                         student_count=student_count,
                         subject_count=subject_count,
                         section_count=section_count)


# ---------------------------------------------
# Faculty Management Routes
# ---------------------------------------------

@app.route('/admin/faculty')
@admin_required
def admin_faculty():
    """List all faculty with their subjects"""
    faculty_list = Faculty.query.filter_by(is_deleted=False).all()
    
    # Get subjects for each faculty
    for faculty in faculty_list:
        allocations = SubjectAllocation.query.filter_by(
            faculty_id=faculty.faculty_id,
            is_deleted=False
        ).all()
        faculty.subjects = [alloc.subject for alloc in allocations if alloc.subject and not alloc.subject.is_deleted]
    
    return render_template('admin_faculty.html', faculty_list=faculty_list)


@app.route('/admin/faculty/add', methods=['GET', 'POST'])
@admin_required
def admin_faculty_add():
    """Add new faculty member"""
    if request.method == 'POST':
        try:
            # Get form data
            employee_id = request.form.get('employee_id')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            department = request.form.get('department')
            designation = request.form.get('designation')
            qualification = request.form.get('qualification')
            username = request.form.get('username')
            password = request.form.get('password')
            subject_ids = request.form.getlist('subjects')
            
            # Check if employee_id or username already exists
            existing_faculty = Faculty.query.filter_by(employee_id=employee_id).first()
            if existing_faculty:
                return render_template('admin_faculty_form.html', 
                                     subjects=Subject.query.filter_by(is_deleted=False).all(),
                                     error='Employee ID already exists')
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('admin_faculty_form.html',
                                     subjects=Subject.query.filter_by(is_deleted=False).all(),
                                     error='Username already exists')
            
            # Create user account
            from werkzeug.security import generate_password_hash
            faculty_role = Role.query.filter_by(role_name='faculty').first()
            
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role_id=faculty_role.role_id
            )
            db.session.add(new_user)
            db.session.flush()
            
            # Create faculty record
            new_faculty = Faculty(
                user_id=new_user.user_id,
                employee_id=employee_id,
                first_name=first_name,
                last_name=last_name,
                name=f"{first_name} {last_name}",
                email=email,
                phone=phone,
                department=department,
                designation=designation,
                qualification=qualification
            )
            db.session.add(new_faculty)
            db.session.flush()
            
            # Assign subjects
            for subject_id in subject_ids:
                allocation = SubjectAllocation(
                    subject_id=subject_id,
                    faculty_id=new_faculty.faculty_id,
                    section_id=None  # Can be assigned later
                )
                db.session.add(allocation)
            
            db.session.commit()
            return redirect(url_for('admin_faculty'))
            
        except Exception as e:
            db.session.rollback()
            return render_template('admin_faculty_form.html',
                                 subjects=Subject.query.filter_by(is_deleted=False).all(),
                                 error=str(e))
    
    # GET request
    subjects = Subject.query.filter_by(is_deleted=False).all()
    return render_template('admin_faculty_form.html', subjects=subjects)


@app.route('/admin/faculty/<faculty_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_faculty_edit(faculty_id):
    """Edit existing faculty member"""
    faculty = Faculty.query.get_or_404(faculty_id)
    
    if request.method == 'POST':
        try:
            faculty.first_name = request.form.get('first_name')
            faculty.last_name = request.form.get('last_name')
            faculty.name = f"{faculty.first_name} {faculty.last_name}"
            faculty.email = request.form.get('email')
            faculty.phone = request.form.get('phone')
            faculty.department = request.form.get('department')
            faculty.designation = request.form.get('designation')
            faculty.qualification = request.form.get('qualification')
            
            # Update subject allocations
            subject_ids = request.form.getlist('subjects')
            
            # Remove old allocations
            SubjectAllocation.query.filter_by(faculty_id=faculty_id).delete()
            
            # Add new allocations
            for subject_id in subject_ids:
                allocation = SubjectAllocation(
                    subject_id=subject_id,
                    faculty_id=faculty_id,
                    section_id=None
                )
                db.session.add(allocation)
            
            db.session.commit()
            return redirect(url_for('admin_faculty'))
            
        except Exception as e:
            db.session.rollback()
            subjects = Subject.query.filter_by(is_deleted=False).all()
            allocations = SubjectAllocation.query.filter_by(faculty_id=faculty_id).all()
            faculty_subject_ids = [a.subject_id for a in allocations]
            return render_template('admin_faculty_form.html', 
                                 faculty=faculty,
                                 subjects=subjects,
                                 faculty_subject_ids=faculty_subject_ids,
                                 error=str(e))
    
    # GET request
    subjects = Subject.query.filter_by(is_deleted=False).all()
    allocations = SubjectAllocation.query.filter_by(faculty_id=faculty_id).all()
    faculty_subject_ids = [a.subject_id for a in allocations]
    return render_template('admin_faculty_form.html', 
                         faculty=faculty,
                         subjects=subjects,
                         faculty_subject_ids=faculty_subject_ids)


@app.route('/api/admin/faculty/<faculty_id>', methods=['DELETE'])
@admin_required
def api_delete_faculty(faculty_id):
    """Delete faculty (soft delete)"""
    try:
        faculty = Faculty.query.get_or_404(faculty_id)
        faculty.is_deleted = True
        faculty.user.is_deleted = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ---------------------------------------------
# Student Management Routes
# ---------------------------------------------

@app.route('/admin/students')
@admin_required
def admin_students():
    """List all students"""
    students = Student.query.filter_by(is_deleted=False).all()
    programs = Program.query.filter_by(is_deleted=False).all()
    sections = Section.query.filter_by(is_deleted=False).all()
    
    total_students = len(students)
    sections_count = len(sections)
    programs_count = len(programs)
    
    return render_template('admin_students.html',
                         students=students,
                         programs=programs,
                         sections=sections,
                         total_students=total_students,
                         sections_count=sections_count,
                         programs_count=programs_count)


@app.route('/admin/students/add', methods=['GET', 'POST'])
@admin_required
def admin_student_add():
    """Add new student"""
    if request.method == 'POST':
        try:
            roll_number = request.form.get('roll_number')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            date_of_birth = request.form.get('date_of_birth')
            program_id = request.form.get('program_id')
            section_id = request.form.get('section_id')
            admission_year = request.form.get('admission_year')
            current_semester = request.form.get('current_semester')
            address = request.form.get('address')
            guardian_name = request.form.get('guardian_name')
            guardian_phone = request.form.get('guardian_phone')
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Check if roll_number or username exists
            existing_student = Student.query.filter_by(roll_number=roll_number).first()
            if existing_student:
                return render_template('admin_student_form.html',
                                     programs=Program.query.filter_by(is_deleted=False).all(),
                                     sections=Section.query.filter_by(is_deleted=False).all(),
                                     error='Roll number already exists')
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('admin_student_form.html',
                                     programs=Program.query.filter_by(is_deleted=False).all(),
                                     sections=Section.query.filter_by(is_deleted=False).all(),
                                     error='Username already exists')
            
            # Create user account
            from werkzeug.security import generate_password_hash
            student_role = Role.query.filter_by(role_name='student').first()
            
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role_id=student_role.role_id
            )
            db.session.add(new_user)
            db.session.flush()
            
            # Create student record
            new_student = Student(
                user_id=new_user.user_id,
                roll_number=roll_number,
                usn=roll_number,
                first_name=first_name,
                last_name=last_name,
                name=f"{first_name} {last_name}",
                email=email,
                phone=phone,
                date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None,
                program_id=program_id if program_id else None,
                section_id=section_id if section_id else None,
                admission_year=int(admission_year) if admission_year else None,
                current_semester=int(current_semester) if current_semester else None,
                address=address,
                guardian_name=guardian_name,
                guardian_phone=guardian_phone
            )
            db.session.add(new_student)
            db.session.commit()
            
            return redirect(url_for('admin_students'))
            
        except Exception as e:
            db.session.rollback()
            return render_template('admin_student_form.html',
                                 programs=Program.query.filter_by(is_deleted=False).all(),
                                 sections=Section.query.filter_by(is_deleted=False).all(),
                                 error=str(e))
    
    # GET request
    programs = Program.query.filter_by(is_deleted=False).all()
    sections = Section.query.filter_by(is_deleted=False).all()
    return render_template('admin_student_form.html', programs=programs, sections=sections)


@app.route('/admin/students/<student_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_student_edit(student_id):
    """Edit existing student"""
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            student.first_name = request.form.get('first_name')
            student.last_name = request.form.get('last_name')
            student.name = f"{student.first_name} {student.last_name}"
            student.email = request.form.get('email')
            student.phone = request.form.get('phone')
            
            date_of_birth = request.form.get('date_of_birth')
            if date_of_birth:
                student.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            
            program_id = request.form.get('program_id')
            student.program_id = program_id if program_id else None
            
            section_id = request.form.get('section_id')
            student.section_id = section_id if section_id else None
            
            admission_year = request.form.get('admission_year')
            student.admission_year = int(admission_year) if admission_year else None
            
            current_semester = request.form.get('current_semester')
            student.current_semester = int(current_semester) if current_semester else None
            
            student.address = request.form.get('address')
            student.guardian_name = request.form.get('guardian_name')
            student.guardian_phone = request.form.get('guardian_phone')
            
            db.session.commit()
            return redirect(url_for('admin_students'))
            
        except Exception as e:
            db.session.rollback()
            return render_template('admin_student_form.html',
                                 student=student,
                                 programs=Program.query.filter_by(is_deleted=False).all(),
                                 sections=Section.query.filter_by(is_deleted=False).all(),
                                 error=str(e))
    
    # GET request
    programs = Program.query.filter_by(is_deleted=False).all()
    sections = Section.query.filter_by(is_deleted=False).all()
    return render_template('admin_student_form.html',
                         student=student,
                         programs=programs,
                         sections=sections)


@app.route('/api/admin/students/<student_id>', methods=['DELETE'])
@admin_required
def api_delete_student(student_id):
    """Delete student (soft delete)"""
    try:
        student = Student.query.get_or_404(student_id)
        student.is_deleted = True
        student.user.is_deleted = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ---------------------------------------------
# Subject Management Routes (with Units/Chapters/Concepts)
# ---------------------------------------------

@app.route('/admin/subjects')
@admin_required
def admin_subjects():
    """List all subjects with hierarchy"""
    from models import Unit, Chapter, Concept
    
    subjects = Subject.query.filter_by(is_deleted=False).all()
    
    # Load full hierarchy for each subject
    for subject in subjects:
        subject.units = Unit.query.filter_by(subject_id=subject.subject_id, is_deleted=False).order_by(Unit.unit_number).all()
        for unit in subject.units:
            unit.chapters = Chapter.query.filter_by(unit_id=unit.unit_id, is_deleted=False).order_by(Chapter.chapter_number).all()
            for chapter in unit.chapters:
                chapter.concepts = Concept.query.filter_by(chapter_id=chapter.chapter_id, is_deleted=False).all()
    
    return render_template('admin_subjects.html', subjects=subjects)


@app.route('/admin/subjects/add', methods=['GET', 'POST'])
@admin_required
def admin_subject_add():
    """Add new subject"""
    if request.method == 'POST':
        try:
            subject_code = request.form.get('subject_code')
            subject_name = request.form.get('subject_name')
            description = request.form.get('description')
            program_id = request.form.get('program_id')
            semester_id = request.form.get('semester_id')
            credits = request.form.get('credits')
            subject_type = request.form.get('subject_type')
            total_hours = request.form.get('total_hours')
            
            # Check if subject code exists
            existing_subject = Subject.query.filter_by(subject_code=subject_code).first()
            if existing_subject:
                return render_template('admin_subject_form.html',
                                     programs=Program.query.filter_by(is_deleted=False).all(),
                                     error='Subject code already exists')
            
            new_subject = Subject(
                subject_code=subject_code,
                code=subject_code,
                subject_name=subject_name,
                description=description,
                program_id=program_id if program_id else None,
                semester_id=int(semester_id) if semester_id else None,
                credits=float(credits) if credits else 0,
                subject_type=subject_type,
                total_hours=int(total_hours) if total_hours else None
            )
            db.session.add(new_subject)
            db.session.commit()
            
            return redirect(url_for('admin_subjects'))
            
        except Exception as e:
            db.session.rollback()
            return render_template('admin_subject_form.html',
                                 programs=Program.query.filter_by(is_deleted=False).all(),
                                 error=str(e))
    
    # GET request
    programs = Program.query.filter_by(is_deleted=False).all()
    return render_template('admin_subject_form.html', programs=programs)


@app.route('/admin/subjects/<subject_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_subject_edit(subject_id):
    """Edit existing subject"""
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        try:
            subject.subject_name = request.form.get('subject_name')
            subject.description = request.form.get('description')
            
            program_id = request.form.get('program_id')
            subject.program_id = program_id if program_id else None
            
            semester_id = request.form.get('semester_id')
            subject.semester_id = int(semester_id) if semester_id else None
            
            credits = request.form.get('credits')
            subject.credits = float(credits) if credits else 0
            
            subject.subject_type = request.form.get('subject_type')
            
            total_hours = request.form.get('total_hours')
            subject.total_hours = int(total_hours) if total_hours else None
            
            db.session.commit()
            return redirect(url_for('admin_subjects'))
            
        except Exception as e:
            db.session.rollback()
            return render_template('admin_subject_form.html',
                                 subject=subject,
                                 programs=Program.query.filter_by(is_deleted=False).all(),
                                 error=str(e))
    
    # GET request
    programs = Program.query.filter_by(is_deleted=False).all()
    return render_template('admin_subject_form.html', subject=subject, programs=programs)


@app.route('/api/admin/subjects/<subject_id>', methods=['DELETE'])
@admin_required
def api_delete_subject(subject_id):
    """Delete subject (soft delete)"""
    try:
        subject = Subject.query.get_or_404(subject_id)
        subject.is_deleted = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# Unit/Chapter/Concept CRUD APIs
@app.route('/api/admin/units', methods=['POST'])
@admin_required
def api_create_unit():
    """Create a unit within a subject"""
    try:
        from models import Unit
        data = request.get_json()
        
        unit = Unit(
            subject_id=data['subject_id'],
            unit_number=data['unit_number'],
            unit_name=data['unit_name'],
            description=data.get('description')
        )
        db.session.add(unit)
        db.session.commit()
        return jsonify({'success': True, 'unit_id': unit.unit_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/units/<unit_id>', methods=['DELETE'])
@admin_required
def api_delete_unit(unit_id):
    """Delete unit (soft delete)"""
    try:
        from models import Unit
        unit = Unit.query.get_or_404(unit_id)
        unit.is_deleted = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/chapters', methods=['POST'])
@admin_required
def api_create_chapter():
    """Create a chapter within a unit"""
    try:
        from models import Chapter
        data = request.get_json()
        
        chapter = Chapter(
            unit_id=data['unit_id'],
            chapter_number=data['chapter_number'],
            chapter_name=data['chapter_name'],
            description=data.get('description')
        )
        db.session.add(chapter)
        db.session.commit()
        return jsonify({'success': True, 'chapter_id': chapter.chapter_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/chapters/<chapter_id>', methods=['DELETE'])
@admin_required
def api_delete_chapter(chapter_id):
    """Delete chapter (soft delete)"""
    try:
        from models import Chapter
        chapter = Chapter.query.get_or_404(chapter_id)
        chapter.is_deleted = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/concepts', methods=['POST'])
@admin_required
def api_create_concept():
    """Create a concept within a chapter"""
    try:
        from models import Concept
        data = request.get_json()
        
        concept = Concept(
            chapter_id=data['chapter_id'],
            concept_name=data['concept_name'],
            description=data.get('description')
        )
        db.session.add(concept)
        db.session.commit()
        return jsonify({'success': True, 'concept_id': concept.concept_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/concepts/<concept_id>', methods=['DELETE'])
@admin_required
def api_delete_concept(concept_id):
    """Delete concept (soft delete)"""
    try:
        from models import Concept
        concept = Concept.query.get_or_404(concept_id)
        concept.is_deleted = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ---------------------------------------------
# Batch/Section Management Routes
# ---------------------------------------------

@app.route('/admin/batches')
@admin_required
def admin_batches():
    """Manage programs and sections"""
    programs = Program.query.filter_by(is_deleted=False).all()
    
    # Get sections with student and schedule counts
    for program in programs:
        program.sections = Section.query.filter_by(program_id=program.program_id, is_deleted=False).all()
        for section in program.sections:
            section.student_count = Student.query.filter_by(section_id=section.section_id, is_deleted=False).count()
            section.schedule_count = ClassSchedule.query.filter_by(section_id=section.section_id, is_deleted=False).count()
    
    return render_template('admin_batches.html', programs=programs)


@app.route('/api/admin/programs', methods=['POST'])
@admin_required
def api_create_program():
    """Create a new program"""
    try:
        data = request.get_json()
        
        program = Program(
            program_code=data['program_code'],
            program_name=data['program_name'],
            name=data['program_name'],
            duration_years=int(data.get('duration_years', 3)),
            duration=int(data.get('duration_years', 3))
        )
        db.session.add(program)
        db.session.commit()
        return jsonify({'success': True, 'program_id': program.program_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/sections', methods=['POST'])
@admin_required
def api_create_section():
    """Create a new section"""
    try:
        data = request.get_json()
        
        section = Section(
            section_name=data['section_name'],
            program_id=data['program_id'],
            academic_year=data.get('academic_year'),
            current_semester=int(data['current_semester']) if data.get('current_semester') else None
        )
        db.session.add(section)
        db.session.commit()
        return jsonify({'success': True, 'section_id': section.section_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/sections/<section_id>', methods=['DELETE'])
@admin_required
def api_delete_section(section_id):
    """Delete section (soft delete)"""
    try:
        section = Section.query.get_or_404(section_id)
        section.is_deleted = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================
# Bulk Import Routes (Admin Only)
# ============================================

@app.route('/admin/import')
@admin_required
def admin_import():
    """
    Display bulk import interface for admin
    """
    try:
        recent_imports = ImportLog.query.order_by(ImportLog.created_at.desc()).limit(10).all()
    except Exception:
        # Handle case where old enum values exist in database
        recent_imports = []
    return render_template('admin_import.html', imports=recent_imports)


@app.route('/api/admin/import/template/<import_type>')
@admin_required
def download_import_template(import_type):
    """
    Download sample Excel template for import
    """
    import os
    from flask import send_file
    
    template_files = {
        'student': 'students_template.xlsx',
        'faculty': 'faculty_template.csv',
        'subject': 'subjects_template.csv',
        'schedule': 'schedules_template.csv'
    }
    
    if import_type not in template_files:
        return jsonify({'success': False, 'error': 'Invalid import type'}), 400
    
    template_path = os.path.join(app.root_path, 'sample_imports', template_files[import_type])
    
    if not os.path.exists(template_path):
        return jsonify({'success': False, 'error': 'Template not found'}), 404
    
    # Determine mimetype based on file extension
    if template_files[import_type].endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        mimetype = 'text/csv'
    
    return send_file(
        template_path,
        as_attachment=True,
        download_name=template_files[import_type],
        mimetype=mimetype
    )


@app.route('/api/admin/import', methods=['POST'])
@admin_required
def api_bulk_import():
    """
    Handle bulk data import from CSV/Excel files
    Supports: students, faculty, subjects, schedules
    """
    current_user = get_current_user()
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    import_type = request.form.get('import_type')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not import_type:
        return jsonify({'success': False, 'error': 'Import type not specified'}), 400
    
    # Allowed file extensions
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return jsonify({'success': False, 'error': 'Invalid file type. Use CSV or Excel'}), 400
    
    try:
        # Read file data
        import pandas as pd
        
        if file_ext == '.csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Process import based on type
        result = process_bulk_import(df, import_type, current_user, file.filename)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Import failed: {str(e)}'}), 400


# ============================================
# Database Initialization
# ============================================

def init_db():
    """
    Initialize the database - create all tables
    """
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Create default roles if they don't exist
        create_default_roles()
        print("✓ Default roles initialized!")


def create_default_roles():
    """
    Create default system roles
    Students can expand this to add more roles
    """
    default_roles = [
        {'role_name': 'admin', 'description': 'System Administrator'},
        {'role_name': 'hod', 'description': 'Head of Department'},
        {'role_name': 'faculty', 'description': 'Faculty Member'},
        {'role_name': 'student', 'description': 'Student'},
        {'role_name': 'parent', 'description': 'Parent/Guardian'},
    ]
    
    for role_data in default_roles:
        existing_role = Role.query.filter_by(role_name=role_data['role_name']).first()
        if not existing_role:
            role = Role(**role_data)
            db.session.add(role)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating roles: {e}")


# ============================================
# Work Diary Helper Functions
# ============================================

def auto_create_work_diary_from_attendance(attendance_session):
    """
    Automatically create work diary entry when attendance is taken
    """
    schedule = attendance_session.schedule
    if not schedule:
        return None
    
    # Generate diary number
    year = datetime.utcnow().year
    last_diary = WorkDiary.query.filter(
        WorkDiary.diary_number.like(f'WD-{year}-%')
    ).order_by(WorkDiary.diary_number.desc()).first()
    
    if last_diary:
        last_num = int(last_diary.diary_number.split('-')[-1])
        diary_num = f'WD-{year}-{last_num + 1:04d}'
    else:
        diary_num = f'WD-{year}-0001'
    
    # Determine activity type based on schedule
    activity_type = 'practical_class' if 'lab' in schedule.room_number.lower() else 'theory_class'
    
    # Count students present (assuming records exist)
    students_present = AttendanceRecord.query.filter_by(
        session_id=attendance_session.session_id,
        status='present'
    ).count()
    
    students_total = AttendanceRecord.query.filter_by(
        session_id=attendance_session.session_id
    ).count()
    
    # Create diary entry
    diary = WorkDiary(
        diary_number=diary_num,
        faculty_id=schedule.faculty_id,
        subject_id=schedule.subject_id,
        section_id=schedule.section.section_id if schedule.section else None,
        date=attendance_session.session_date or datetime.utcnow().date(),
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        activity_type=activity_type,
        attendance_session_id=attendance_session.session_id,
        students_present=students_present,
        students_total=students_total,
        status='draft'
    )
    
    db.session.add(diary)
    return diary


def create_work_diary_entry(data):
    """
    Create work diary entry from form/API data
    """
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    if not faculty_record:
        raise ValueError('Faculty record not found')
    
    # Generate diary number
    year = datetime.utcnow().year
    last_diary = WorkDiary.query.filter(
        WorkDiary.diary_number.like(f'WD-{year}-%')
    ).order_by(WorkDiary.diary_number.desc()).first()
    
    if last_diary:
        last_num = int(last_diary.diary_number.split('-')[-1])
        diary_num = f'WD-{year}-{last_num + 1:04d}'
    else:
        diary_num = f'WD-{year}-0001'
    
    # Parse time strings
    start_time = datetime.strptime(data['start_time'], '%H:%M').time() if isinstance(data.get('start_time'), str) else data.get('start_time')
    end_time = datetime.strptime(data['end_time'], '%H:%M').time() if isinstance(data.get('end_time'), str) else data.get('end_time')
    date = datetime.strptime(data['date'], '%Y-%m-%d').date() if isinstance(data.get('date'), str) else data.get('date')
    
    diary = WorkDiary(
        diary_number=diary_num,
        faculty_id=faculty_record.faculty_id,
        subject_id=data.get('subject_id'),
        section_id=data.get('section_id'),
        date=date,
        start_time=start_time,
        end_time=end_time,
        activity_type=data['activity_type'],
        students_present=data.get('students_present', 0),
        students_total=data.get('students_total', 0),
        activity_title=data.get('activity_title'),
        activity_description=data.get('activity_description'),
        topics_covered=data.get('topics_covered'),
        status='draft'
    )
    
    db.session.add(diary)
    db.session.commit()
    return diary


def update_work_diary_entry(diary, data):
    """
    Update existing work diary entry
    """
    # Only allow updates to draft/rejected entries
    if diary.status not in ['draft', 'rejected']:
        raise ValueError('Cannot edit approved or submitted entries')
    
    # Update fields
    if 'date' in data:
        diary.date = datetime.strptime(data['date'], '%Y-%m-%d').date() if isinstance(data['date'], str) else data['date']
    if 'start_time' in data:
        diary.start_time = datetime.strptime(data['start_time'], '%H:%M').time() if isinstance(data['start_time'], str) else data['start_time']
    if 'end_time' in data:
        diary.end_time = datetime.strptime(data['end_time'], '%H:%M').time() if isinstance(data['end_time'], str) else data['end_time']
    if 'activity_type' in data:
        diary.activity_type = data['activity_type']
    if 'subject_id' in data:
        diary.subject_id = data['subject_id']
    if 'section_id' in data:
        diary.section_id = data['section_id']
    if 'students_present' in data:
        diary.students_present = data['students_present']
    if 'students_total' in data:
        diary.students_total = data['students_total']
    if 'activity_title' in data:
        diary.activity_title = data['activity_title']
    if 'activity_description' in data:
        diary.activity_description = data['activity_description']
    if 'topics_covered' in data:
        diary.topics_covered = data['topics_covered']
    
    db.session.commit()
    return diary


def handle_work_diary_creation():
    """
    Handle POST request for creating work diary
    """
    try:
        data = {
            'date': request.form.get('date'),
            'start_time': request.form.get('start_time'),
            'end_time': request.form.get('end_time'),
            'activity_type': request.form.get('activity_type'),
            'subject_id': request.form.get('subject_id'),
            'section_id': request.form.get('section_id'),
            'students_present': int(request.form.get('students_present', 0)),
            'students_total': int(request.form.get('students_total', 0)),
            'activity_title': request.form.get('activity_title'),
            'activity_description': request.form.get('activity_description'),
            'topics_covered': request.form.get('topics_covered')
        }
        
        diary = create_work_diary_entry(data)
        return redirect(url_for('work_diary_list'))
    except Exception as e:
        return f"Error: {str(e)}", 400


def handle_work_diary_update(diary):
    """
    Handle POST request for updating work diary
    """
    try:
        data = {
            'date': request.form.get('date'),
            'start_time': request.form.get('start_time'),
            'end_time': request.form.get('end_time'),
            'activity_type': request.form.get('activity_type'),
            'subject_id': request.form.get('subject_id'),
            'section_id': request.form.get('section_id'),
            'students_present': int(request.form.get('students_present', 0)),
            'students_total': int(request.form.get('students_total', 0)),
            'activity_title': request.form.get('activity_title'),
            'activity_description': request.form.get('activity_description'),
            'topics_covered': request.form.get('topics_covered')
        }
        
        update_work_diary_entry(diary, data)
        return redirect(url_for('work_diary_list'))
    except Exception as e:
        return f"Error: {str(e)}", 400


def process_bulk_import(df, import_type, current_user, filename):
    """
    Process bulk import data from DataFrame
    Returns result dict with success/failure counts
    """
    import_log = ImportLog(
        import_type=import_type,
        imported_by=current_user.user_id,
        file_name=filename,
        total_rows=len(df),
        status='processing'
    )
    db.session.add(import_log)
    db.session.flush()
    
    success_count = 0
    error_count = 0
    errors = []
    
    try:
        if import_type == 'student':
            success_count, error_count, errors = import_students(df)
        elif import_type == 'faculty':
            success_count, error_count, errors = import_faculty(df)
        elif import_type == 'subject':
            success_count, error_count, errors = import_subjects(df)
        elif import_type == 'schedule':
            success_count, error_count, errors = import_schedules(df)
        else:
            raise ValueError(f'Unknown import type: {import_type}')
        
        # Update import log
        import_log.successful_rows = success_count
        import_log.failed_rows = error_count
        import_log.status = 'completed' if error_count == 0 else 'completed_with_errors'
        
        if errors:
            import_log.error_log = '\n'.join(errors[:50])  # Store first 50 errors
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Import completed: {success_count} succeeded, {error_count} failed',
            'successful': success_count,
            'failed': error_count,
            'errors': errors[:10]  # Return first 10 errors
        }
    
    except Exception as e:
        import_log.status = 'failed'
        import_log.error_log = str(e)
        db.session.commit()
        raise


def import_students(df):
    """
    Import students from DataFrame
    Creates User account for each student:
    - Username = roll_number (USN)
    - Password = date_of_birth (DDMMYYYY format)
    """
    import pandas as pd
    from auth import hash_password
    
    success_count = 0
    error_count = 0
    errors = []
    
    # Required columns (minimum)
    required_columns = ['roll_number', 'first_name', 'last_name', 'email', 'date_of_birth']
    
    # Validate columns
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f'Missing required columns: {", ".join(missing_cols)}')
    
    # Get student role
    student_role = Role.query.filter_by(role_name='student').first()
    if not student_role:
        raise ValueError('Student role not found in database')
    
    for idx, row in df.iterrows():
        try:
            roll_number = str(row['roll_number']).strip()
            
            # Check if student already exists
            existing = Student.query.filter_by(roll_number=roll_number).first()
            if existing:
                errors.append(f"Row {idx+2}: Student {roll_number} already exists")
                error_count += 1
                continue
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=roll_number).first()
            if existing_user:
                errors.append(f"Row {idx+2}: Username {roll_number} already exists")
                error_count += 1
                continue
            
            # Parse date of birth for password
            dob = row['date_of_birth']
            if pd.isna(dob):
                errors.append(f"Row {idx+2}: Date of birth is required for password generation")
                error_count += 1
                continue
            
            # Convert to date if string
            if isinstance(dob, str):
                try:
                    dob = pd.to_datetime(dob).date()
                except:
                    errors.append(f"Row {idx+2}: Invalid date format for date_of_birth")
                    error_count += 1
                    continue
            elif hasattr(dob, 'date'):
                dob = dob.date()
            
            # Password = DDMMYYYY format
            password = dob.strftime('%d%m%Y')
            
            # Create User account
            user = User(
                username=roll_number,
                password_hash=hash_password(password),
                email=str(row['email']).strip(),
                role_id=student_role.role_id,
                is_active=True
            )
            db.session.add(user)
            db.session.flush()  # Get user_id
            
            # Parse optional fields
            phone = row.get('phone', '')
            if pd.isna(phone):
                phone = None
            else:
                phone = str(phone).strip() if phone else None
            
            admission_year = row.get('admission_year')
            if pd.isna(admission_year) if hasattr(pd, 'isna') else admission_year is None:
                admission_year = None
            else:
                admission_year = int(admission_year)
            
            guardian_name = row.get('guardian_name', '')
            if pd.isna(guardian_name):
                guardian_name = None
            
            guardian_phone = row.get('guardian_phone', '')
            if pd.isna(guardian_phone):
                guardian_phone = None
            
            address = row.get('address', '')
            if pd.isna(address):
                address = None
            
            # Get program_id if provided
            program_id = None
            if 'program_code' in row and not pd.isna(row.get('program_code')):
                program = Program.query.filter_by(program_code=str(row['program_code']).strip()).first()
                if program:
                    program_id = program.program_id
            
            # Create Student record
            student = Student(
                user_id=user.user_id,
                roll_number=roll_number,
                first_name=str(row['first_name']).strip(),
                last_name=str(row['last_name']).strip(),
                email=str(row['email']).strip(),
                phone=phone,
                date_of_birth=dob,
                guardian_name=guardian_name,
                guardian_phone=str(guardian_phone).strip() if guardian_phone else None,
                address=address,
                admission_year=admission_year,
                program_id=program_id,
                status='active'
            )
            db.session.add(student)
            
            # Create Parent account with same credentials but parent role
            # Username: roll_number_parent (e.g., BCA2024001_parent)
            # Password: same as student (DOB in DDMMYYYY format)
            parent_role = Role.query.filter_by(role_name='parent').first()
            if parent_role:
                parent_username = f"{roll_number}_parent"
                existing_parent = User.query.filter_by(username=parent_username).first()
                if not existing_parent:
                    parent_email = f"parent_{row['email']}" if '@' in str(row['email']) else f"{roll_number}_parent@bcabub.edu"
                    parent_user = User(
                        username=parent_username,
                        password_hash=hash_password(password),  # Same password as student
                        email=parent_email,
                        role_id=parent_role.role_id,
                        is_active=True
                    )
                    db.session.add(parent_user)
            
            success_count += 1
            
        except Exception as e:
            print(f"[IMPORT ERROR] Row {idx+2}: {str(e)}")  # Debug logging
            import traceback
            traceback.print_exc()  # Print full stack trace
            errors.append(f"Row {idx+2}: {str(e)}")
            error_count += 1
    
    # Log summary
    print(f"[IMPORT COMPLETE] Success: {success_count}, Failed: {error_count}")
    if errors:
        print(f"[IMPORT ERRORS] {errors}")
    
    db.session.commit()
    return success_count, error_count, errors


def import_faculty(df):
    """Import faculty from DataFrame"""
    success_count = 0
    error_count = 0
    errors = []
    
    required_columns = ['employee_id', 'first_name', 'last_name', 'email']
    
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f'Missing required columns: {", ".join(missing_cols)}')
    
    for idx, row in df.iterrows():
        try:
            existing = Faculty.query.filter_by(employee_id=row['employee_id']).first()
            if existing:
                errors.append(f"Row {idx+2}: Faculty {row['employee_id']} already exists")
                error_count += 1
                continue
            
            faculty = Faculty(
                employee_id=row['employee_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone=row.get('phone'),
                designation=row.get('designation'),
                department=row.get('department')
            )
            db.session.add(faculty)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {idx+2}: {str(e)}")
            error_count += 1
    
    db.session.commit()
    return success_count, error_count, errors


def import_subjects(df):
    """Import subjects from DataFrame"""
    import pandas as pd
    
    success_count = 0
    error_count = 0
    errors = []
    
    required_columns = ['subject_code', 'subject_name', 'semester']
    
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f'Missing required columns: {", ".join(missing_cols)}')
    
    for idx, row in df.iterrows():
        try:
            existing = Subject.query.filter_by(subject_code=str(row['subject_code']).strip()).first()
            if existing:
                errors.append(f"Row {idx+2}: Subject {row['subject_code']} already exists")
                error_count += 1
                continue
            
            # Get credits, handle NaN
            credits_val = row.get('credits', 4) if not pd.isna(row.get('credits', 4)) else 4
            subject_type_val = row.get('subject_type', 'theory') if not pd.isna(row.get('subject_type', 'theory')) else 'theory'
            
            subject = Subject(
                subject_code=str(row['subject_code']).strip(),
                subject_name=str(row['subject_name']).strip(),
                semester_id=int(row['semester']),  # Use semester_id field
                credits=float(credits_val),
                subject_type=str(subject_type_val).strip()
            )
            db.session.add(subject)
            success_count += 1
            
        except Exception as e:
            print(f"[IMPORT ERROR] Row {idx+2}: {str(e)}")
            import traceback
            traceback.print_exc()
            errors.append(f"Row {idx+2}: {str(e)}")
            error_count += 1
    
    print(f"[IMPORT COMPLETE] Subjects - Success: {success_count}, Failed: {error_count}")
    if errors:
        print(f"[IMPORT ERRORS] {errors}")
    
    db.session.commit()
    return success_count, error_count, errors


def import_schedules(df):
    """Import class schedules from DataFrame"""
    success_count = 0
    error_count = 0
    errors = []
    
    required_columns = ['subject_code', 'faculty_employee_id', 'day_of_week', 'start_time', 'end_time', 'room_number']
    
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f'Missing required columns: {", ".join(missing_cols)}')
    
    for idx, row in df.iterrows():
        try:
            # Lookup subject and faculty
            subject = Subject.query.filter_by(subject_code=row['subject_code']).first()
            faculty = Faculty.query.filter_by(employee_id=row['faculty_employee_id']).first()
            
            if not subject:
                errors.append(f"Row {idx+2}: Subject {row['subject_code']} not found")
                error_count += 1
                continue
            
            if not faculty:
                errors.append(f"Row {idx+2}: Faculty {row['faculty_employee_id']} not found")
                error_count += 1
                continue
            
            schedule = ClassSchedule(
                subject_id=subject.subject_id,
                faculty_id=faculty.faculty_id,
                day_of_week=row['day_of_week'],
                start_time=row['start_time'],
                end_time=row['end_time'],
                room_number=row['room_number']
            )
            db.session.add(schedule)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {idx+2}: {str(e)}")
            error_count += 1
    
    db.session.commit()
    return success_count, error_count, errors


# ============================================
# Main Application Entry
# ============================================

if __name__ == '__main__':
    # Create database tables if they don't exist
    init_db()
    
    # Run the Flask application
    # debug=True for development, set to False in production
    print("\n" + "="*50)
    print("  BCA BUB Attendance System")
    print("  Mobile-First PWA Application")
    print("="*50)
    print("\n📱 Access the app at:")
    print("   • Local: http://localhost:5000")
    print("   • Mobile: http://YOUR_IP:5000")
    print("\n🔧 Running in DEBUG mode")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
