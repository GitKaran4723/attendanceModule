# BCA BUB - Student Project Guide

## 🎓 Project Overview

This is a modular Progressive Web App (PWA) for managing attendance in BCA BUB college. The project is designed for students to work on different modules collaboratively.

## 📁 Project Structure

```
AttendanceModule/
├── app.py                  # Main Flask application with routes
├── models.py               # Database models (SQLAlchemy ORM)
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── static/
│   ├── manifest.json      # PWA manifest
│   ├── service-worker.js  # Offline functionality
│   ├── css/
│   │   └── style.css     # Material Design styles
│   ├── js/
│   │   └── app.js        # Frontend JavaScript
│   └── icons/            # App icons
├── templates/
│   ├── index.html        # Dashboard
│   ├── faculty.html      # Faculty management
│   ├── students.html     # Student management
│   └── attendance.html   # Attendance records
└── instance/
    └── attendance.db     # SQLite database (created on first run)
```

## 🗄️ Database Schema

### Core Tables
- **roles** - User roles (admin, hod, faculty, student)
- **users** - Authentication and user accounts
- **faculties** - Faculty information
- **students** - Student information
- **programs** - Academic programs (BCA, MCA, etc.)
- **sections** - Class sections

### Academic Tables
- **semesters** - Academic terms
- **subjects** - Course subjects
- **subject_allocations** - Faculty-Subject-Section mapping
- **class_schedules** - Timetable entries

### Attendance Tables
- **attendance_sessions** - Attendance session per class
- **attendance_records** - Individual student attendance

### Assessment Tables
- **tests** - Test/exam information
- **test_results** - Student test scores

## 👥 Module Assignment for Students

### Module 1: User Management (2-3 students)
**Files to work on:**
- `app.py` - Add routes for user CRUD
- `templates/` - Create user forms

**Tasks:**
1. Implement user registration with role selection
2. Add password hashing (use werkzeug.security)
3. Create user profile pages
4. Add user edit/delete functionality
5. Implement user search and filtering

**API Endpoints to create:**
```python
POST   /api/users/register   # Register new user
PUT    /api/users/<id>        # Update user
DELETE /api/users/<id>        # Soft delete user
GET    /api/users/search      # Search users
```

### Module 2: Faculty Management (2-3 students)
**Files to work on:**
- `app.py` - Expand faculty routes
- `templates/faculty.html` - Add forms and details

**Tasks:**
1. Add faculty registration form
2. Implement faculty profile pages
3. Add designation and HOD management
4. Create faculty dashboard showing:
   - Assigned subjects
   - Class schedule
   - Attendance sessions taken
5. Add bulk import from CSV

**API Endpoints to create:**
```python
POST   /api/faculty            # Add new faculty
GET    /api/faculty/<id>       # Get faculty details
PUT    /api/faculty/<id>       # Update faculty
GET    /api/faculty/<id>/subjects # Get assigned subjects
POST   /api/faculty/import     # Bulk import
```

### Module 3: Student Management (2-3 students)
**Files to work on:**
- `app.py` - Expand student routes
- `templates/students.html` - Add forms

**Tasks:**
1. Create student registration form
2. Implement section assignment
3. Add student profile with:
   - Personal details
   - Academic info
   - Attendance percentage
   - Test scores
4. Add filters by section, program, year
5. Implement bulk student import

**API Endpoints to create:**
```python
POST   /api/students           # Add student
GET    /api/students/<id>      # Student details
PUT    /api/students/<id>      # Update student
GET    /api/students/<id>/attendance  # Attendance summary
GET    /api/students/<id>/tests       # Test results
POST   /api/students/import    # Bulk import
```

### Module 4: Schedule Management (2-3 students)
**Files to work on:**
- `app.py` - Create schedule routes
- `templates/schedule.html` - Create new template

**Tasks:**
1. Create timetable entry form
2. Implement weekly schedule view
3. Add schedule for different sections
4. Create faculty schedule view
5. Add schedule conflict detection
6. Implement schedule copy/paste for weeks

**API Endpoints to create:**
```python
POST   /api/schedules          # Create schedule
GET    /api/schedules/section/<id>  # Get section timetable
GET    /api/schedules/faculty/<id>  # Get faculty timetable
DELETE /api/schedules/<id>     # Delete schedule
```

### Module 5: Attendance Management (3-4 students)
**Files to work on:**
- `app.py` - Implement attendance workflow
- `templates/attendance.html` - Enhance interface

**Tasks:**
1. Create attendance taking interface:
   - Select schedule
   - Load student list
   - Mark present/absent/late/excused
   - Add remarks
2. Implement attendance finalization
3. Add attendance editing (before finalized)
4. Create attendance reports:
   - By student
   - By subject
   - By date range
   - Defaulters list
5. Add attendance summary dashboard

**API Endpoints to create:**
```python
POST   /api/attendance/session       # Create session
POST   /api/attendance/record        # Mark attendance
PUT    /api/attendance/record/<id>   # Update record
GET    /api/attendance/session/<id>  # Get session details
PUT    /api/attendance/session/<id>/finalize  # Finalize
GET    /api/attendance/reports       # Generate reports
```

### Module 6: Test Management (2-3 students)
**Files to work on:**
- `app.py` - Create test routes
- `templates/tests.html` - Create new template

**Tasks:**
1. Create test entry form
2. Implement marks entry interface
3. Add test result viewing
4. Create test analytics:
   - Average marks
   - Pass percentage
   - Top performers
5. Generate result sheets

**API Endpoints to create:**
```python
POST   /api/tests              # Create test
POST   /api/tests/<id>/results # Enter marks
GET    /api/tests/<id>         # Test details
GET    /api/tests/<id>/analytics # Test statistics
```

### Module 7: Reports & Analytics (2-3 students)
**Files to work on:**
- `app.py` - Create reports routes
- `templates/reports.html` - Create new template

**Tasks:**
1. Attendance reports:
   - Defaulters (< 75%)
   - Subject-wise
   - Date-range
2. Test performance reports
3. Faculty workload reports
4. Export to PDF/Excel
5. Create visual charts (use Chart.js)

### Module 8: Authentication & Authorization (2 students)
**Files to work on:**
- `app.py` - Add auth middleware
- Create `auth.py` module

**Tasks:**
1. Implement login/logout
2. Add session management
3. Create role-based access control
4. Add password reset functionality
5. Implement "Remember Me"

**API Endpoints to create:**
```python
POST   /api/auth/login         # Login
POST   /api/auth/logout        # Logout
POST   /api/auth/reset         # Reset password
GET    /api/auth/check         # Check auth status
```

### Module 9: PWA Features (1-2 students)
**Files to work on:**
- `service-worker.js`
- `manifest.json`
- `static/js/app.js`

**Tasks:**
1. Enhance offline caching
2. Add push notifications
3. Implement background sync
4. Add install prompts
5. Create offline fallback pages

## 🚀 Getting Started (For Students)

### 1. Setup Development Environment

```bash
# Clone/download the project
cd AttendanceModule

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### 2. Understanding the Code

**Read these files first:**
1. `models.py` - Understand the database structure
2. `app.py` - See how routes work
3. `templates/index.html` - Learn the UI structure

### 3. Working on Your Module

1. **Create a new branch** (if using Git):
   ```bash
   git checkout -b feature/faculty-management
   ```

2. **Add your routes in app.py**:
   ```python
   @app.route('/your-route')
   def your_function():
       # Your code here
       pass
   ```

3. **Create templates in templates/**:
   - Copy existing template structure
   - Maintain consistent styling

4. **Test your changes**:
   - Run the app
   - Test all CRUD operations
   - Check mobile responsiveness

5. **Document your work**:
   - Add comments to code
   - Update this file with your changes

## 📝 Coding Guidelines

### Python (Backend)
```python
# Use descriptive function names
@app.route('/api/faculty/<faculty_id>')
def get_faculty_details(faculty_id):
    """
    Retrieve faculty details by ID.
    Returns JSON with faculty information.
    """
    faculty = Faculty.query.get_or_404(faculty_id)
    return jsonify(faculty.to_dict())

# Always handle errors
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
    return jsonify({'error': str(e)}), 400

# Use proper HTTP status codes
return jsonify(data), 201  # Created
return jsonify(data), 200  # OK
return jsonify(error), 400  # Bad Request
return jsonify(error), 404  # Not Found
```

### HTML (Frontend)
```html
<!-- Use semantic HTML -->
<section class="section">
    <h3 class="section-title">Faculty List</h3>
    <div class="user-list">
        <!-- Content -->
    </div>
</section>

<!-- Use existing CSS classes -->
<button class="btn-primary">Submit</button>
<button class="btn-text">Cancel</button>
```

### JavaScript
```javascript
// Use async/await for API calls
async function saveFaculty() {
    try {
        const response = await fetch('/api/faculty', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            showSnackbar('Saved successfully!');
        }
    } catch (error) {
        showSnackbar('Error: ' + error.message);
    }
}
```

## 🧪 Testing Checklist

Before submitting your module:

- [ ] All CRUD operations work correctly
- [ ] Forms validate input properly
- [ ] Errors are handled gracefully
- [ ] Mobile UI works properly
- [ ] Data persists in database
- [ ] No console errors
- [ ] Code is commented
- [ ] API returns correct status codes

## 🐛 Common Issues & Solutions

### Issue: Database not found
**Solution:** Run `python app.py` to create the database automatically

### Issue: Import errors
**Solution:** Make sure virtual environment is activated and dependencies are installed

### Issue: Template not found
**Solution:** Templates must be in the `templates/` folder

### Issue: Static files not loading
**Solution:** Use `url_for('static', filename='...')` in templates

## 📚 Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Tutorial: https://docs.sqlalchemy.org/
- Material Design: https://material.io/design
- PWA Guide: https://web.dev/progressive-web-apps/

## 🤝 Collaboration Tips

1. **Communicate**: Use group chat/meetings regularly
2. **Code Review**: Review each other's code
3. **Git**: Use version control (Git/GitHub)
4. **Documentation**: Document your APIs
5. **Testing**: Test together before final submission

## 📊 Project Timeline (Suggested)

**Week 1-2:** Setup & Learning
- Understand codebase
- Setup development environment
- Learn Flask basics

**Week 3-4:** Module Development
- Each team works on their module
- Regular standup meetings
- Code reviews

**Week 5-6:** Integration
- Integrate all modules
- Fix bugs
- Testing

**Week 7-8:** Polish & Deployment
- UI improvements
- Performance optimization
- Documentation
- Final testing

## 🎯 Bonus Features (Optional)

- Email notifications
- SMS integration
- Biometric attendance
- QR code check-in
- Mobile app (React Native/Flutter)
- Data visualization dashboard
- Export to Excel/PDF
- Multi-language support

Good luck with your project! 🚀
