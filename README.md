# BCA BUB - Attendance Management System

A comprehensive Progressive Web App (PWA) built with Flask for managing college attendance. This project features a complete database schema with modular architecture designed for student collaboration.

## 🎯 Project Purpose

This is an **educational project** designed for BCA students to learn:
- Full-stack web development with Flask
- Database design with SQLAlchemy ORM
- RESTful API development
- Progressive Web Apps (PWA)
- Team collaboration and modular development

## ✨ Features

### Implemented (Base Framework)
- ✅ **Progressive Web App (PWA)** - Installable on mobile devices
- ✅ **Offline Support** - Service Worker for offline functionality
- ✅ **Native Android Look** - Material Design UI
- ✅ **Comprehensive Database Schema** - 14 interconnected tables
- ✅ **Modular Architecture** - Easy for teams to work on different modules
- ✅ **Mobile-First Design** - Optimized for smartphones
- ✅ **SQLAlchemy ORM** - Professional database management

### To Be Implemented (By Students)
- 🔨 User Authentication & Authorization
- 🔨 Faculty Management (CRUD)
- 🔨 Student Management (CRUD)
- 🔨 Class Schedule/Timetable
- 🔨 Attendance Taking Workflow
- 🔨 Test/Exam Management
- 🔨 Reports & Analytics
- 🔨 Bulk Import/Export

## 📊 Database Schema

The system includes **14 tables** organized into:

**Core Tables:**
- Roles, Users, Faculty, Students, Programs, Sections

**Academic Tables:**
- Semesters, Subjects, SubjectAllocation, ClassSchedule

**Attendance Tables:**
- AttendanceSession, AttendanceRecord

**Assessment Tables:**
- Test, TestResult

## Installation

1. **Clone or download this project**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the app:**
   - Open your browser and go to `http://localhost:5000`
   - On mobile: Use your computer's IP address (e.g., `http://192.168.1.100:5000`)

## Installing the PWA on Mobile

### Android:
1. Open the app in Chrome browser
2. Tap the menu (three dots)
3. Select "Install app" or "Add to Home Screen"
4. The app will install and appear on your home screen

### iOS (Safari):
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Tap "Add"

## 📁 Project Structure

```
AttendanceModule/
├── app.py                      # Main Flask application with routes
├── models.py                   # Database models (14 tables)
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview (this file)
├── STUDENT_GUIDE.md           # Detailed guide for students
├── QUICKSTART.md              # Quick setup instructions
├── static/
│   ├── manifest.json          # PWA manifest
│   ├── service-worker.js      # Service worker for offline
│   ├── css/style.css          # Material Design styles
│   ├── js/app.js              # Frontend JavaScript
│   └── icons/                 # App icons
├── templates/
│   ├── index.html             # Dashboard
│   ├── faculty.html           # Faculty management
│   ├── students.html          # Student management
│   └── attendance.html        # Attendance records
└── instance/
    └── attendance.db          # SQLite database (auto-created)
```

## 🗄️ Database Schema

**14 tables with proper relationships:**

1. **roles** - User role definitions
2. **users** - Authentication & user accounts
3. **faculties** - Faculty/teacher profiles
4. **students** - Student profiles
5. **programs** - Academic programs (BCA, MCA, etc.)
6. **sections** - Class sections
7. **semesters** - Academic terms
8. **subjects** - Course subjects
9. **subject_allocations** - Faculty-subject assignments
10. **class_schedules** - Timetable entries
11. **attendance_sessions** - Attendance taking sessions
12. **attendance_records** - Individual student attendance
13. **tests** - Test/exam information
14. **test_results** - Student test scores

All tables include:
- UUID primary keys
- Timestamps (created_at, updated_at)
- Soft delete capability
- Proper foreign key relationships

## 👥 For Students - Module Assignment

The project is divided into **9 modules** that students can work on independently:

1. **User Management** - Registration, authentication, profiles
2. **Faculty Management** - Faculty CRUD, profiles, assignments
3. **Student Management** - Student CRUD, enrollment, profiles  
4. **Schedule Management** - Timetable creation and management
5. **Attendance Management** - Taking attendance, reports
6. **Test Management** - Test creation, marks entry, analytics
7. **Reports & Analytics** - Various reports and dashboards
8. **Authentication** - Login/logout, role-based access
9. **PWA Features** - Enhanced offline support, notifications

**📖 See STUDENT_GUIDE.md for detailed instructions on each module**

## 🔌 API Structure (To Be Implemented)

### Current (Base)
- `GET /` - Dashboard
- `GET /faculty` - Faculty list
- `GET /students` - Students list
- `GET /attendance` - Attendance sessions

### To Be Added (By Students)
```
Faculty APIs:
POST   /api/faculty
GET    /api/faculty/<id>
PUT    /api/faculty/<id>
DELETE /api/faculty/<id>

Student APIs:
POST   /api/students
GET    /api/students/<id>
PUT    /api/students/<id>

Attendance APIs:
POST   /api/attendance/session
POST   /api/attendance/record
GET    /api/attendance/reports

(See STUDENT_GUIDE.md for complete API specifications)
```

## Adding App Icons

To complete the PWA installation, you need to add app icons in the `static/icons/` folder:

- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

You can use online tools like https://realfavicongenerator.net/ to generate all sizes from a single image.

## 🎓 Learning Objectives

By working on this project, students will learn:

- **Backend Development**: Flask, SQLAlchemy, RESTful APIs
- **Frontend Development**: HTML5, CSS3, JavaScript, Material Design
- **Database Design**: Normalization, relationships, constraints
- **PWA Development**: Service workers, offline support, installability
- **Version Control**: Git, collaborative development
- **Project Management**: Modular architecture, documentation
- **Best Practices**: Code organization, error handling, security

## 🛠️ Technologies Used

- **Backend**: Python 3.x, Flask 3.0
- **Database**: SQLAlchemy 3.1, SQLite (can migrate to PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **UI Framework**: Material Design (custom CSS)
- **PWA**: Service Worker, Web App Manifest
- **Icons**: Material Icons

## 🔐 Security Notes

⚠️ **Current Status**: Development mode (not production-ready)

**Before deploying to production:**
- [ ] Change SECRET_KEY in config.py
- [ ] Implement proper authentication
- [ ] Add password hashing (bcrypt/argon2)
- [ ] Enable HTTPS/SSL
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Add CSRF protection
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization
- [ ] Set up proper logging
- [ ] Configure CORS if needed

## 🌐 Browser Support

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari (iOS 11.3+)
- ✅ Samsung Internet
- ✅ Any modern browser supporting PWA

## 📚 Documentation

- **README.md** - Project overview (this file)
- **STUDENT_GUIDE.md** - Detailed guide for students working on modules
- **QUICKSTART.md** - Quick setup and installation
- **models.py** - Inline documentation of all database models
- **app.py** - Commented code explaining routes

## 🤝 Contributing

This is an educational project. Students should:
1. Read the STUDENT_GUIDE.md
2. Choose a module to work on
3. Create a branch for your feature
4. Write clean, documented code
5. Test thoroughly before merging
6. Collaborate with team members

## 📝 Project Status

- ✅ **Phase 1**: Base framework, database schema, PWA setup - **COMPLETED**
- 🔨 **Phase 2**: Module development by students - **IN PROGRESS**
- ⏳ **Phase 3**: Integration and testing - **PENDING**
- ⏳ **Phase 4**: Deployment and documentation - **PENDING**

## 📧 Support & Questions

For project-related questions:
- Check the STUDENT_GUIDE.md first
- Ask your team members
- Consult your instructor
- Review Flask and SQLAlchemy documentation

## 📄 License

This is an educational project. Free to use for learning purposes.
