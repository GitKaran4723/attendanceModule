# Contributing to BCA BUB Attendance System

## 👥 For Students Working on This Project

Thank you for contributing to the BCA BUB Attendance System! This guide will help you work effectively with your team.

## 🚀 Getting Started

### 1. Setup Your Environment

```bash
# Clone the project (if using Git)
git clone <repository-url>
cd AttendanceModule

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py

# Run the application
python app.py
```

### 2. Choose Your Module

Review `STUDENT_GUIDE.md` and choose a module to work on. Coordinate with your team to avoid overlaps.

## 📝 Coding Standards

### Python Code Style

Follow PEP 8 guidelines:

```python
# Good: Clear function names, docstrings, proper spacing
@app.route('/api/faculty/<faculty_id>')
def get_faculty_details(faculty_id):
    """
    Retrieve faculty details by ID.
    
    Args:
        faculty_id (str): UUID of the faculty member
        
    Returns:
        JSON response with faculty data
    """
    faculty = Faculty.query.get_or_404(faculty_id)
    return jsonify(faculty.to_dict())


# Bad: No docstring, unclear names, no error handling
@app.route('/api/f/<id>')
def gf(id):
    f = Faculty.query.get(id)
    return jsonify(f.to_dict())
```

### Database Queries

Always handle database operations safely:

```python
# Good: Proper error handling
try:
    new_faculty = Faculty(
        name=data.get('name'),
        email=data.get('email')
    )
    db.session.add(new_faculty)
    db.session.commit()
    return jsonify({'success': True}), 201
except Exception as e:
    db.session.rollback()
    return jsonify({'success': False, 'error': str(e)}), 400


# Bad: No error handling
new_faculty = Faculty(name=data.get('name'))
db.session.add(new_faculty)
db.session.commit()
return jsonify({'success': True})
```

### Frontend Code

Keep JavaScript clean and use modern syntax:

```javascript
// Good: async/await, proper error handling
async function saveFaculty(data) {
    try {
        const response = await fetch('/api/faculty', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSnackbar('Faculty added successfully!');
            location.reload();
        } else {
            showSnackbar('Error: ' + result.error);
        }
    } catch (error) {
        showSnackbar('Network error: ' + error.message);
    }
}


// Bad: Callbacks, poor error handling
function saveFaculty(data) {
    fetch('/api/faculty', {
        method: 'POST',
        body: JSON.stringify(data)
    }).then(r => r.json()).then(d => {
        alert('Done');
    });
}
```

### HTML Templates

Use semantic HTML and maintain consistency:

```html
<!-- Good: Semantic HTML, clear class names -->
<section class="section">
    <h3 class="section-title">Faculty Members</h3>
    <div class="user-list">
        {% for faculty in faculties %}
        <div class="list-item">
            <span class="material-icons list-icon">account_circle</span>
            <div class="list-content">
                <div class="list-title">{{ faculty.name }}</div>
                <div class="list-subtitle">{{ faculty.email }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
</section>


<!-- Bad: Divs for everything, inline styles -->
<div style="padding: 10px">
    <div style="font-size: 20px">Faculty</div>
    <div>
        {% for f in faculties %}
        <div style="padding: 5px">{{ f.name }}</div>
        {% endfor %}
    </div>
</div>
```

## 🌿 Git Workflow (If Using Git)

### Branch Naming

```bash
# Feature branches
git checkout -b feature/faculty-management
git checkout -b feature/attendance-reports

# Bug fixes
git checkout -b fix/login-error
git checkout -b fix/database-query

# Enhancements
git checkout -b enhance/mobile-ui
```

### Commit Messages

```bash
# Good: Clear, descriptive
git commit -m "Add faculty registration form with validation"
git commit -m "Fix: Resolve attendance calculation bug"
git commit -m "Update: Improve mobile menu animation"

# Bad: Vague
git commit -m "changes"
git commit -m "fix"
git commit -m "update"
```

### Before Pushing

```bash
# 1. Test your code
python app.py
# Test all features manually

# 2. Check for errors
python verify_setup.py

# 3. Commit your changes
git add .
git commit -m "Your descriptive message"

# 4. Pull latest changes
git pull origin main

# 5. Resolve conflicts if any

# 6. Push your branch
git push origin your-branch-name
```

## ✅ Pull Request Checklist

Before submitting a pull request:

- [ ] Code runs without errors
- [ ] All features work as expected
- [ ] Added comments to complex code
- [ ] Updated documentation if needed
- [ ] Tested on mobile view
- [ ] No console errors in browser
- [ ] Database migrations work
- [ ] API returns correct status codes
- [ ] Forms validate properly
- [ ] Error messages are user-friendly

## 📋 Code Review Guidelines

When reviewing others' code:

### What to Check

1. **Functionality**: Does it work correctly?
2. **Code Quality**: Is it clean and readable?
3. **Performance**: Are there any bottlenecks?
4. **Security**: Are inputs validated?
5. **UI/UX**: Is it user-friendly?
6. **Documentation**: Is it well-documented?

### How to Give Feedback

```
✅ Good Feedback:
"The function works well, but consider adding error handling 
for the database query. Example:
try:
    result = db.session.query(...)
except Exception as e:
    return error_response(e)"

❌ Bad Feedback:
"This is wrong"
"Doesn't work"
```

## 🐛 Reporting Issues

When you find a bug:

```markdown
**Bug Description:**
The faculty email field doesn't validate properly

**Steps to Reproduce:**
1. Go to Add Faculty page
2. Enter invalid email (e.g., "notanemail")
3. Click Submit
4. Form accepts invalid email

**Expected Behavior:**
Should show error message for invalid email

**Actual Behavior:**
Form submits with invalid email

**Screenshots:**
[Attach screenshot if helpful]

**Your Environment:**
- Browser: Chrome 120
- OS: Windows 11
- Python: 3.11
```

## 💡 Best Practices

### 1. Test Frequently

Don't wait until the end to test. Test after each feature:

```python
# After adding a route, test it immediately
@app.route('/api/test')
def test():
    return jsonify({'status': 'working'})

# Visit http://localhost:5000/api/test
```

### 2. Use the Existing Patterns

Study how existing features work:

```python
# Look at how Faculty API is structured
# Then follow the same pattern for Students

@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    # Same structure as api_faculty
    if request.method == 'POST':
        # Handle creation
        pass
    # Handle GET
    return jsonify(...)
```

### 3. Keep Functions Small

```python
# Good: One function, one purpose
def get_faculty_by_id(faculty_id):
    """Get single faculty member"""
    return Faculty.query.get_or_404(faculty_id)

def get_faculty_subjects(faculty_id):
    """Get subjects taught by faculty"""
    return SubjectAllocation.query.filter_by(
        faculty_id=faculty_id
    ).all()


# Bad: One function does everything
def get_faculty_data(faculty_id):
    """Get everything about faculty"""
    faculty = Faculty.query.get(faculty_id)
    subjects = SubjectAllocation.query.filter_by(...)
    schedules = ClassSchedule.query.filter_by(...)
    # ... too much in one function
```

### 4. Comment Complex Logic

```python
# Good: Complex logic explained
def calculate_attendance_percentage(student_id, subject_id):
    """
    Calculate attendance percentage for a student in a subject.
    
    Formula: (Present + Late) / Total * 100
    - Present and Late both count as attended
    - Excused absences are excluded from total
    """
    # Get all attendance records for this student-subject combo
    records = AttendanceRecord.query.join(
        AttendanceSession
    ).join(
        ClassSchedule
    ).filter(
        AttendanceRecord.student_id == student_id,
        ClassSchedule.subject_id == subject_id
    ).all()
    
    # Count different statuses
    total = len([r for r in records if r.status != 'excused'])
    attended = len([r for r in records if r.status in ['present', 'late']])
    
    # Calculate percentage
    return (attended / total * 100) if total > 0 else 0
```

### 5. Use Meaningful Variable Names

```python
# Good
student_attendance_percentage = 85.5
total_classes_held = 40
classes_attended = 34

# Bad
x = 85.5
t = 40
a = 34
```

## 🤝 Communication

### Daily Standup (Recommended)

Share with your team:
1. What did you work on yesterday?
2. What will you work on today?
3. Any blockers or issues?

### Ask for Help

Don't struggle alone! Ask when:
- Stuck for more than 30 minutes
- Not sure about the approach
- Need clarification on requirements
- Found a bug you can't fix

### Share Knowledge

When you learn something new:
- Share with the team
- Document in code comments
- Add to project wiki/notes

## 📚 Resources

- **Python**: https://docs.python.org/3/
- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **JavaScript**: https://developer.mozilla.org/
- **Material Design**: https://material.io/design
- **Git**: https://git-scm.com/doc

## ⚠️ Common Mistakes to Avoid

### 1. Not Checking for None

```python
# Bad
student = Student.query.get(student_id)
return jsonify(student.to_dict())  # Crashes if student is None

# Good
student = Student.query.get_or_404(student_id)
return jsonify(student.to_dict())
```

### 2. SQL Injection Risk

```python
# Bad
query = f"SELECT * FROM students WHERE usn = '{usn}'"
db.session.execute(query)

# Good
student = Student.query.filter_by(usn=usn).first()
```

### 3. Not Validating Input

```python
# Bad
email = request.json.get('email')
# Use email without validation

# Good
email = request.json.get('email', '').strip()
if not email or '@' not in email:
    return jsonify({'error': 'Invalid email'}), 400
```

### 4. Forgetting to Rollback

```python
# Bad
try:
    db.session.commit()
except:
    pass  # Database left in bad state

# Good
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
    return jsonify({'error': str(e)}), 400
```

## 🎯 Goals

Remember, the goal is to:
- ✅ Learn by doing
- ✅ Build something real
- ✅ Work as a team
- ✅ Create a portfolio project
- ✅ Have fun coding!

## 📞 Need Help?

1. Check the documentation files
2. Ask your teammates
3. Review similar working code
4. Ask your instructor
5. Search online (Stack Overflow, etc.)

---

**Happy Coding! 🚀**

Remember: Everyone was a beginner once. Don't be afraid to ask questions, make mistakes, and learn from them. That's how you grow as a developer!
