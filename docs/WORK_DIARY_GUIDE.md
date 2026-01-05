# Work Diary & Authentication Setup Guide

## New Features Added

### 1. **Authentication System** 🔐
Complete role-based authentication system with login/logout functionality.

#### Features:
- Secure password hashing using werkzeug
- Session-based authentication
- Role-based access control (Admin, HOD, Faculty, Student)
- Protected routes with decorators
- Permission checking functions

#### Usage:
```python
# Protect routes
@app.route('/protected')
@login_required
def protected_route():
    current_user = get_current_user()
    return f"Hello {current_user.username}"

# Role-specific routes
@app.route('/admin-only')
@admin_required
def admin_route():
    # Only admins can access
    pass

@app.route('/faculty-only')
@faculty_required
def faculty_route():
    # Only faculty can access
    pass
```

### 2. **Work Diary System** 📓
Faculty can track daily activities with automatic diary entries when taking attendance.

#### Features:
- Auto-generated diary numbers (WD-YYYY-NNNN format)
- Automatic diary creation from attendance sessions
- Manual entry for non-class activities:
  - Theory Classes
  - Practical/Lab Classes
  - Invigilation
  - Exam Duty
  - Meetings
  - Committee Work
  - Counseling
  - Other activities
- Approval workflow: Draft → Submitted → Approved/Rejected
- HOD/Admin approval system
- Student count tracking
- Topics covered documentation

#### Diary Entry Fields:
- Diary Number (auto-generated)
- Date & Time (start/end with duration calculation)
- Faculty, Subject, Section
- Activity Type
- Students Present/Total (for classes)
- Activity Title & Description (for non-class activities)
- Topics Covered
- Approval status and remarks

### 3. **Bulk Import System** 📥
Admin can import large datasets from CSV/Excel files.

#### Supported Import Types:
1. **Students** - Required columns: enrollment_no, first_name, last_name, email
2. **Faculty** - Required columns: employee_id, first_name, last_name, email
3. **Subjects** - Required columns: subject_code, subject_name, semester
4. **Schedules** - Required columns: subject_code, faculty_employee_id, day_of_week, start_time, end_time, room_number

#### Features:
- CSV and Excel (.xlsx, .xls) support
- Validation and error handling
- Duplicate detection
- Import history tracking
- Success/failure reports
- Error logging for debugging

## Quick Start Guide

### 1. Install New Dependencies
```bash
pip install pandas==2.1.3 openpyxl==3.1.2
```

Or simply:
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
The database will be automatically created on first run with default roles.

```bash
python app.py
```

### 3. Create Admin User (via Python console)
```python
from app import app, db
from models import User, Role
from auth import hash_password

with app.app_context():
    # Get admin role
    admin_role = Role.query.filter_by(role_name='admin').first()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@bcabub.edu',
        password_hash=hash_password('admin123'),
        role_id=admin_role.role_id,
        is_active=True
    )
    
    db.session.add(admin)
    db.session.commit()
    print("Admin user created! Username: admin, Password: admin123")
```

### 4. Login
Navigate to `http://localhost:5000/login`
- Username: `admin`
- Password: `admin123` (change this immediately!)

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Work Diary
- `GET /work-diary` - List all diary entries
- `GET/POST /work-diary/create` - Create new diary entry
- `GET/POST /work-diary/<id>/edit` - Edit diary entry
- `POST /api/work-diary/<id>/submit` - Submit for approval
- `POST /api/work-diary/<id>/approve` - Approve entry (Admin/HOD)
- `POST /api/work-diary/<id>/reject` - Reject entry (Admin/HOD)

### Bulk Import
- `GET /admin/import` - Import interface (Admin only)
- `POST /api/admin/import` - Upload and process import file

## Database Models

### WorkDiary Table
```sql
- diary_id (UUID, Primary Key)
- diary_number (VARCHAR, Unique) - Format: WD-YYYY-NNNN
- faculty_id (Foreign Key → faculty)
- subject_id (Foreign Key → subjects)
- section_id (Foreign Key → sections)
- date (DATE)
- start_time (TIME)
- end_time (TIME)
- duration_hours (DECIMAL, Calculated)
- activity_type (ENUM: theory_class, practical_class, invigilation, etc.)
- attendance_session_id (Foreign Key → attendance_sessions, nullable)
- students_present (INTEGER)
- students_total (INTEGER)
- activity_title (VARCHAR)
- activity_description (TEXT)
- topics_covered (TEXT)
- status (ENUM: draft, submitted, approved, rejected)
- approved_by (Foreign Key → users)
- approved_at (TIMESTAMP)
- approval_remarks (TEXT)
- created_at, updated_at (Timestamps)
```

### ImportLog Table
```sql
- import_id (UUID, Primary Key)
- import_type (VARCHAR) - students, faculty, subjects, schedules
- imported_by (Foreign Key → users)
- file_name (VARCHAR)
- total_rows (INTEGER)
- successful_rows (INTEGER)
- failed_rows (INTEGER)
- status (ENUM: processing, completed, completed_with_errors, failed)
- error_log (TEXT)
- imported_at (TIMESTAMP)
```

## Sample CSV Formats

### Students Import (students.csv)
```csv
enrollment_no,first_name,last_name,email,phone,date_of_birth
2021001,Raj,Kumar,raj.kumar@example.com,9876543210,2003-05-15
2021002,Priya,Sharma,priya.sharma@example.com,9876543211,2003-08-22
```

### Faculty Import (faculty.csv)
```csv
employee_id,first_name,last_name,email,phone,designation,department
FAC001,Dr. Amit,Verma,amit.verma@bcabub.edu,9876543212,Professor,Computer Science
FAC002,Dr. Neha,Singh,neha.singh@bcabub.edu,9876543213,Assistant Professor,Computer Science
```

### Subjects Import (subjects.csv)
```csv
subject_code,subject_name,semester,credits,subject_type
CS101,Introduction to Programming,1,4,theory
CS102,Programming Lab,1,2,practical
CS201,Data Structures,3,4,theory
```

### Schedules Import (schedules.csv)
```csv
subject_code,faculty_employee_id,day_of_week,start_time,end_time,room_number
CS101,FAC001,Monday,09:00,10:30,Lab-1
CS102,FAC002,Tuesday,11:00,13:00,Lab-2
```

## Security Considerations

### Password Security
- Passwords are hashed using werkzeug's security functions
- Never store plain text passwords
- Use strong passwords in production

### Session Security
- Sessions use Flask's built-in session management
- Set `SECRET_KEY` in production environment
- Use HTTPS in production

### Role-Based Access
- Four roles: admin, hod, faculty, student
- Each route can be protected with decorators
- Permissions are checked at both route and function level

## Workflow Examples

### Work Diary Auto-Creation Flow
1. Faculty takes attendance for a class
2. System automatically creates work diary entry
3. Diary entry populated with:
   - Subject, section details
   - Class timing
   - Student count from attendance
   - Activity type (theory/practical based on room)
4. Faculty can edit and add topics covered
5. Faculty submits for approval
6. HOD/Admin reviews and approves

### Manual Diary Entry Flow
1. Faculty clicks "Create Work Diary"
2. Selects activity type (invigilation, meeting, etc.)
3. Fills in details:
   - Date and time
   - Activity title
   - Description
4. Saves as draft
5. Submits for approval
6. HOD/Admin reviews

### Bulk Import Flow
1. Admin prepares CSV/Excel file
2. Navigates to Bulk Import page
3. Selects import type
4. Uploads file
5. System validates and imports data
6. Shows success/error report
7. Import logged in history

## Troubleshooting

### Login Issues
- Ensure user exists in database
- Check password is correct
- Verify user is_active = True
- Check role assignment

### Work Diary Not Creating
- Verify faculty record exists for user
- Check attendance session has valid schedule
- Ensure database constraints are met

### Import Failing
- Check CSV column names match exactly
- Verify data types (dates, numbers)
- Check for duplicate entries
- Review error log in ImportLog table

## Next Steps

### For Students:
1. Create additional users for testing
2. Implement API endpoints for mobile app
3. Add export functionality (PDF reports)
4. Create analytics dashboard
5. Add notifications for diary approval
6. Implement search and filtering
7. Add calendar view for diaries
8. Create mobile app interface

### For Faculty:
1. Login with your credentials
2. Take attendance to auto-create diary entries
3. Add manual entries for non-class activities
4. Submit diaries for approval
5. Track your monthly activities

### For Admin:
1. Create user accounts for faculty and students
2. Use bulk import for initial data setup
3. Review and approve work diaries
4. Monitor import history
5. Generate reports

## Support

For issues or questions:
1. Check the error logs in terminal
2. Review the ImportLog table for import errors
3. Verify user permissions and roles
4. Check database constraints

## License

This project is for educational purposes as part of the BCA BUB program.
