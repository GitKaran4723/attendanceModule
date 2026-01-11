from flask import Blueprint, render_template, request, jsonify, current_app
from models import db, Student, Subject, Section, Program, StudentSubjectEnrollment
from sqlalchemy import func
import uuid

enrollment_bp = Blueprint('enrollment', __name__)

@enrollment_bp.route('/admin/enrollment')
def admin_enrollment_page():
    programs = Program.query.all()
    # Assuming standard 8 semesters for now, or fetch from config
    semesters = range(1, 9) 
from flask import Blueprint, render_template, request, jsonify, current_app
from models import db, Student, Subject, Section, Program, StudentSubjectEnrollment
from sqlalchemy import func
import uuid
from auth import admin_required, login_required

enrollment_bp = Blueprint('enrollment', __name__)

@enrollment_bp.route('/admin/enrollment')
@admin_required
def admin_enrollment_page():
    programs = Program.query.all()
    # Assuming standard 8 semesters for now, or fetch from config
    semesters = range(1, 9) 
    return render_template('admin_enrollment.html', programs=programs, semesters=semesters)

@enrollment_bp.route('/api/admin/enrollment/data', methods=['GET'])
@admin_required
def get_enrollment_data():
    program_id = request.args.get('program_id')
    semester = request.args.get('semester')
    academic_year = request.args.get('academic_year')
    current_section_id = request.args.get('section_id') # Optional filter

    if not all([program_id, semester, academic_year]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # 1. Fetch Students
    # Logic: Fetch students in this Program + Semester
    # They might be in Core Sections.
    query = Student.query.join(Section).filter(
        Section.program_id == program_id,
        Section.current_semester == semester,
        Section.academic_year == academic_year,
        Student.is_deleted == False
    )
    
    if current_section_id:
        query = query.filter(Student.section_id == current_section_id)
        
    students = query.all()
    
    # 2. Fetch Elective Subjects for this Semester
    # Grouped by 'elective_group'
    subjects = Subject.query.filter(
        Subject.program_id == program_id,
        Subject.semester_id == semester,
        Subject.subject_category.in_(['elective', 'language', 'specialization'])
    ).all()
    
    # Structure subjects: { "Language II": [Sub1, Sub2], "Specialization": [SubA, SubB] }
    elective_groups = {}
    for sub in subjects:
        group = sub.elective_group or "Uncategorized Electives"
        if group not in elective_groups:
            elective_groups[group] = []
        elective_groups[group].append(sub.to_dict())

    # 3. Fetch Existing Enrollments
    # Map: student_id -> { group_name: subject_id }
    enrollments_map = {}
    student_ids = [s.student_id for s in students]
    
    if student_ids:
        existing_enrollments = StudentSubjectEnrollment.query.filter(
            StudentSubjectEnrollment.student_id.in_(student_ids),
            StudentSubjectEnrollment.academic_year == academic_year
        ).all()
        
        for record in existing_enrollments:
            if record.student_id not in enrollments_map:
                enrollments_map[record.student_id] = {}
            
            # Find which group this subject belongs to
            # We can find it from the 'subjects' list we queried earlier
            # Optimization: create a subject_id lookup
            subject_record = next((s for s in subjects if s.subject_id == record.subject_id), None)
            if subject_record:
                group = subject_record.elective_group or "Uncategorized Electives"
                enrollments_map[record.student_id][group] = record.subject_id

    # 4. Filter out groups that have no subjects (sanity check)
    final_groups = {k: v for k, v in elective_groups.items() if v}

    response_data = {
        'students': [{
            'student_id': s.student_id,
            'name': s.name,
            'usn': s.roll_number, # Assuming roll_number is USN or we use usn field
            'section': s.section.section_name if s.section else 'N/A',
            'enrollments': enrollments_map.get(s.student_id, {})
        } for s in students],
        'elective_groups': final_groups
    }

    return jsonify(response_data)

@enrollment_bp.route('/api/admin/enrollment/save', methods=['POST'])
@admin_required
def save_enrollments():
    data = request.json
    # Expected: 
    # { 
    #   "program_id": "...", "semester": 5, "academic_year": "...",
    #   "enrollments": [ { "student_id": "...", "subject_id": "..." }, ... ] 
    # }
    
    program_id = data.get('program_id')
    semester = data.get('semester')
    academic_year = data.get('academic_year')
    enrollments_list = data.get('enrollments', [])

    if not enrollments_list:
         return jsonify({'message': 'No changes to save'}), 200

    try:
        # Group enrollments by Subject to optimize "Virtual Section" creation
        # subject_id -> [student_ids]
        subject_buckets = {}
        for item in enrollments_list:
            sid = item['subject_id']
            if sid not in subject_buckets:
                subject_buckets[sid] = []
            subject_buckets[sid].append(item['student_id'])
            
        # For each subject, ensure Virtual Section exists
        for subject_id, student_ids in subject_buckets.items():
            # 1. Get/Create Virtual Section
            virtual_section = Section.query.filter_by(
                program_id=program_id,
                current_semester=semester,
                academic_year=academic_year,
                linked_subject_id=subject_id,
                is_elective=True
            ).first()
            
            if not virtual_section:
                # Need subject name for section name
                subject = Subject.query.get(subject_id)
                if not subject:
                    continue # Should not happen
                
                # Naming convention: "3rd Sem - Kannada via Section" or just "Kannada - 2024"
                # Better: "{SubjectName} ({Semester} Sem)"
                section_name = f"{subject.subject_name} ({semester} Sem) - {academic_year}"
                # Truncate if too long (64 char limit)
                section_name = section_name[:64]
                
                virtual_section = Section(
                    section_id=str(uuid.uuid4()),
                    # program_id=program_id, # Wait, Program ID?
                    # Virtual section might handle students from DIFFERENT sections 
                    # but usually same Program.
                    program_id=program_id, 
                    year_of_study=(int(semester)+1)//2, # approx
                    academic_year=academic_year,
                    current_semester=semester,
                    section_name=section_name,
                    is_elective=True,
                    linked_subject_id=subject_id,
                    is_deleted=False
                )
                db.session.add(virtual_section)
                db.session.flush() # Get ID
            
            # 2. Update Enrollments
            for stud_id in student_ids:
                # Check if enrollment exists
                existing = StudentSubjectEnrollment.query.filter_by(
                    student_id=stud_id,
                    subject_id=subject_id,
                    academic_year=academic_year
                ).first()
                
                if not existing:
                    new_enrollment = StudentSubjectEnrollment(
                        enrollment_id=str(uuid.uuid4()),
                        student_id=stud_id,
                        subject_id=subject_id,
                        section_id=virtual_section.section_id,
                        academic_year=academic_year,
                        semester=semester
                    )
                    db.session.add(new_enrollment)
                else:
                    # Update section_id if missing (migration fix)
                    if existing.section_id != virtual_section.section_id:
                        existing.section_id = virtual_section.section_id

        # What about REMOVAL? 
        # The UI should send the CURRENT state specific to a group.
        # Handling un-enrollment is complex if we only receive "selected" items.
        # For MVP, we presume this payload ADDS/UPDATES.
        # To handle removal, we would need to know which group we are saving for,
        # and remove any enrollments for that group that are NOT in the list.
        # But let's stick to "Add/Update" for now as per "Enrol electives" request.
        
        db.session.commit()
        return jsonify({'message': 'Enrollments saved successfully', 'sections_created': True})

        db.session.commit()
        return jsonify({'message': 'Enrollments saved successfully', 'sections_created': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================
# Subject-Wise Enrollment (New Request)
# ============================================

@enrollment_bp.route('/admin/subjects/<subject_id>/enroll-students')
@admin_required
def admin_subject_enrollment_page(subject_id):
    """
    Specific page to enroll students into ONE subject.
    """
    subject = Subject.query.filter_by(subject_id=subject_id).first_or_404()
    
    # 1. Fetch Students eligible for this subject's semester/program
    # Logic: Students in the same Program + Semester
    query = Student.query.join(Section).filter(
        Section.program_id == subject.program_id,
        Section.current_semester == subject.semester_id,
        Student.is_deleted == False
    )
    all_students = query.all()
    
    # 2. Fetch existing enrollments for this subject
    # This helps us separate "Enrolled" vs "Available"
    existing_enrollments = StudentSubjectEnrollment.query.filter_by(
        subject_id=subject_id,
        semester=subject.semester_id
        # academic_year? We should probably match current section's AY
    ).all()
    
    enrolled_student_ids = {e.student_id for e in existing_enrollments}
    
    # 3. Partition students
    available_students = []
    enrolled_students = []
    
    for student in all_students:
        if student.student_id in enrolled_student_ids:
            # Find the enrollment record
            enrollment = next(e for e in existing_enrollments if e.student_id == student.student_id)
            enrolled_students.append({
                'student': student,
                'enrollment': enrollment
            })
        else:
            available_students.append(student)
            
    return render_template('admin_enroll_students.html', 
                           subject=subject,
                           available_students=available_students,
                           enrolled_students=enrolled_students)


@enrollment_bp.route('/api/admin/enrollments/add', methods=['POST'])
@admin_required
def add_enrollments_bulk():
    """
    Bulk enroll students into a subject.
    Auto-creates Virtual Section if needed.
    """
    data = request.json
    subject_id = data.get('subject_id')
    student_ids = data.get('student_ids', [])
    
    if not subject_id or not student_ids:
        return jsonify({'success': False, 'error': 'Missing subject_id or student_ids'}), 400
        
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'success': False, 'error': 'Subject not found'}), 404
            
        # 1. Get/Create Virtual Section
        # We need an academic_year context. We'll pick it from the first student's current section
        # OR fallback to a system default if possible.
        first_student = Student.query.get(student_ids[0])
        academic_year = first_student.section.academic_year if (first_student and first_student.section) else '2024-2025'
        
        virtual_section = Section.query.filter_by(
            linked_subject_id=subject_id,
            academic_year=academic_year,
            current_semester=subject.semester_id,
            is_elective=True
        ).first()
        
        if not virtual_section:
            section_name = f"{subject.subject_name} ({subject.semester_id} Sem) - {academic_year}"[:64]
            virtual_section = Section(
                section_id=str(uuid.uuid4()),
                program_id=subject.program_id,
                year_of_study=(int(subject.semester_id)+1)//2,
                academic_year=academic_year,
                current_semester=subject.semester_id,
                section_name=section_name,
                is_elective=True,
                linked_subject_id=subject_id,
                is_deleted=False
            )
            db.session.add(virtual_section)
            db.session.flush()
            
        # 2. Create Enrollments
        count = 0
        for stud_id in student_ids:
            # Check exist
            existing = StudentSubjectEnrollment.query.filter_by(
                student_id=stud_id, subject_id=subject_id
            ).first()
            
            if not existing:
                enroll = StudentSubjectEnrollment(
                    enrollment_id=str(uuid.uuid4()),
                    student_id=stud_id,
                    subject_id=subject_id,
                    section_id=virtual_section.section_id,
                    academic_year=academic_year,
                    semester=subject.semester_id
                )
                db.session.add(enroll)
                count += 1
                
        db.session.commit()
        return jsonify({'success': True, 'enrolled_count': count})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@enrollment_bp.route('/api/admin/enrollments/<enrollment_id>', methods=['DELETE'])
@admin_required
def delete_enrollment(enrollment_id):
    try:
        enrollment = StudentSubjectEnrollment.query.filter_by(enrollment_id=enrollment_id).first()
        if not enrollment:
            return jsonify({'success': False, 'error': 'Enrollment not found'}), 404
            
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
