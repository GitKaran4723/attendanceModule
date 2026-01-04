# ============================================
# Student Dashboard Routes
# ============================================

# Motivational quotes list
MOTIVATIONAL_QUOTES = [
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "Believe you can and you're halfway there.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "Education is the most powerful weapon which you can use to change the world.",
    "Your attitude, not your aptitude, will determine your altitude.",
    "The only way to do great work is to love what you do.",
    "Don't watch the clock; do what it does. Keep going.",
    "The expert in anything was once a beginner.",
    "Success is the sum of small efforts repeated day in and day out.",
    "Dream big, work hard, stay focused, and surround yourself with good people.",
    "The beautiful thing about learning is that no one can take it away from you.",
    "Strive for progress, not perfection.",
    "Your only limit is you.",
    "Great things never come from comfort zones.",
    "The harder you work for something, the greater you'll feel when you achieve it."
]

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    """
    Student Dashboard - Main page for students
    Shows attendance analytics, holidays, check-in status, and motivational quote
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        flash('Student record not found.', 'danger')
        return redirect(url_for('login'))
    
    # Get student's section
    section = Section.query.get(student_record.section_id)
    
    # Calculate overall attendance percentage
    total_sessions = db.session.query(AttendanceSession.attendance_session_id).join(ClassSchedule).filter(
        ClassSchedule.section_id == student_record.section_id,
        AttendanceSession.is_deleted == False
    ).distinct().count()
    
    attended = db.session.query(AttendanceSession.attendance_session_id).join(
        AttendanceRecord, AttendanceRecord.attendance_session_id == AttendanceSession.attendance_session_id
    ).join(ClassSchedule).filter(
        AttendanceRecord.student_id == student_record.student_id,
        AttendanceRecord.status == 'present',
        ClassSchedule.section_id == student_record.section_id
    ).distinct().count()
    
    overall_percentage = int((attended / total_sessions * 100)) if total_sessions > 0 else 0
    
    # Check if in red zone (<75%)
    is_red_zone = overall_percentage < 75
    
    # Get random motivational quote
    import random
    motivational_quote = random.choice(MOTIVATIONAL_QUOTES)
    
    # Check today's check-in status
    today = date.today()
    checkin_today = CampusCheckIn.query.filter_by(
        student_id=student_record.student_id,
        checkin_date=today
    ).first()
    
    has_checked_in = bool(checkin_today)
    
    dashboard_data = {
        'student': student_record,
        'section': section,
        'overall_percentage': overall_percentage,
        'total_sessions': total_sessions,
        'attended': attended,
        'is_red_zone': is_red_zone,
        'motivational_quote': motivational_quote,
        'has_checked_in': has_checked_in
    }
    
    return render_template('student/dashboard.html', **dashboard_data)


@app.route('/api/student/analytics')
@student_required
def api_student_analytics():
    """
    Get detailed attendance analytics for the logged-in student
    Returns subject-wise breakdown with percentages
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    try:
        # Get student's section
        section = Section.query.get(student_record.section_id)
        if not section:
            return jsonify({'success': False, 'error': 'Section not found'}), 404
        
        # Get ALL subjects for this semester
        subjects = Subject.query.filter_by(semester_id=section.current_semester).all()
        
        # Initialize stats for ALL subjects in this semester
        subject_stats = {}
        for subject in subjects:
            subject_stats[subject.subject_id] = {
                'subject_name': subject.subject_name,
                'subject_code': subject.subject_code,
                'total_classes': 0,
                'attended': 0
            }
        
        # Get all sessions for the student's section
        all_sessions = db.session.query(
            AttendanceSession, 
            ClassSchedule,
            Subject
        ).join(
            ClassSchedule, AttendanceSession.schedule_id == ClassSchedule.schedule_id
        ).join(
            Subject, ClassSchedule.subject_id == Subject.subject_id
        ).filter(
            ClassSchedule.section_id == student_record.section_id,
            AttendanceSession.is_deleted == False
        ).all()
        
        # Get all attendance records for this student
        student_records = AttendanceRecord.query.filter_by(
            student_id=student_record.student_id,
            is_deleted=False
        ).all()
        
        # Create a map of session_id -> status
        attendance_map = {r.attendance_session_id: r.status for r in student_records}
        
        # Process Stats - Count EVERY session
        for session, schedule, subject in all_sessions:
            sub_id = subject.subject_id
            
            # Only count if this subject is in the semester
            if sub_id in subject_stats:
                subject_stats[sub_id]['total_classes'] += 1
                
                # Check attendance
                status = attendance_map.get(session.attendance_session_id, 'absent')
                
                if status == 'present':
                    subject_stats[sub_id]['attended'] += 1
        
        # Format Subject Stats
        final_subject_stats = []
        for sub_id, stats in subject_stats.items():
            total = stats['total_classes']
            attended = stats['attended']
            percentage = round((attended / total * 100), 1) if total > 0 else 0
            
            final_subject_stats.append({
                'subject_name': stats['subject_name'],
                'subject_code': stats['subject_code'],
                'total_classes': total,
                'attended': attended,
                'percentage': percentage
            })
        
        # Calculate overall percentage
        total_all = sum(s['total_classes'] for s in final_subject_stats)
        attended_all = sum(s['attended'] for s in final_subject_stats)
        overall_percentage = round((attended_all / total_all * 100), 1) if total_all > 0 else 0
        
        return jsonify({
            'success': True,
            'student_name': f"{student_record.first_name} {student_record.last_name}",
            'roll_number': student_record.roll_number,
            'overall_percentage': overall_percentage,
            'is_red_zone': overall_percentage < 75,
            'subject_stats': final_subject_stats
        })
    except Exception as e:
        import traceback
        print(f"Analytics Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/student/check-in', methods=['POST'])
@student_required
def api_student_checkin():
    """
    Student campus check-in with GPS verification
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'success': False, 'error': 'GPS location required'}), 400
    
    today = date.today()
    
    # Check if already checked in today
    existing = CampusCheckIn.query.filter_by(
        student_id=student_record.student_id,
        checkin_date=today
    ).first()
    
    if existing:
        return jsonify({'success': False, 'error': 'Already checked in today'}), 400
    
    # Get campus location from config
    config = CollegeConfig.query.first()
    
    # Verify location if config exists
    if config and config.campus_latitude and config.campus_longitude:
        from math import radians, sin, cos, sqrt, atan2
        
        # Calculate distance
        R = 6371000  # Earth's radius in meters
        lat1, lon1, lat2, lon2 = map(radians, [latitude, longitude, config.campus_latitude, config.campus_longitude])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        radius = config.campus_radius_meters or 500  # Default 500m
        
        if distance > radius:
            return jsonify({
                'success': False,
                'error': f'You are not at campus! You are {int(distance)}m away.',
                'distance': int(distance)
            }), 400
    
    # Create check-in record
    checkin = CampusCheckIn(
        student_id=student_record.student_id,
        checkin_date=today,
        checkin_time=datetime.now(),
        latitude=latitude,
        longitude=longitude
    )
    
    db.session.add(checkin)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Checked in successfully!',
        'checkin_time': checkin.checkin_time.strftime('%I:%M %p')
    })


@app.route('/api/student/recent-absences')
@student_required
def api_student_recent_absences():
    """
    Get student's absences from the past 3 days
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    # Get absences from past 3 days
    three_days_ago = date.today() - timedelta(days=3)
    
    absences = db.session.query(
        AttendanceRecord,
        AttendanceSession,
        ClassSchedule,
        Subject
    ).join(
        AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.attendance_session_id
    ).join(
        ClassSchedule, AttendanceSession.schedule_id == ClassSchedule.schedule_id
    ).join(
        Subject, ClassSchedule.subject_id == Subject.subject_id
    ).filter(
        AttendanceRecord.student_id == student_record.student_id,
        AttendanceRecord.status == 'absent',
        AttendanceSession.taken_at >= three_days_ago,
        AttendanceRecord.is_deleted == False
    ).order_by(AttendanceSession.taken_at.desc()).all()
    
    absence_list = []
    for record, session, schedule, subject in absences:
        absence_list.append({
            'date': session.taken_at.strftime('%d %b %Y'),
            'day': session.taken_at.strftime('%A'),
            'subject_name': subject.subject_name,
            'subject_code': subject.subject_code
        })
    
    return jsonify({
        'success': True,
        'absences': absence_list
    })


@app.route('/api/student/holidays')
@student_required
def api_student_holidays():
    """
    Get upcoming and recent holidays
    """
    from models import Holiday
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Get upcoming holidays (next 30 days)
    upcoming = Holiday.query.filter(
        Holiday.holiday_date >= today,
        Holiday.holiday_date <= today + timedelta(days=30)
    ).order_by(Holiday.holiday_date).all()
    
    # Get recent holidays (past 7 days)
    recent = Holiday.query.filter(
        Holiday.holiday_date >= today - timedelta(days=7),
        Holiday.holiday_date < today
    ).order_by(Holiday.holiday_date.desc()).all()
    
    # Check if tomorrow is a holiday
    tomorrow_holiday = Holiday.query.filter_by(holiday_date=tomorrow).first()
    
    upcoming_list = [{
        'date': h.holiday_date.strftime('%d %b %Y'),
        'day': h.holiday_date.strftime('%A'),
        'name': h.holiday_name,
        'is_tomorrow': h.holiday_date == tomorrow
    } for h in upcoming]
    
    recent_list = [{
        'date': h.holiday_date.strftime('%d %b %Y'),
        'day': h.holiday_date.strftime('%A'),
        'name': h.holiday_name
    } for h in recent]
    
    return jsonify({
        'success': True,
        'tomorrow_is_holiday': bool(tomorrow_holiday),
        'tomorrow_holiday_name': tomorrow_holiday.holiday_name if tomorrow_holiday else None,
        'upcoming': upcoming_list,
        'recent': recent_list
    })


@app.route('/api/student/motivational-quote')
@student_required
def api_student_motivational_quote():
    """
    Get a random motivational quote
    """
    import random
    quote = random.choice(MOTIVATIONAL_QUOTES)
    
    return jsonify({
        'success': True,
        'quote': quote
    })


@app.route('/student/profile')
@student_required
def student_profile():
    """
    Student profile view and edit page
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        flash('Student record not found.', 'danger')
        return redirect(url_for('login'))
    
    section = Section.query.get(student_record.section_id)
    
    return render_template('student/profile.html', student=student_record, section=section)


@app.route('/api/student/profile', methods=['PUT'])
@student_required
def api_student_update_profile():
    """
    Update student profile (phone, address only)
    """
    current_user = get_current_user()
    student_record = Student.query.filter_by(user_id=current_user.user_id).first()
    
    if not student_record:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    data = request.get_json()
    
    # Students can only update specific fields
    if 'phone' in data:
        student_record.phone = data['phone']
    if 'address' in data:
        student_record.address = data['address']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
