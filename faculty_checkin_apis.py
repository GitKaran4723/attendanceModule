# Faculty Check-In/Checkout API Endpoints
# Add these to app.py

from math import radians, sin, cos, sqrt, atan2
import app
from auth import get_current_user
import datetime
from datetime import date, datetime


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates using Haversine formula
    Returns distance in meters
    """
    R = 6371000  # Earth's radius in meters
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance


@app.route('/api/faculty/check-in', methods=['POST'])
@faculty_required
def api_faculty_checkin():
    """Faculty check-in (can be done from anywhere)"""
    from models import FacultyAttendance
    
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'success': False, 'error': 'GPS location required'}), 400
    
    today = date.today()
    
    # Check if already checked in today
    existing = FacultyAttendance.query.filter_by(
        faculty_id=faculty_record.faculty_id,
        date=today
    ).first()
    
    if existing and existing.check_in_time:
        return jsonify({'success': False, 'error': 'Already checked in today'}), 400
    
    # Create or update attendance record
    if not existing:
        attendance = FacultyAttendance(
            faculty_id=faculty_record.faculty_id,
            date=today
        )
    else:
        attendance = existing
    
    attendance.check_in_time = datetime.now()
    attendance.check_in_latitude = latitude
    attendance.check_in_longitude = longitude
    
    if not existing:
        db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'check_in_time': attendance.check_in_time.isoformat(),
        'message': 'Checked in successfully!'
    })


@app.route('/api/faculty/check-out', methods=['POST'])
@faculty_required
def api_faculty_checkout():
    """Faculty check-out (must be at department location)"""
    from models import FacultyAttendance, CollegeConfig
    
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'success': False, 'error': 'GPS location required'}), 400
    
    today = date.today()
    
    # Get today's attendance record
    attendance = FacultyAttendance.query.filter_by(
        faculty_id=faculty_record.faculty_id,
        date=today
    ).first()
    
    if not attendance or not attendance.check_in_time:
        return jsonify({'success': False, 'error': 'Please check in first'}), 400
    
    if attendance.check_out_time:
        return jsonify({'success': False, 'error': 'Already checked out today'}), 400
    
    # Get campus location from config
    config = CollegeConfig.query.first()
    if not config or not config.campus_latitude or not config.campus_longitude:
        # If no config, allow checkout (fallback)
        attendance.check_out_time = datetime.now()
        attendance.check_out_latitude = latitude
        attendance.check_out_longitude = longitude
        attendance.check_out_valid = True
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Checked out successfully!',
            'hours_worked': attendance.get_hours_worked()
        })
    
    # Calculate distance from campus
    distance = calculate_distance(
        latitude, longitude,
        config.campus_latitude, config.campus_longitude
    )
    
    radius = config.campus_radius_meters or 100  # Default 100m
    
    if distance > radius:
        return jsonify({
            'success': False,
            'error': f'You are not at the department! You are {int(distance)}m away. Please come to campus to check out.',
            'distance': int(distance),
            'required_radius': radius
        }), 400
    
    # Valid checkout
    attendance.check_out_time = datetime.now()
    attendance.check_out_latitude = latitude
    attendance.check_out_longitude = longitude
    attendance.check_out_valid = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'check_out_time': attendance.check_out_time.isoformat(),
        'hours_worked': attendance.get_hours_worked(),
        'message': 'Checked out successfully!'
    })


@app.route('/api/faculty/attendance-status')
@faculty_required
def api_faculty_attendance_status():
    """Get today's check-in/out status"""
    from models import FacultyAttendance
    
    current_user = get_current_user()
    faculty_record = Faculty.query.filter_by(user_id=current_user.user_id).first()
    
    today = date.today()
    attendance = FacultyAttendance.query.filter_by(
        faculty_id=faculty_record.faculty_id,
        date=today
    ).first()
    
    if not attendance:
        return jsonify({
            'checked_in': False,
            'checked_out': False
        })
    
    return jsonify({
        'checked_in': bool(attendance.check_in_time),
        'checked_out': bool(attendance.check_out_time),
        'check_in_time': attendance.check_in_time.isoformat() if attendance.check_in_time else None,
        'check_out_time': attendance.check_out_time.isoformat() if attendance.check_out_time else None,
        'hours_worked': attendance.get_hours_worked()
    })
