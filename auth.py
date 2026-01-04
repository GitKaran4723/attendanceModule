"""
Authentication and Authorization Module
Handles user login, session management, and role-based access control
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db


# ============================================
# Password Hashing Utilities
# ============================================

def hash_password(password):
    """
    Hash a password using werkzeug's security functions
    """
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password_hash, password):
    """
    Verify a password against its hash
    """
    return check_password_hash(password_hash, password)


# ============================================
# Session Management
# ============================================

def login_user(user):
    """
    Create a session for the user after successful login
    """
    from flask import session
    
    # Make session permanent (will last for PERMANENT_SESSION_LIFETIME)
    session.permanent = True
    
    session['user_id'] = user.user_id
    session['username'] = user.username
    session['role'] = user.role.role_name if user.role else None
    session['is_authenticated'] = True
    
    # Update last login time
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.session.commit()


def logout_user():
    """
    Clear user session on logout
    """
    session.clear()


def get_current_user():
    """
    Get the currently logged-in user from session
    Returns User object or None
    """
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def is_authenticated():
    """
    Check if user is logged in
    """
    return session.get('is_authenticated', False)


def get_user_role():
    """
    Get the role of current user
    """
    return session.get('role', None)


# ============================================
# Decorators for Route Protection
# ============================================

def login_required(f):
    """
    Decorator to require login for a route
    Usage: @login_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Decorator to require specific role(s) for a route
    Usage: @role_required('admin', 'hod')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.url))
            
            user_role = get_user_role()
            if user_role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def faculty_required(f):
    """
    Decorator to require faculty role (includes HOD and admin)
    Usage: @faculty_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        
        user_role = get_user_role()
        if user_role not in ['faculty', 'hod', 'admin']:
            flash('Only faculty members can access this page.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role
    Usage: @admin_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        
        if get_user_role() != 'admin':
            flash('Only administrators can access this page.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Decorator to require student role
    Usage: @student_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        
        user_role = get_user_role()
        if user_role not in ['student', 'parent']:
            flash('Only students can access this page.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# Permission Checking
# ============================================

def can_edit_work_diary(diary):
    """
    Check if current user can edit a work diary entry
    - Own diary if not submitted
    - Admin/HOD can edit any
    """
    user = get_current_user()
    if not user:
        return False
    
    role = get_user_role()
    
    # Admin and HOD can edit any
    if role in ['admin', 'hod']:
        return True
    
    # Faculty can edit their own if not submitted
    if role == 'faculty':
        if diary.faculty.user_id == user.user_id and diary.status == 'draft':
            return True
    
    return False


def can_approve_work_diary(diary):
    """
    Check if current user can approve a work diary entry
    Only HOD and Admin can approve
    """
    role = get_user_role()
    return role in ['admin', 'hod']


def can_view_all_diaries():
    """
    Check if user can view all work diaries
    Admin and HOD can view all, faculty only their own
    """
    role = get_user_role()
    return role in ['admin', 'hod']
