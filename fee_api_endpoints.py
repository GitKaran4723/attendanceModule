# Fee Management API Endpoints - Add to app.py after student edit route

# ---------------------------------------------
# Fee Management Routes
# ---------------------------------------------

@app.route('/api/admin/students/<student_id>/assign-fee', methods=['POST'])
@admin_required
def api_assign_fee_to_student(student_id):
    """Auto-assign fee to student based on joining year, academic year, and seat type"""
    from fee_helpers import assign_fee_to_student
    
    current_user = get_current_user()
    result = assign_fee_to_student(student_id, current_user.user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/api/admin/students/<student_id>/additional-fee', methods=['POST'])
@admin_required
def api_add_additional_fee(student_id):
    """Add additional fee to student"""
    from fee_helpers import add_additional_fee
    
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        result = add_additional_fee(
            student_id=student_id,
            academic_year=data.get('academic_year'),
            fee_name=data.get('fee_name'),
            amount=data.get('amount'),
            remarks=data.get('remarks'),
            user_id=current_user.user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/students/<student_id>/additional-fee/<int:fee_index>', methods=['DELETE'])
@admin_required
def api_remove_additional_fee(student_id, fee_index):
    """Remove additional fee from student"""
    from fee_helpers import remove_additional_fee
    
    try:
        data = request.get_json()
        result = remove_additional_fee(
            student_id=student_id,
            academic_year=data.get('academic_year'),
            fee_index=fee_index
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/students/<student_id>/fee-breakdown')
@login_required
def api_get_fee_breakdown(student_id):
    """Get fee breakdown for student (accessible by student, faculty, admin)"""
    from fee_helpers import get_student_fee_breakdown
    
    current_user = get_current_user()
    
    # Check permissions
    if current_user.role == 'student':
        # Students can only view their own fees
        student = Student.query.filter_by(user_id=current_user.user_id).first()
        if not student or student.student_id != student_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    elif current_user.role == 'faculty':
        # Faculty can view fees of students in their class
        faculty = Faculty.query.filter_by(user_id=current_user.user_id).first()
        if faculty:
            # Check if student is in faculty's class
            student = Student.query.get(student_id)
            if not student or not student.section_id:
                return jsonify({'success': False, 'error': 'Student not found'}), 404
            
            section = Section.query.get(student.section_id)
            if not section or section.class_teacher_id != faculty.faculty_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    # Admin can view all
    
    academic_year = request.args.get('academic_year')
    result = get_student_fee_breakdown(student_id, academic_year)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
