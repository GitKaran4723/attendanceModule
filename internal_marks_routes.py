# ============================================================================
# INTERNAL MARKS SYSTEM - FACULTY ROUTES
# ============================================================================

@app.route('/faculty/internal-marks')
@login_required
def faculty_internal_marks():
    """
    Faculty Internal Marks - List all assessments created by faculty
    """
    current_user = get_current_user()
    
    # Get faculty record
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    if not faculty_record:
        flash('Faculty record not found.', 'danger')
        return redirect(url_for('login'))
    
    # Get all tests created by this faculty
    tests = Test.query.filter_by(
        faculty_id=faculty_record.faculty_id,
        is_deleted=False
    ).order_by(Test.test_date.desc()).all()
    
    # Get faculty's subject allocations for dropdown
    allocations = SubjectAllocation.query.filter_by(
        faculty_id=faculty_record.faculty_id,
        is_deleted=False
    ).all()
    
    return render_template('faculty/internal_marks.html', 
                         tests=tests, 
                         allocations=allocations,
                         faculty=faculty_record)


@app.route('/faculty/internal-marks/create', methods=['GET', 'POST'])
@login_required
def faculty_create_assessment():
    """
    Create new internal assessment
    """
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    if not faculty_record:
        flash('Faculty record not found.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            subject_id = request.form.get('subject_id')
            section_id = request.form.get('section_id')
            test_name = request.form.get('test_name')
            component_type = request.form.get('component_type', 'test')
            max_marks = float(request.form.get('max_marks', 0))
            weightage = request.form.get('weightage')
            test_date = request.form.get('test_date')
            description = request.form.get('description')
            
            # Validate that faculty teaches this subject in this section
            allocation = SubjectAllocation.query.filter_by(
                faculty_id=faculty_record.faculty_id,
                subject_id=subject_id,
                section_id=section_id,
                is_deleted=False
            ).first()
            
            if not allocation:
                flash('You are not authorized to create assessments for this subject/section.', 'danger')
                return redirect(url_for('faculty_internal_marks'))
            
            # Create new test
            new_test = Test(
                test_name=test_name,
                subject_id=subject_id,
                faculty_id=faculty_record.faculty_id,
                section_id=section_id,
                component_type=component_type,
                max_marks=max_marks,
                weightage=float(weightage) if weightage else None,
                test_date=datetime.strptime(test_date, '%Y-%m-%d').date() if test_date else None,
                description=description,
                is_published=False
            )
            
            db.session.add(new_test)
            db.session.commit()
            
            flash(f'Assessment "{test_name}" created successfully!', 'success')
            return redirect(url_for('faculty_enter_marks', test_id=new_test.test_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating assessment: {str(e)}', 'danger')
            return redirect(url_for('faculty_internal_marks'))
    
    # GET request - show form
    allocations = SubjectAllocation.query.filter_by(
        faculty_id=faculty_record.faculty_id,
        is_deleted=False
    ).all()
    
    return render_template('faculty/create_assessment.html', 
                         allocations=allocations,
                         faculty=faculty_record)


@app.route('/faculty/internal-marks/<test_id>/enter-marks')
@login_required
def faculty_enter_marks(test_id):
    """
    Enter/Edit marks for an assessment
    """
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    if not faculty_record:
        flash('Faculty record not found.', 'danger')
        return redirect(url_for('login'))
    
    # Get test
    test = Test.query.get_or_404(test_id)
    
    # Verify faculty owns this test
    if test.faculty_id != faculty_record.faculty_id:
        flash('You are not authorized to edit this assessment.', 'danger')
        return redirect(url_for('faculty_internal_marks'))
    
    # Get students in the section
    section = Section.query.get(test.section_id)
    students = section.get_students()
    
    # Get existing results
    existing_results = {r.student_id: r for r in test.results.all()}
    
    # Prepare student data with marks
    student_data = []
    for student in students:
        result = existing_results.get(student.student_id)
        student_data.append({
            'student': student,
            'marks': result.marks_obtained if result else None,
            'remarks': result.remarks if result else ''
        })
    
    return render_template('faculty/enter_marks.html',
                         test=test,
                         student_data=student_data,
                         faculty=faculty_record)


@app.route('/api/faculty/internal-marks/<test_id>/save-marks', methods=['POST'])
@login_required
def api_save_marks(test_id):
    """
    Save marks for multiple students
    """
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    if not faculty_record:
        return jsonify({'success': False, 'error': 'Faculty not found'}), 404
    
    test = Test.query.get_or_404(test_id)
    
    # Verify ownership
    if test.faculty_id != faculty_record.faculty_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        marks_data = request.json.get('marks', [])
        
        for item in marks_data:
            student_id = item.get('student_id')
            marks = item.get('marks')
            remarks = item.get('remarks', '')
            
            # Validate marks
            if marks is not None:
                marks = float(marks)
                if marks < 0 or marks > test.max_marks:
                    return jsonify({
                        'success': False, 
                        'error': f'Marks must be between 0 and {test.max_marks}'
                    }), 400
            
            # Check if result exists
            result = TestResult.query.filter_by(
                test_id=test_id,
                student_id=student_id
            ).first()
            
            if result:
                # Update existing
                result.marks_obtained = marks
                result.remarks = remarks
            else:
                # Create new
                result = TestResult(
                    test_id=test_id,
                    student_id=student_id,
                    marks_obtained=marks,
                    remarks=remarks
                )
                db.session.add(result)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Marks saved successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/faculty/internal-marks/<test_id>/publish', methods=['POST'])
@login_required
def api_publish_marks(test_id):
    """
    Toggle publish status of marks
    """
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    if not faculty_record:
        return jsonify({'success': False, 'error': 'Faculty not found'}), 404
    
    test = Test.query.get_or_404(test_id)
    
    # Verify ownership
    if test.faculty_id != faculty_record.faculty_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        test.is_published = not test.is_published
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_published': test.is_published,
            'message': 'Marks published' if test.is_published else 'Marks unpublished'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INTERNAL MARKS SYSTEM - STUDENT ROUTES
# ============================================================================

@app.route('/student/internal-marks')
@student_required
def student_internal_marks():
    """
    Student view of internal marks
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        flash('Student record not found.', 'danger')
        return redirect(url_for('login'))
    
    # Get student's section
    section = Section.query.get(student_record.section_id)
    
    # Get all published tests for student's subjects
    # Get compulsory subjects
    compulsory_subjects = Subject.query.filter(
        Subject.program_id == section.program_id,
        Subject.semester_id == section.current_semester,
        Subject.subject_category == 'compulsory'
    ).all()
    
    # Get enrolled electives
    enrollments = StudentSubjectEnrollment.query.filter_by(
        student_id=student_record.student_id,
        semester=section.current_semester,
        is_deleted=False
    ).all()
    enrolled_subjects = [Subject.query.get(e.subject_id) for e in enrollments]
    
    all_subjects = compulsory_subjects + enrolled_subjects
    
    # Get marks for each subject
    subject_marks = {}
    for subject in all_subjects:
        # Find target section (main or elective)
        target_section_id = student_record.section_id
        enrollment = next((e for e in enrollments if e.subject_id == subject.subject_id), None)
        if enrollment and enrollment.section_id:
            target_section_id = enrollment.section_id
        
        # Get published tests for this subject/section
        tests = Test.query.filter_by(
            subject_id=subject.subject_id,
            section_id=target_section_id,
            is_published=True,
            is_deleted=False
        ).order_by(Test.test_date.desc()).all()
        
        # Get student's results
        marks_list = []
        for test in tests:
            result = TestResult.query.filter_by(
                test_id=test.test_id,
                student_id=student_record.student_id
            ).first()
            
            marks_list.append({
                'test': test,
                'marks': result.marks_obtained if result else None,
                'percentage': round((result.marks_obtained / test.max_marks * 100), 2) if result and result.marks_obtained is not None else None
            })
        
        if marks_list:
            subject_marks[subject.subject_id] = {
                'subject': subject,
                'marks': marks_list
            }
    
    return render_template('student/internal_marks.html',
                         subject_marks=subject_marks,
                         student=student_record,
                         section=section)


@app.route('/api/student/internal-marks')
@student_required
def api_student_internal_marks():
    """
    API endpoint for student internal marks
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    # Similar logic as above but return JSON
    # Implementation similar to student_internal_marks route
    return jsonify({'success': True, 'message': 'API endpoint for future use'})


