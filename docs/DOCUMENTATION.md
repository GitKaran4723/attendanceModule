# 📚 BCA BUB Attendance Module - Complete Documentation

## 📖 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Implementation Synopsis](#implementation-synopsis)
4. [Database Models](#database-models)
5. [User Roles & Access Control](#user-roles--access-control)
6. [Core Features](#core-features)
7. [API Reference](#api-reference)
8. [Installation & Setup](#installation--setup)
9. [Configuration](#configuration)
10. [Testing Guide](#testing-guide)

---

## 📋 Project Overview

### What is BCA BUB Attendance Module?

The **BCA BUB Attendance Module** is a comprehensive, production-ready Progressive Web Application (PWA) designed for managing college attendance, faculty workload, student performance tracking, and parent monitoring. Built with Flask (Python), SQLAlchemy ORM, and modern web technologies, this system serves as both a functional application and an educational project for BCA students.

### Key Highlights

- ✅ **16 Database Tables** with complete relationships
- ✅ **4 User Roles** (Admin, HOD, Faculty, Student/Parent)
- ✅ **Progressive Web App** - Installable on mobile devices
- ✅ **Work Diary System** with approval workflow
- ✅ **Student Check-In/Check-Out** tracking
- ✅ **Parent Dashboard** for real-time monitoring
- ✅ **Bulk Import** functionality (CSV/Excel)
- ✅ **RESTful API** architecture
- ✅ **Material Design UI** with mobile-first approach

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Flask 3.0 | Web framework |
| **ORM** | SQLAlchemy 3.1 | Database management |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | Data storage |
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **UI Framework** | Material Design | Modern, responsive UI |
| **PWA** | Service Worker, Manifest | Offline support |
| **Authentication** | Flask Sessions, Werkzeug | Security |
| **Data Import** | Pandas, OpenPyXL | Bulk operations |

---

## 🏗️ System Architecture

### Application Structure

```
AttendanceModule/
├── Core Application Files
│   ├── app.py                  # Main Flask application (4400+ lines)
│   ├── models.py               # Database models (1133 lines)
│   ├── auth.py                 # Authentication & authorization
│   ├── config.py               # Configuration settings
│   └── requirements.txt        # Python dependencies
│
├── Database & Migrations
│   ├── instance/
│   │   └── attendance.db       # SQLite database
│   └── migrations/             # Database migrations
│
├── Frontend Assets
│   ├── static/
│   │   ├── manifest.json       # PWA manifest
│   │   ├── service-worker.js   # Offline support
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   └── icons/              # App icons
│   │
│   └── templates/
│       ├── admin/              # Admin pages
│       ├── faculty/            # Faculty pages
│       ├── student/            # Student pages
│       └── parent/             # Parent pages
│
├── Utility Scripts
│   ├── setup.py                # Automated setup
│   ├── create_users.py         # User creation
│   ├── update_database.py      # Database utilities
│   └── verify_setup.py         # Setup verification
│
└── Documentation
    ├── README.md               # Project overview
    ├── DOCUMENTATION.md        # This file
    ├── STUDENT_GUIDE.md        # Student development guide
    ├── WORK_DIARY_GUIDE.md     # Work diary feature guide
    ├── ADMIN_IMPLEMENTATION.md # Admin features
    └── TESTING_GUIDE.md        # Testing documentation
```

---

## 🎯 Implementation Synopsis

### 1. Authentication & Authorization System

**Implementation Details:**
- **Module:** `auth.py`
- **Lines of Code:** ~200 lines
- **Database Tables:** `users`, `roles`

**Features Implemented:**
1. **Secure Password Management**
   - Password hashing using Werkzeug's `generate_password_hash` and `check_password_hash`
   - Salted hashes for enhanced security
   - Password validation on login

2. **Session Management**
   - Flask session-based authentication
   - Automatic session cleanup on logout
   - Session timeout configuration

3. **Role-Based Access Control (RBAC)**
   - 4 predefined roles: Admin, HOD, Faculty, Student
   - Route protection decorators:
     - `@login_required` - Requires authentication
     - `@admin_required` - Admin-only access
     - `@faculty_required` - Faculty and above
     - `@hod_required` - HOD and Admin only
   
4. **Permission Checking Functions**
   - `can_approve_diary()` - Check diary approval rights
   - `can_edit_diary()` - Check diary edit permissions
   - `can_view_all_diaries()` - Check view all permissions

**Login Flow:**
```
User enters credentials → Validate credentials → Check password hash
→ Create session → Redirect based on role
```

**Special Features:**
- Parent login using student USN with `is_parent_view` session flag
- Login type selection (Student/Parent)

---

### 2. Student & Faculty Management

**Implementation Details:**
- **Database Tables:** `students`, `faculties`, `users`
- **Routes:** 10+ routes for CRUD operations
- **Templates:** Admin forms for add/edit

**Student Management Features:**

1. **Student Registration**
   - Personal details (first name, last name, DOB, address)
   - Academic details (program, section, semester, USN/roll number)
   - Guardian information (name, phone)
   - User account creation with secure password

2. **Bulk Student Import**
   - CSV/Excel file upload
   - Automatic user account creation
   - Data validation and duplicate checking
   - Error reporting and success logging

3. **Student Profile Management**
   - Update personal information
   - Change section/program
   - Track enrollment status
   - Soft delete for data integrity

**Faculty Management Features:**

1. **Faculty Registration**
   - Personal details (first name, last name, employee ID)
   - Professional details (department, qualification, designation)
   - Employment information (type, join date, HOD status)
   - User account with role assignment

2. **Subject Allocation**
   - Assign subjects to faculty
   - Link faculty to sections
   - Track allocation type (primary/co-teacher)

3. **Faculty Dashboard**
   - View assigned subjects and sections
   - Access work diary
   - Manage attendance sessions
   - Track class schedules

---

### 3. Attendance Management System

**Implementation Details:**
- **Database Tables:** `attendance_sessions`, `attendance_records`, `class_schedules`
- **Routes:** 15+ routes for attendance operations
- **Auto-generation:** Work diary entries from attendance

**Core Attendance Features:**

1. **Attendance Session Management**
   - Create session linked to class schedule
   - Auto-populate student list from section
   - Support for theory and practical classes
   - Track topics taught during session
   - Unique diary number generation

2. **Attendance Recording**
   - Mark students: Present, Absent, Late, Excused
   - Add remarks for individual students
   - Bulk status updates
   - Real-time attendance statistics

3. **Attendance Analytics**
   - Overall attendance percentage per student
   - Subject-wise attendance tracking
   - Section-wise attendance reports
   - Date range filtering

4. **Approval Workflow**
   - Draft → Finalized → Approved flow
   - HOD/Admin approval required
   - Approval timestamps and remarks
   - Edit restrictions after approval

**Attendance Calculation:**
```
Attendance % = (Total Present + Late) / Total Sessions × 100
```

---

### 4. Work Diary System

**Implementation Details:**
- **Database Table:** `work_diaries`
- **Lines of Code:** ~400 lines
- **Auto-generation:** Linked to attendance sessions
- **Routes:** 12+ diary management routes

**Work Diary Features:**

1. **Automatic Diary Creation**
   - Auto-created when attendance is taken
   - Diary number format: `WD-YYYY-NNNN` (e.g., WD-2025-0001)
   - Links to attendance session
   - Pre-fills: subject, section, date, time, student count

2. **Manual Diary Entries**
   - Non-class activities:
     - Invigilation
     - Exam Duty
     - Department Meetings
     - Committee Work
     - Counseling Sessions
     - Seminars/Workshops
   - Custom activity descriptions
   - Duration tracking
   - Location/venue information

3. **Diary Workflow**
   ```
   Draft → Edit/Add Topics → Submit → HOD/Admin Review → Approved/Rejected
   ```

4. **Approval Management**
   - HOD and Admin can approve/reject
   - Approval remarks
   - Email notification (optional)
   - Approval timestamp tracking

5. **Faculty Work Summary**
   - Date-wise work log
   - Total hours calculation
   - Activity breakdown
   - Monthly/semester reports
   - Export to Excel/PDF

**Work Diary UI Features:**
- Color-coded status badges (Draft/Submitted/Approved/Rejected)
- Filter by date range, status, faculty
- Sort by diary number, date, faculty name
- Download reports (XLSX/CSV format)
- Separate views for Admin and Faculty

---

### 5. Student Check-In/Check-Out System

**Implementation Details:**
- **Database Table:** `student_attendance` (daily check-in tracking)
- **Real-time Status:** In Campus / Checked Out / Absent
- **Templates:** Student dashboard with check-in controls

**Check-In/Out Features:**

1. **Daily Check-In**
   - Students check in when arriving on campus
   - Timestamp recorded (check-in time)
   - GPS location tracking (optional)
   - Device information logged

2. **Check-Out**
   - Students check out when leaving campus
   - Checkout timestamp
   - Duration on campus calculated
   - Reason for early departure (optional)

3. **Status Tracking**
   - Real-time status display:
     - 🟢 **In Campus** - Checked in, not checked out
     - 🔵 **Checked Out** - Left campus
     - 🔴 **Absent** - Not checked in
   
4. **Parent Notification**
   - Automatic notifications when:
     - Student checks in
     - Student checks out
     - Student marked absent in class
     - Student doesn't check in by specific time

5. **Analytics**
   - Daily attendance patterns
   - Average time on campus
   - Late arrival tracking
   - Early departure monitoring

---

### 6. Parent Dashboard & Monitoring

**Implementation Details:**
- **Templates:** `parent/dashboard.html`, `parent/profile.html`, `parent/contact_teacher.html`
- **Access:** Via student USN login with "Parent" selection
- **Session Flag:** `is_parent_view = True`

**Parent Dashboard Features:**

1. **Real-Time Student Monitoring**
   - Current check-in/check-out status
   - Live attendance percentage
   - Subject-wise attendance breakdown
   - Recent attendance records

2. **Academic Performance**
   - Test scores and results
   - Overall grade tracking
   - Subject-wise performance
   - Progress charts

3. **Attendance Analytics**
   - Monthly attendance calendar
   - Attendance trend graphs
   - Subject-wise attendance comparison
   - Absent days listing

4. **Communication**
   - Contact class teacher functionality
   - Message faculty directly
   - View announcements
   - Access parent-teacher meeting schedules

5. **Notifications**
   - Absence alerts
   - Low attendance warnings (<75%)
   - Test result notifications
   - Important announcements

**Parent Access Control:**
- Read-only access (cannot modify data)
- No check-in/check-out capabilities
- Restricted to own child's data
- Secure authentication required

---

### 7. Program, Section & Subject Management

**Implementation Details:**
- **Database Tables:** `programs`, `sections`, `subjects`, `subject_allocations`
- **Features:** Hierarchical curriculum structure

**Program Management:**

1. **Program Setup**
   - Program code (e.g., BCA, MCA)
   - Program name
   - Duration (years/semesters)
   - Academic structure definition

2. **Section Management**
   - Section naming (A, B, C, etc.)
   - Link to program
   - Year of study
   - Current semester tracking
   - Academic year assignment
   - Class teacher assignment

**Subject Management:**

1. **Subject Hierarchy**
   ```
   Subject
   ├── Unit 1
   │   ├── Chapter 1.1
   │   │   └── Concepts
   │   └── Chapter 1.2
   ├── Unit 2
   └── ...
   ```

2. **Subject Details**
   - Subject code (unique identifier)
   - Subject name
   - Credits
   - Type (Theory/Practical/Mixed)
   - Semester assignment
   - Total teaching hours
   - Specialization flag (elective subjects)

3. **Curriculum Management**
   - Units within subjects
   - Chapters within units
   - Concepts within chapters
   - Topic tracking in attendance

4. **Subject Allocation**
   - Assign faculty to subjects
   - Link to specific sections
   - Allocation type (primary/co-teacher)
   - Semester-wise allocation

---

### 8. Bulk Import System

**Implementation Details:**
- **Database Table:** `import_logs`
- **Supported Formats:** CSV, Excel (.xlsx, .xls)
- **Dependencies:** Pandas, OpenPyXL
- **Template:** `admin_import.html`

**Import Types Supported:**

1. **Student Import**
   - Required fields: first_name, last_name, email, usn, program, section
   - Optional fields: phone, dob, address, guardian_name, guardian_phone
   - Auto-creates user accounts with default passwords
   - Validates USN uniqueness

2. **Faculty Import**
   - Required fields: first_name, last_name, email, employee_id
   - Optional fields: phone, department, qualification, designation
   - Auto-creates user accounts
   - Assigns faculty role

3. **Subject Import**
   - Required fields: subject_code, subject_name, program
   - Optional fields: credits, semester, type, description
   - Validates code uniqueness
   - Links to program

4. **Schedule Import**
   - Required fields: subject_code, faculty_email, section, date, start_time, end_time
   - Auto-links to existing records
   - Validates time conflicts

**Import Features:**

1. **Validation**
   - Data type checking
   - Required field validation
   - Unique constraint checking
   - Foreign key validation
   - Format validation (dates, emails)

2. **Error Handling**
   - Row-by-row error tracking
   - Detailed error messages
   - Partial import support
   - Error log generation
   - Rollback on critical errors

3. **Import Logging**
   - Import history tracking
   - Success/failure statistics
   - Error log storage
   - Imported by tracking
   - Timestamp recording

4. **Sample Templates**
   - Pre-formatted CSV templates in `sample_imports/`
   - Header row included
   - Example data provided
   - Documentation comments

---

### 9. Class Schedule & Timetable

**Implementation Details:**
- **Database Table:** `class_schedules`
- **Features:** Weekly timetable, room assignment, conflict detection

**Schedule Features:**

1. **Timetable Creation**
   - Day-wise schedule
   - Period-wise assignment
   - Subject allocation
   - Faculty assignment
   - Room allocation

2. **Schedule Attributes**
   - Date and time (start/end)
   - Subject and faculty
   - Section
   - Room/location
   - Class type (theory/practical)
   - Semester linkage

3. **Conflict Detection**
   - Faculty time conflict checking
   - Room booking conflicts
   - Section scheduling conflicts
   - Automatic alerts

4. **Schedule Views**
   - Faculty timetable view
   - Section timetable view
   - Room utilization view
   - Daily schedule view

---

### 10. Testing & Assessment System

**Implementation Details:**
- **Database Tables:** `tests`, `test_results`
- **Features:** Test creation, marks entry, analytics

**Test Management:**

1. **Test Creation**
   - Test name/title
   - Subject and section
   - Test date
   - Maximum marks
   - Semester assignment

2. **Marks Entry**
   - Student-wise marks
   - Bulk marks entry
   - Validation (marks ≤ max marks)
   - Remarks/comments

3. **Result Analytics**
   - Class average
   - Top performers
   - Subject-wise performance
   - Student progress tracking
   - Grade distribution

---

### 11. Progressive Web App (PWA)

**Implementation Details:**
- **Files:** `manifest.json`, `service-worker.js`, `app.js`
- **Features:** Installability, offline support, native feel

**PWA Features:**

1. **Installability**
   - Add to home screen (Android)
   - Add to home screen (iOS)
   - Standalone mode
   - Custom splash screen
   - App icons (multiple sizes)

2. **Offline Support**
   - Service worker caching
   - Offline fallback page
   - Cache-first strategy for static assets
   - Network-first for API calls
   - Background sync ready

3. **Native App Experience**
   - No browser UI in standalone mode
   - Custom app icon
   - Full screen mode
   - Status bar theming
   - Smooth animations

4. **Manifest Configuration**
   ```json
   {
     "name": "BCA BUB Attendance",
     "short_name": "Attendance",
     "start_url": "/",
     "display": "standalone",
     "background_color": "#1976D2",
     "theme_color": "#1976D2"
   }
   ```

---

### 12. Admin Configuration & Settings

**Implementation Details:**
- **Template:** `admin_config.html`
- **Features:** System-wide settings management

**Configuration Options:**

1. **Academic Settings**
   - Current academic year
   - Current semester
   - Semester start/end dates
   - Attendance minimum threshold

2. **Notification Settings**
   - Email notifications on/off
   - Parent notification triggers
   - Low attendance threshold
   - Absence alert timing

3. **System Settings**
   - Application name
   - Institution details
   - Logo upload
   - Theme customization

4. **Attendance Rules**
   - Minimum attendance percentage required
   - Late mark threshold (arrival time)
   - Excuse approval workflow
   - Attendance calculation method

---

### 13. Reporting & Analytics

**Implementation Details:**
- **Features:** Multiple report types, export functionality

**Report Types:**

1. **Attendance Reports**
   - Student-wise attendance
   - Section-wise attendance
   - Subject-wise attendance
   - Date range reports
   - Defaulter list (below threshold)

2. **Faculty Reports**
   - Work diary summary
   - Teaching hours analysis
   - Subject allocation report
   - Monthly workload report

3. **Performance Reports**
   - Test results summary
   - Class performance analysis
   - Subject-wise averages
   - Student progress reports

4. **Export Options**
   - Excel (.xlsx)
   - CSV
   - PDF (planned)
   - Print-friendly views

---

### 14. UI/UX Design

**Implementation Details:**
- **Framework:** Material Design
- **Approach:** Mobile-first responsive design
- **Lines of CSS:** 900+ lines

**Design Features:**

1. **Material Design Components**
   - Cards
   - FABs (Floating Action Buttons)
   - Bottom navigation
   - Dialogs/Modals
   - Snackbar notifications
   - Progress indicators
   - Chips and badges

2. **Color Scheme**
   - Primary: Blue (#1976D2)
   - Faculty: Purple theme
   - Admin: Blue theme
   - Student: Green theme
   - Parent: Orange theme
   - Status colors for badges

3. **Responsive Design**
   - Mobile breakpoint: 768px
   - Tablet optimization
   - Desktop layout
   - Touch-friendly buttons (min 48px)
   - Swipe gestures

4. **Accessibility**
   - ARIA labels
   - Keyboard navigation
   - Color contrast compliance
   - Screen reader support
   - Focus indicators

---

## 🗄️ Database Models

### Complete Database Schema (16 Tables)

#### 1. **roles**
Base user role definitions.
```
- role_id (PK)
- role_name (Admin, HOD, Faculty, Student)
- description
- created_at, updated_at
```

#### 2. **users**
User authentication and basic info.
```
- user_id (PK)
- username (unique)
- email (unique)
- password_hash
- role_id (FK → roles)
- is_active
- last_login_at
- created_at, updated_at
```

#### 3. **faculties**
Faculty profile information.
```
- faculty_id (PK)
- user_id (FK → users, unique)
- employee_id (unique)
- first_name, last_name
- phone, email
- department, qualification, designation
- employment_type (full_time/part_time)
- join_date
- is_hod
- status
- created_at, updated_at
```

#### 4. **students**
Student profile and academic details.
```
- student_id (PK)
- user_id (FK → users, unique)
- roll_number / usn (unique)
- first_name, last_name
- date_of_birth
- email, phone
- address
- guardian_name, guardian_phone
- program_id (FK → programs)
- section_id (FK → sections)
- semester_id (FK → semesters)
- admission_year
- current_semester
- status, is_active
- gender
- created_at, updated_at
```

#### 5. **programs**
Academic programs (BCA, MCA, etc.).
```
- program_id (PK)
- program_code (unique)
- program_name
- duration (years)
- created_at, updated_at
```

#### 6. **sections**
Class sections within programs.
```
- section_id (PK)
- section_name
- program_id (FK → programs)
- year_of_study
- academic_year
- current_semester
- class_teacher_id (FK → faculties)
- created_at, updated_at
```

#### 7. **semesters**
Academic semesters/terms.
```
- semester_id (PK)
- name (e.g., "Semester 1 - 2025")
- start_date, end_date
- academic_year
- created_at, updated_at
```

#### 8. **subjects**
Course subjects with curriculum.
```
- subject_id (PK)
- subject_code (unique)
- subject_name
- credits
- subject_type (theory/practical/mixed)
- program_id (FK → programs)
- semester_id
- description
- total_hours
- is_specialization
- created_at, updated_at
```

#### 9. **units**
Units within subjects.
```
- unit_id (PK)
- subject_id (FK → subjects)
- unit_number
- unit_name
- description
- created_at, updated_at
```

#### 10. **chapters**
Chapters within units.
```
- chapter_id (PK)
- unit_id (FK → units)
- chapter_number
- chapter_name
- description
- created_at, updated_at
```

#### 11. **concepts**
Concepts within chapters.
```
- concept_id (PK)
- chapter_id (FK → chapters)
- concept_name
- description
- created_at, updated_at
```

#### 12. **subject_allocations**
Faculty-subject assignments.
```
- allocation_id (PK)
- subject_id (FK → subjects)
- faculty_id (FK → faculties)
- section_id (FK → sections)
- semester_id (FK → semesters)
- allocation_type (primary/co-teacher)
- created_at, updated_at
```

#### 13. **class_schedules**
Timetable entries.
```
- schedule_id (PK)
- subject_id (FK → subjects)
- faculty_id (FK → faculties)
- section_id (FK → sections)
- room_id
- date
- start_time, end_time
- class_type (theory/practical)
- semester_id (FK → semesters)
- created_at, updated_at
```

#### 14. **attendance_sessions**
Attendance taking sessions.
```
- attendance_session_id (PK)
- schedule_id (FK → class_schedules)
- taken_by_user_id (FK → users)
- taken_at
- status (draft/finalized)
- approved_by (FK → users)
- approved_at
- topic_taught
- diary_number (unique)
- created_at, updated_at
```

#### 15. **attendance_records**
Individual student attendance.
```
- record_id (PK)
- attendance_session_id (FK → attendance_sessions)
- student_id (FK → students)
- status (present/absent/late/excused)
- remarks
- created_at, updated_at
```

#### 16. **tests**
Test/exam information.
```
- test_id (PK)
- test_name
- subject_id (FK → subjects)
- faculty_id (FK → faculties)
- section_id (FK → sections)
- semester_id (FK → semesters)
- test_date
- max_marks
- created_at, updated_at
```

#### 17. **test_results**
Student test results.
```
- result_id (PK)
- test_id (FK → tests)
- student_id (FK → students)
- marks_obtained
- remarks
- created_at, updated_at
```

#### 18. **work_diaries**
Faculty work diary entries.
```
- diary_id (PK)
- diary_number (unique, format: WD-YYYY-NNNN)
- faculty_id (FK → faculties)
- subject_id (FK → subjects)
- section_id (FK → sections)
- semester_id (FK → semesters)
- academic_year
- date
- start_time, end_time
- duration_hours
- activity_type (theory_class/practical_class/invigilation/etc.)
- attendance_session_id (FK → attendance_sessions)
- students_present, total_students
- activity_title, activity_description
- location
- topics_covered
- status (draft/submitted/approved/rejected)
- submitted_at
- approved_by (FK → users)
- approved_at
- approval_remarks
- attachment_url
- created_at, updated_at
```

#### 19. **import_logs**
Bulk import audit trail.
```
- import_id (PK)
- import_type (faculty/student/subject/schedule/etc.)
- imported_by (FK → users)
- file_name
- total_rows, successful_rows, failed_rows
- status (processing/completed/failed/partial)
- error_log (JSON)
- import_data (JSON backup)
- created_at, updated_at
```

#### 20. **student_subject_enrollments**
Student enrollment in specialization subjects.
```
- enrollment_id (PK)
- student_id (FK → students)
- subject_id (FK → subjects)
- enrollment_date
- status (active/dropped)
- created_at, updated_at
```

### Database Relationships

```
roles (1) ←→ (M) users
users (1) ←→ (1) faculties
users (1) ←→ (1) students
programs (1) ←→ (M) sections
programs (1) ←→ (M) subjects
sections (1) ←→ (M) students
sections (1) ←→ (M) class_schedules
subjects (1) ←→ (M) units
units (1) ←→ (M) chapters
chapters (1) ←→ (M) concepts
subjects (1) ←→ (M) subject_allocations
faculties (1) ←→ (M) subject_allocations
sections (1) ←→ (M) subject_allocations
class_schedules (1) ←→ (M) attendance_sessions
attendance_sessions (1) ←→ (M) attendance_records
students (1) ←→ (M) attendance_records
faculties (1) ←→ (M) work_diaries
attendance_sessions (1) ←→ (1) work_diaries
```

---

## 👥 User Roles & Access Control

### Role Hierarchy

```
Admin (Highest Level)
  ├── Full system access
  ├── User management
  ├── Configuration settings
  └── All approvals

HOD (Head of Department)
  ├── Faculty management
  ├── Work diary approval
  ├── Attendance oversight
  └── Section management

Faculty
  ├── Attendance taking
  ├── Work diary creation
  ├── Test management
  └── Student viewing

Student/Parent (Read Access)
  ├── View attendance
  ├── View test results
  ├── Profile viewing
  └── Dashboard access
```

### Role-Specific Features

| Feature | Admin | HOD | Faculty | Student | Parent |
|---------|-------|-----|---------|---------|--------|
| Manage Users | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage Faculty | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage Students | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage Subjects | ✅ | ✅ | ❌ | ❌ | ❌ |
| Bulk Import | ✅ | ❌ | ❌ | ❌ | ❌ |
| Take Attendance | ✅ | ✅ | ✅ | ❌ | ❌ |
| Create Work Diary | ✅ | ✅ | ✅ | ❌ | ❌ |
| Approve Work Diary | ✅ | ✅ | ❌ | ❌ | ❌ |
| Enter Test Marks | ✅ | ✅ | ✅ | ❌ | ❌ |
| View All Attendance | ✅ | ✅ | ✅ | ❌ | ❌ |
| View Own Attendance | ✅ | ✅ | ✅ | ✅ | ✅ |
| Check In/Out | ❌ | ❌ | ❌ | ✅ | ❌ |
| Contact Teacher | ❌ | ❌ | ❌ | ✅ | ✅ |
| System Config | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 🚀 API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET/POST | `/login` | User login | Public |
| GET | `/logout` | User logout | Authenticated |

### Admin Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/admin/dashboard` | Admin dashboard | Admin |
| GET | `/admin/faculty` | List all faculty | Admin, HOD |
| GET/POST | `/admin/faculty/add` | Add new faculty | Admin, HOD |
| GET/POST | `/admin/faculty/<id>/edit` | Edit faculty | Admin, HOD |
| DELETE | `/api/faculty/<id>` | Delete faculty | Admin |
| GET | `/admin/students` | List all students | Admin, HOD |
| GET/POST | `/admin/student/add` | Add new student | Admin, HOD |
| GET/POST | `/admin/student/<id>/edit` | Edit student | Admin, HOD |
| DELETE | `/api/student/<id>` | Delete student | Admin |
| GET | `/admin/subjects` | List all subjects | Admin, HOD |
| GET/POST | `/admin/subject/add` | Add new subject | Admin, HOD |
| GET/POST | `/admin/subject/<id>/edit` | Edit subject | Admin, HOD |
| DELETE | `/api/subject/<id>` | Delete subject | Admin |
| GET | `/admin/sections` | Manage sections | Admin, HOD |
| GET | `/admin/batches` | Manage programs | Admin, HOD |
| GET | `/admin/assign-students` | Student assignment | Admin, HOD |
| GET | `/admin/import` | Bulk import interface | Admin |
| POST | `/api/admin/import` | Process bulk import | Admin |
| GET | `/admin/config` | System configuration | Admin |

### Work Diary Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/work-diary` | List work diaries | Faculty+ |
| GET/POST | `/work-diary/create` | Create work diary | Faculty+ |
| GET/POST | `/work-diary/<id>/edit` | Edit work diary | Owner/Admin |
| GET | `/api/work-diary` | List diaries (JSON) | Faculty+ |
| POST | `/api/work-diary` | Create diary (JSON) | Faculty+ |
| GET | `/api/work-diary/<id>` | Get diary (JSON) | Faculty+ |
| PUT | `/api/work-diary/<id>` | Update diary (JSON) | Owner/Admin |
| DELETE | `/api/work-diary/<id>` | Delete diary | Owner/Admin |
| POST | `/api/work-diary/<id>/submit` | Submit for approval | Owner |
| POST | `/api/work-diary/<id>/approve` | Approve diary | Admin/HOD |
| POST | `/api/work-diary/<id>/reject` | Reject diary | Admin/HOD |
| GET | `/admin/work-diary` | Admin diary view | Admin/HOD |

### Attendance Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/faculty/my-classes` | View my classes | Faculty+ |
| GET | `/faculty/attendance/<schedule_id>` | Take attendance | Faculty+ |
| POST | `/api/attendance/session/create` | Create session | Faculty+ |
| POST | `/api/attendance/record` | Mark attendance | Faculty+ |
| POST | `/api/attendance/finalize` | Finalize session | Faculty+ |
| GET | `/api/attendance/reports` | Attendance reports | Faculty+ |

### Student Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/student/dashboard` | Student dashboard | Student |
| POST | `/api/student/checkin` | Check in | Student |
| POST | `/api/student/checkout` | Check out | Student |
| GET | `/student/attendance` | My attendance | Student |
| GET | `/student/results` | My test results | Student |
| GET | `/student/profile` | My profile | Student |

### Parent Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/parent/dashboard` | Parent dashboard | Parent |
| GET | `/parent/profile` | Student profile | Parent |
| GET | `/parent/contact-teacher` | Contact teacher | Parent |

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (included with Python)
- Modern web browser

### Quick Setup (Automated)

```bash
# Windows
start.bat

# Or run directly
python setup.py
```

### Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python app.py
# (Press Ctrl+C after database is created)

# 3. Create initial users
python create_users.py

# 4. Run application
python app.py

# 5. Access application
# Browser: http://localhost:5000
# Mobile: http://YOUR_IP_ADDRESS:5000
```

### Default Login Credentials

After running `create_users.py`:

```
Admin:
  Username: admin
  Password: admin123

HOD:
  Username: hod
  Password: hod123

Faculty:
  Username: faculty1
  Password: faculty123

Student:
  Username: student1
  Password: student123
```

### Installing as PWA on Mobile

**Android (Chrome):**
1. Open app in Chrome
2. Tap menu (⋮)
3. Select "Install app" or "Add to Home Screen"
4. App icon appears on home screen

**iOS (Safari):**
1. Open app in Safari
2. Tap Share button
3. Select "Add to Home Screen"
4. Tap "Add"

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file based on `.env.example`:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///instance/attendance.db

# Session Configuration
SESSION_LIFETIME=3600

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Attendance Configuration
MINIMUM_ATTENDANCE_PERCENTAGE=75
LATE_THRESHOLD_MINUTES=15

# Notification Configuration
ENABLE_PARENT_NOTIFICATIONS=True
LOW_ATTENDANCE_THRESHOLD=75
```

### Database Configuration

**Development (SQLite):**
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/attendance.db'
```

**Production (PostgreSQL):**
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/attendance'
```

### PWA Configuration

Edit `static/manifest.json`:

```json
{
  "name": "Your Institution Name - Attendance",
  "short_name": "Attendance",
  "description": "Attendance management system",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1976D2",
  "theme_color": "#1976D2",
  "icons": [...]
}
```

---

## 🧪 Testing Guide

### Manual Testing Steps

1. **Authentication Testing**
   ```
   - Test login with valid credentials
   - Test login with invalid credentials
   - Test role-based redirects
   - Test logout functionality
   - Test session persistence
   ```

2. **Attendance Testing**
   ```
   - Create attendance session
   - Mark students present/absent
   - Verify attendance calculations
   - Test approval workflow
   - Verify auto-diary creation
   ```

3. **Work Diary Testing**
   ```
   - Create manual diary entry
   - Verify auto-diary from attendance
   - Test submission workflow
   - Test approval/rejection
   - Verify diary numbering
   ```

4. **Bulk Import Testing**
   ```
   - Import sample student CSV
   - Import sample faculty CSV
   - Verify error handling
   - Check import logs
   - Verify data integrity
   ```

5. **Parent Dashboard Testing**
   ```
   - Login as parent
   - Verify read-only access
   - Check real-time status
   - Test notifications
   - Verify attendance analytics
   ```

### Sample Test Data

Use files in `sample_imports/` folder:
- `students_template.csv`
- `faculty_template.csv`
- `subjects_template.csv`
- `schedules_template.csv`

### Automated Testing (Future)

```bash
# Unit tests
python -m pytest tests/

# Coverage report
python -m pytest --cov=.
```

---

## 📝 Additional Resources

### Related Documentation

- [README.md](README.md) - Project overview
- [STUDENT_GUIDE.md](STUDENT_GUIDE.md) - Guide for student developers
- [WORK_DIARY_GUIDE.md](WORK_DIARY_GUIDE.md) - Work diary feature details
- [ADMIN_IMPLEMENTATION.md](ADMIN_IMPLEMENTATION.md) - Admin features guide
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

### Support & Community

- **Issues:** Report bugs and request features
- **Discussions:** Ask questions and share ideas
- **Documentation:** Explore guides and tutorials

### License

This project is created for educational purposes. Free to use for learning.

---

## 🎯 Future Enhancements

### Planned Features

1. **Mobile App** (React Native / Flutter)
2. **Email Notifications** (SMTP integration)
3. **SMS Alerts** (Twilio integration)
4. **PDF Report Generation**
5. **Biometric Attendance** (Face recognition)
6. **QR Code Check-In**
7. **Analytics Dashboard** (Charts and graphs)
8. **API Documentation** (Swagger/OpenAPI)
9. **Unit Tests** (pytest)
10. **CI/CD Pipeline** (GitHub Actions)

### Contribution Areas

Students can enhance:
- UI/UX improvements
- Performance optimization
- Additional reports
- More analytics
- Enhanced notifications
- Mobile responsiveness
- Accessibility features
- Documentation

---

## 📊 Project Statistics

- **Total Lines of Code:** ~5,500+
- **Python Files:** 10+ modules
- **HTML Templates:** 35+ pages
- **JavaScript Files:** 5+ files
- **CSS Files:** 3+ stylesheets
- **Database Tables:** 20 tables
- **API Endpoints:** 60+ routes
- **User Roles:** 4 roles
- **Features:** 14 major features

---

**Built with ❤️ for BCA BUB Students**
*Last Updated: January 2026*
