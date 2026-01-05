# Database Schema Documentation

## Overview

This document provides a comprehensive description of all database tables in the **BCA BUB Attendance System**. The database consists of **23 tables** organized into the following modules:

1. **Core User Management** (3 tables)
2. **Academic Entities** (4 tables)  
3. **Curriculum Structure** (4 tables)
4. **Subject Management** (2 tables)
5. **Attendance System** (2 tables)
6. **Assessment/Testing** (2 tables)
7. **Work Diary System** (1 table)
8. **Bulk Import Tracking** (1 table)
9. **Student Enrollment** (1 table)
10. **Campus Check-In** (2 tables)
11. **Faculty Attendance** (1 table)

---

## Table Descriptions

### 1. Core User Management

#### 1.1 `roles`

Stores user role definitions (Admin, Faculty, Student, HOD).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `role_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique role identifier (UUID) |
| `role_name` | VARCHAR(64) | NOT NULL, UNIQUE, INDEX | Role name (e.g., "Admin", "Faculty") |
| `description` | TEXT | | Role description |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Relationships:**
- One-to-Many with `users` (a role can have multiple users)

---

#### 1.2 `users`

Core user authentication and authorization table.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `user_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique user identifier (UUID) |
| `username` | VARCHAR(128) | NOT NULL, UNIQUE, INDEX | Login username |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | User email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Hashed password |
| `role_id` | VARCHAR(36) | **FK → roles(role_id)**, NOT NULL | User's role |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account active status |
| `last_login_at` | DATETIME | | Last login timestamp |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `role_id` → `roles(role_id)`

**Relationships:**
- Many-to-One with `roles`
- One-to-One with `faculties` (if user is faculty)
- One-to-One with `students` (if user is student)

---

#### 1.3 `faculties`

Faculty/teacher profile information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `faculty_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique faculty identifier (UUID) |
| `user_id` | VARCHAR(36) | **FK → users(user_id)**, NOT NULL, UNIQUE, INDEX | Link to user account |
| `employee_id` | VARCHAR(50) | UNIQUE, INDEX | Employee/staff ID |
| `first_name` | VARCHAR(100) | NOT NULL | Faculty first name |
| `last_name` | VARCHAR(100) | NOT NULL | Faculty last name |
| `name` | VARCHAR(200) | | Legacy full name field (backward compatibility) |
| `department` | VARCHAR(100) | | Department name |
| `qualification` | VARCHAR(200) | | Educational qualifications |
| `phone` | VARCHAR(20) | | Contact phone number |
| `email` | VARCHAR(255) | | Email address |
| `employment_type` | ENUM | 'full_time', 'part_time' | Employment type |
| `join_date` | DATE | | Date of joining |
| `designation` | VARCHAR(128) | | Job designation/title |
| `is_hod` | BOOLEAN | NOT NULL, DEFAULT FALSE | Head of Department flag |
| `status` | VARCHAR(32) | DEFAULT 'active' | Faculty status |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `user_id` → `users(user_id)`

**Relationships:**
- One-to-One with `users`
- One-to-Many with `subject_allocations`
- One-to-Many with `class_schedules`
- One-to-Many with `tests`
- One-to-Many with `work_diaries`
- One-to-Many with `sections` (as class teacher)

---

### 2. Academic Entities

#### 2.1 `programs`

Academic programs (e.g., BCA, MCA, B.Sc Computer Science).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `program_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique program identifier (UUID) |
| `program_code` | VARCHAR(50) | UNIQUE, INDEX | Program code (e.g., "BCA") |
| `program_name` | VARCHAR(150) | NOT NULL | Full program name |
| `name` | VARCHAR(150) | | Legacy name field (backward compatibility) |
| `duration` | INTEGER | | Program duration (years/semesters) |
| `duration_years` | INTEGER | | Duration in years (for templates) |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Relationships:**
- One-to-Many with `sections`
- One-to-Many with `students`
- One-to-Many with `subjects`

---

#### 2.2 `sections`

Class sections within programs (e.g., BCA 3rd Year Section A).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `section_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique section identifier (UUID) |
| `section_name` | VARCHAR(64) | NOT NULL | Section name (e.g., "Section A") |
| `name` | VARCHAR(64) | | Legacy name field |
| `program_id` | VARCHAR(36) | **FK → programs(program_id)**, NOT NULL, INDEX | Link to program |
| `year_of_study` | INTEGER | | Year of study (1, 2, 3, etc.) |
| `academic_year` | VARCHAR(20) | | Academic year (e.g., "2024-2025") |
| `current_semester` | INTEGER | | Current semester number |
| `class_teacher_id` | VARCHAR(36) | **FK → faculties(faculty_id)**, INDEX | Class teacher |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `program_id` → `programs(program_id)`
- `class_teacher_id` → `faculties(faculty_id)`

**Unique Constraints:**
- `uix_section_program_semester` on (`section_name`, `program_id`, `current_semester`, `academic_year`)

**Relationships:**
- Many-to-One with `programs`
- Many-to-One with `faculties` (class teacher)
- One-to-Many with `students`
- One-to-Many with `subject_allocations`
- One-to-Many with `class_schedules`
- One-to-Many with `tests`

---

#### 2.3 `students`

Student profile and academic information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `student_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique student identifier (UUID) |
| `user_id` | VARCHAR(36) | **FK → users(user_id)**, NOT NULL, UNIQUE, INDEX | Link to user account |
| `roll_number` | VARCHAR(64) | UNIQUE, INDEX | Student roll/registration number |
| `usn` | VARCHAR(64) | INDEX | University Seat Number (legacy) |
| `first_name` | VARCHAR(100) | NOT NULL | Student first name |
| `last_name` | VARCHAR(100) | NOT NULL | Student last name |
| `name` | VARCHAR(200) | | Legacy full name field |
| `date_of_birth` | DATE | | Date of birth |
| `dob` | DATE | | Legacy DOB field |
| `email` | VARCHAR(255) | | Email address |
| `phone` | VARCHAR(20) | | Contact phone number |
| `address` | TEXT | | Residential address |
| `guardian_name` | VARCHAR(200) | | Parent/guardian name |
| `guardian_phone` | VARCHAR(20) | | Guardian contact number |
| `program_id` | VARCHAR(36) | **FK → programs(program_id)** | Enrolled program |
| `section_id` | VARCHAR(36) | **FK → sections(section_id)** | Assigned section |
| `semester_id` | VARCHAR(36) | **FK → semesters(semester_id)** | Current semester |
| `admission_year` | INTEGER | | Year of admission |
| `current_semester` | INTEGER | | Current semester number (1-8) |
| `gender` | VARCHAR(10) | | Gender (M/F/Other) |
| `status` | VARCHAR(32) | DEFAULT 'active' | Student status |
| `is_active` | BOOLEAN | DEFAULT TRUE, NOT NULL | Active status |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `user_id` → `users(user_id)`
- `program_id` → `programs(program_id)`
- `section_id` → `sections(section_id)`
- `semester_id` → `semesters(semester_id)`

**Relationships:**
- One-to-One with `users`
- Many-to-One with `programs`
- Many-to-One with `sections`
- Many-to-One with `semesters`
- One-to-Many with `attendance_records`
- One-to-Many with `test_results`
- One-to-Many with `student_subject_enrollments`
- One-to-Many with `campus_checkins`

---

#### 2.4 `semesters`

Academic semester/term information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `semester_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique semester identifier (UUID) |
| `name` | VARCHAR(64) | NOT NULL | Semester name (e.g., "Semester 1") |
| `start_date` | DATE | | Semester start date |
| `end_date` | DATE | | Semester end date |
| `academic_year` | VARCHAR(32) | | Academic year |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Relationships:**
- One-to-Many with `students`
- One-to-Many with `class_schedules`
- One-to-Many with `tests`
- One-to-Many with `subject_allocations`
- One-to-Many with `work_diaries`

---

### 3. Curriculum Structure

#### 3.1 `subjects`

Subject/course information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `subject_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique subject identifier (UUID) |
| `subject_code` | VARCHAR(64) | NOT NULL, INDEX, UNIQUE (uix_subject_code) | Subject code (e.g., "CS101") |
| `code` | VARCHAR(64) | | Legacy code field |
| `subject_name` | VARCHAR(255) | NOT NULL | Subject name |
| `credits` | FLOAT | DEFAULT 0 | Credit hours |
| `subject_type` | VARCHAR(64) | | Subject type (Theory/Practical/Project) |
| `type` | ENUM | 'theory', 'practical', 'mixed', DEFAULT 'theory' | Legacy type field |
| `program_id` | VARCHAR(36) | **FK → programs(program_id)**, INDEX | Associated program |
| `semester_id` | INTEGER | | Semester number (1-8) |
| `description` | TEXT | | Subject description |
| `total_hours` | INTEGER | | Total teaching hours |
| `is_specialization` | BOOLEAN | DEFAULT FALSE | Elective/specialization flag |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `program_id` → `programs(program_id)`

**Unique Constraints:**
- `uix_subject_code` on (`subject_code`)

**Relationships:**
- Many-to-One with `programs`
- One-to-Many with `units`
- One-to-Many with `subject_allocations`
- One-to-Many with `class_schedules`
- One-to-Many with `tests`
- One-to-Many with `student_subject_enrollments`
- One-to-Many with `work_diaries`

---

#### 3.2 `units`

Units within subjects (e.g., Unit 1, Unit 2).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `unit_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique unit identifier (UUID) |
| `subject_id` | VARCHAR(36) | **FK → subjects(subject_id)**, NOT NULL, INDEX | Parent subject |
| `unit_number` | INTEGER | NOT NULL | Unit number |
| `unit_name` | VARCHAR(255) | NOT NULL | Unit name/title |
| `description` | TEXT | | Unit description |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `subject_id` → `subjects(subject_id)` (CASCADE DELETE)

**Unique Constraints:**
- `uix_subject_unit` on (`subject_id`, `unit_number`)

**Relationships:**
- Many-to-One with `subjects`
- One-to-Many with `chapters`

---

#### 3.3 `chapters`

Chapters within units.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `chapter_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique chapter identifier (UUID) |
| `unit_id` | VARCHAR(36) | **FK → units(unit_id)**, NOT NULL, INDEX | Parent unit |
| `chapter_number` | FLOAT | NOT NULL | Chapter number (allows decimals) |
| `chapter_name` | VARCHAR(255) | NOT NULL | Chapter name/title |
| `description` | TEXT | | Chapter description |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `unit_id` → `units(unit_id)` (CASCADE DELETE)

**Unique Constraints:**
- `uix_unit_chapter` on (`unit_id`, `chapter_number`)

**Relationships:**
- Many-to-One with `units`
- One-to-Many with `concepts`

---

#### 3.4 `concepts`

Concepts within chapters (smallest curriculum unit).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `concept_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique concept identifier (UUID) |
| `chapter_id` | VARCHAR(36) | **FK → chapters(chapter_id)**, NOT NULL, INDEX | Parent chapter |
| `concept_name` | VARCHAR(255) | NOT NULL | Concept name |
| `description` | TEXT | | Concept description |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `chapter_id` → `chapters(chapter_id)` (CASCADE DELETE)

**Relationships:**
- Many-to-One with `chapters`

---

### 4. Subject Management

#### 4.1 `subject_allocations`

Faculty subject assignments for sections.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `allocation_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique allocation identifier (UUID) |
| `subject_id` | VARCHAR(36) | **FK → subjects(subject_id)**, NOT NULL, INDEX | Allocated subject |
| `faculty_id` | VARCHAR(36) | **FK → faculties(faculty_id)**, NOT NULL, INDEX | Assigned faculty |
| `section_id` | VARCHAR(36) | **FK → sections(section_id)**, INDEX | Assigned section |
| `semester_id` | VARCHAR(36) | **FK → semesters(semester_id)** | Academic semester |
| `allocation_type` | VARCHAR(64) | | Type (primary/co-teacher) |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `subject_id` → `subjects(subject_id)`
- `faculty_id` → `faculties(faculty_id)`
- `section_id` → `sections(section_id)`
- `semester_id` → `semesters(semester_id)`

**Unique Constraints:**
- `uix_sub_fac_sec` on (`subject_id`, `faculty_id`, `section_id`)

**Relationships:**
- Many-to-One with `subjects`
- Many-to-One with `faculties`
- Many-to-One with `sections`
- Many-to-One with `semesters`

---

#### 4.2 `class_schedules`

Class timetable entries.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `schedule_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique schedule identifier (UUID) |
| `subject_id` | VARCHAR(36) | **FK → subjects(subject_id)**, NOT NULL | Scheduled subject |
| `faculty_id` | VARCHAR(36) | **FK → faculties(faculty_id)**, NOT NULL | Teaching faculty |
| `section_id` | VARCHAR(36) | **FK → sections(section_id)**, NOT NULL | Class section |
| `semester_id` | VARCHAR(36) | **FK → semesters(semester_id)** | Academic semester |
| `room_id` | VARCHAR(64) | | Room/venue identifier |
| `date` | DATE | NOT NULL, INDEX | Class date |
| `start_time` | TIME | | Class start time |
| `end_time` | TIME | | Class end time |
| `class_type` | VARCHAR(16) | | Class type (theory/practical) |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `subject_id` → `subjects(subject_id)`
- `faculty_id` → `faculties(faculty_id)`
- `section_id` → `sections(section_id)`
- `semester_id` → `semesters(semester_id)`

**Indexes:**
- `ix_schedule_section_date` on (`section_id`, `date`)

**Relationships:**
- Many-to-One with `subjects`
- Many-to-One with `faculties`
- Many-to-One with `sections`
- Many-to-One with `semesters`
- One-to-Many with `attendance_sessions`

---

### 5. Attendance System

#### 5.1 `attendance_sessions`

Attendance session metadata (one per scheduled class).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `attendance_session_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique session identifier (UUID) |
| `schedule_id` | VARCHAR(36) | **FK → class_schedules(schedule_id)**, NOT NULL, INDEX | Associated schedule |
| `taken_by_user_id` | VARCHAR(36) | **FK → users(user_id)**, NOT NULL | User who took attendance |
| `taken_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Attendance recording timestamp |
| `status` | ENUM | 'draft', 'finalized', DEFAULT 'draft' | Session status |
| `approved_by` | VARCHAR(36) | **FK → users(user_id)** | Approving user |
| `approved_at` | DATETIME | | Approval timestamp |
| `topic_taught` | VARCHAR(255) | | Topic/content taught in class |
| `diary_number` | VARCHAR(20) | UNIQUE, INDEX | Unique diary identifier (e.g., BCA-2024-001) |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `schedule_id` → `class_schedules(schedule_id)`
- `taken_by_user_id` → `users(user_id)`
- `approved_by` → `users(user_id)`

**Relationships:**
- Many-to-One with `class_schedules`
- Many-to-One with `users` (taken by)
- Many-to-One with `users` (approved by)
- One-to-Many with `attendance_records`
- One-to-One with `work_diaries`

---

#### 5.2 `attendance_records`

Individual student attendance records.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `record_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique record identifier (UUID) |
| `attendance_session_id` | VARCHAR(36) | **FK → attendance_sessions(attendance_session_id)**, NOT NULL, INDEX | Parent session |
| `student_id` | VARCHAR(36) | **FK → students(student_id)**, NOT NULL, INDEX | Student |
| `status` | ENUM | 'present', 'absent', 'late', 'excused', NOT NULL | Attendance status |
| `remarks` | VARCHAR(400) | | Additional remarks |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `attendance_session_id` → `attendance_sessions(attendance_session_id)` (CASCADE DELETE)
- `student_id` → `students(student_id)`

**Unique Constraints:**
- `uix_session_student` on (`attendance_session_id`, `student_id`)

**Indexes:**
- `ix_attendance_student_date` on (`student_id`, `attendance_session_id`)

**Relationships:**
- Many-to-One with `attendance_sessions`
- Many-to-One with `students`

---

### 6. Assessment/Testing

#### 6.1 `tests`

Test/exam information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `test_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique test identifier (UUID) |
| `test_name` | VARCHAR(255) | NOT NULL | Test name (e.g., "Mid-term 1") |
| `subject_id` | VARCHAR(36) | **FK → subjects(subject_id)**, NOT NULL | Subject being tested |
| `faculty_id` | VARCHAR(36) | **FK → faculties(faculty_id)**, NOT NULL | Conducting faculty |
| `section_id` | VARCHAR(36) | **FK → sections(section_id)**, NOT NULL | Section taking test |
| `semester_id` | VARCHAR(36) | **FK → semesters(semester_id)** | Academic semester |
| `test_date` | DATE | | Test date |
| `max_marks` | FLOAT | | Maximum marks |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `subject_id` → `subjects(subject_id)`
- `faculty_id` → `faculties(faculty_id)`
- `section_id` → `sections(section_id)`
- `semester_id` → `semesters(semester_id)`

**Relationships:**
- Many-to-One with `subjects`
- Many-to-One with `faculties`
- Many-to-One with `sections`
- Many-to-One with `semesters`
- One-to-Many with `test_results`

---

#### 6.2 `test_results`

Individual student test results.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `result_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique result identifier (UUID) |
| `test_id` | VARCHAR(36) | **FK → tests(test_id)**, NOT NULL, INDEX | Associated test |
| `student_id` | VARCHAR(36) | **FK → students(student_id)**, NOT NULL, INDEX | Student |
| `marks_obtained` | FLOAT | | Marks scored |
| `remarks` | VARCHAR(400) | | Additional remarks |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `test_id` → `tests(test_id)` (CASCADE DELETE)
- `student_id` → `students(student_id)`

**Unique Constraints:**
- `uix_test_student` on (`test_id`, `student_id`)

**Relationships:**
- Many-to-One with `tests`
- Many-to-One with `students`

---

### 7. Work Diary System

#### 7.1 `work_diaries`

Faculty work diary entries with auto-generated diary numbers.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `diary_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique diary identifier (UUID) |
| `diary_number` | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | Auto-generated (WD-YYYY-NNNN) |
| `faculty_id` | VARCHAR(36) | **FK → faculties(faculty_id)**, NOT NULL, INDEX | Faculty member |
| `subject_id` | VARCHAR(36) | **FK → subjects(subject_id)** | Subject (for classes) |
| `section_id` | VARCHAR(36) | **FK → sections(section_id)** | Section (for classes) |
| `semester_id` | VARCHAR(36) | **FK → semesters(semester_id)** | Academic semester |
| `academic_year` | VARCHAR(32) | | Academic year (e.g., "2024-2025") |
| `date` | DATE | NOT NULL, INDEX | Activity date |
| `start_time` | TIME | NOT NULL | Activity start time |
| `end_time` | TIME | NOT NULL | Activity end time |
| `duration_hours` | FLOAT | | Calculated duration in hours |
| `activity_type` | ENUM | 'theory_class', 'practical_class', 'tutorial', 'invigilation', 'meeting', 'seminar', 'workshop', 'exam_duty', 'other', NOT NULL | Activity type |
| `attendance_session_id` | VARCHAR(36) | **FK → attendance_sessions(attendance_session_id)**, INDEX | Linked attendance (if class) |
| `students_present` | INTEGER | DEFAULT 0 | Number of students present |
| `total_students` | INTEGER | DEFAULT 0 | Section strength |
| `activity_title` | VARCHAR(255) | | Activity title (for non-class activities) |
| `activity_description` | TEXT | | Detailed description |
| `location` | VARCHAR(128) | | Room/venue |
| `topics_covered` | TEXT | | Topics taught/discussed |
| `status` | ENUM | 'draft', 'submitted', 'approved', 'rejected', DEFAULT 'draft', NOT NULL | Diary status |
| `submitted_at` | DATETIME | | Submission timestamp |
| `approved_by` | VARCHAR(36) | **FK → users(user_id)** | Approving user |
| `approved_at` | DATETIME | | Approval timestamp |
| `approval_remarks` | TEXT | | Approval/rejection remarks |
| `attachment_url` | VARCHAR(500) | | Uploaded file path |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `faculty_id` → `faculties(faculty_id)`
- `subject_id` → `subjects(subject_id)`
- `section_id` → `sections(section_id)`
- `semester_id` → `semesters(semester_id)`
- `attendance_session_id` → `attendance_sessions(attendance_session_id)`
- `approved_by` → `users(user_id)`

**Relationships:**
- Many-to-One with `faculties`
- Many-to-One with `subjects`
- Many-to-One with `sections`
- Many-to-One with `semesters`
- One-to-One with `attendance_sessions`
- Many-to-One with `users` (approved by)

---

### 8. Bulk Import Tracking

#### 8.1 `import_logs`

Track bulk import operations for audit purposes.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `import_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique import identifier (UUID) |
| `import_type` | ENUM | 'faculty', 'student', 'subject', 'schedule', 'work_diary', 'other', NOT NULL | Type of data imported |
| `imported_by` | VARCHAR(36) | **FK → users(user_id)**, NOT NULL | User who performed import |
| `file_name` | VARCHAR(255) | | Uploaded file name |
| `total_rows` | INTEGER | DEFAULT 0 | Total rows in file |
| `successful_rows` | INTEGER | DEFAULT 0 | Successfully imported rows |
| `failed_rows` | INTEGER | DEFAULT 0 | Failed row count |
| `status` | ENUM | 'processing', 'completed', 'failed', 'partial', DEFAULT 'processing', NOT NULL | Import status |
| `error_log` | TEXT | | JSON error details |
| `import_data` | TEXT | | JSON backup of imported data |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `imported_by` → `users(user_id)`

**Relationships:**
- Many-to-One with `users`

---

### 9. Student Enrollment

#### 9.1 `student_subject_enrollments`

Individual student enrollment in specialization/elective subjects.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `enrollment_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique enrollment identifier (UUID) |
| `student_id` | VARCHAR(36) | **FK → students(student_id)**, NOT NULL, INDEX | Enrolled student |
| `subject_id` | VARCHAR(36) | **FK → subjects(subject_id)**, NOT NULL, INDEX | Enrolled subject |
| `academic_year` | VARCHAR(20) | | Academic year (e.g., "2024-2025") |
| `semester` | INTEGER | | Semester number (1-8) |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `student_id` → `students(student_id)`
- `subject_id` → `subjects(subject_id)`

**Unique Constraints:**
- `uix_student_subject_year` on (`student_id`, `subject_id`, `academic_year`)

**Relationships:**
- Many-to-One with `students`
- Many-to-One with `subjects`

---

### 10. Campus Check-In System

#### 10.1 `campus_checkins`

Student daily campus check-in/checkout with GPS validation.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `checkin_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique check-in identifier (UUID) |
| `student_id` | VARCHAR(36) | **FK → students(student_id)**, NOT NULL, INDEX | Student |
| `checkin_date` | DATE | NOT NULL, INDEX | Check-in date |
| `checkin_time` | TIME | NOT NULL | Check-in time |
| `latitude` | FLOAT | NOT NULL | Check-in GPS latitude |
| `longitude` | FLOAT | NOT NULL | Check-in GPS longitude |
| `checkout_time` | TIME | | Check-out time (nullable initially) |
| `checkout_latitude` | FLOAT | | Check-out GPS latitude |
| `checkout_longitude` | FLOAT | | Check-out GPS longitude |
| `is_valid_location` | BOOLEAN | DEFAULT TRUE | Within campus bounds flag |
| `device_info` | VARCHAR(255) | | Browser/device information |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Foreign Keys:**
- `student_id` → `students(student_id)`

**Unique Constraints:**
- `uix_student_daily_checkin` on (`student_id`, `checkin_date`)

**Indexes:**
- `ix_checkin_date_section` on (`checkin_date`)

**Relationships:**
- Many-to-One with `students`

---

#### 10.2 `college_config`

System configuration including campus location settings.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `config_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique config identifier (UUID) |
| `config_key` | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | Configuration key |
| `campus_latitude` | FLOAT | | Campus GPS latitude |
| `campus_longitude` | FLOAT | | Campus GPS longitude |
| `campus_radius_meters` | INTEGER | DEFAULT 100 | Check-in radius in meters |
| `college_name` | VARCHAR(255) | | College name |
| `checkin_start_time` | TIME | | Check-in window start (e.g., 07:00) |
| `checkin_end_time` | TIME | | Check-in window end (e.g., 18:00) |
| `config_value` | TEXT | | General configuration value |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**No Foreign Keys**

---

### 11. Faculty Attendance

#### 11.1 `faculty_attendance`

Faculty check-in/checkout tracking with GPS validation.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `attendance_id` | VARCHAR(36) | PRIMARY KEY, DEFAULT gen_uuid() | Unique attendance identifier (UUID) |
| `faculty_id` | VARCHAR(36) | NOT NULL | Faculty member (no FK - legacy) |
| `date` | DATE | NOT NULL | Attendance date |
| `check_in_time` | DATETIME | | Check-in timestamp |
| `check_in_latitude` | FLOAT | | Check-in GPS latitude |
| `check_in_longitude` | FLOAT | | Check-in GPS longitude |
| `check_out_time` | DATETIME | | Check-out timestamp |
| `check_out_latitude` | FLOAT | | Check-out GPS latitude |
| `check_out_longitude` | FLOAT | | Check-out GPS longitude |
| `check_out_valid` | BOOLEAN | DEFAULT FALSE | Check-out within campus flag |
| `created_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL, DEFAULT utcnow() | Last update timestamp |

**Indexes:**
- `idx_faculty_date` on (`faculty_id`, `date`)

**Note:** The `faculty_id` does not have a foreign key constraint due to legacy table structure.

---

## Entity Relationship Summary

### Key Relationships

1. **User → Role**: Many users belong to one role
2. **User → Faculty/Student**: One-to-one relationship based on role
3. **Program → Sections**: One program has many sections
4. **Section → Students**: One section has many students
5. **Faculty → Subject Allocations**: Faculty assigned to multiple subjects
6. **Subject → Units → Chapters → Concepts**: Hierarchical curriculum structure
7. **Class Schedule → Attendance Session**: One schedule can have multiple sessions
8. **Attendance Session → Attendance Records**: One session has many student records
9. **Test → Test Results**: One test has many student results
10. **Student → Campus Check-ins**: Daily check-in tracking
11. **Faculty → Work Diaries**: Faculty activity tracking

### Soft Delete Pattern

Most tables include `is_deleted` (BOOLEAN) for soft deletion, allowing data recovery and audit trails without physical deletion.

### Timestamp Pattern

All tables include:
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp (auto-updated)

### UUID Primary Keys

All tables use VARCHAR(36) UUID strings as primary keys for global uniqueness and scalability.

---

## Database Statistics

- **Total Tables**: 23
- **Total Foreign Keys**: 40+
- **Tables with Soft Delete**: 20
- **Tables with Timestamps**: 23
- **Unique Constraints**: 15+
- **Custom Indexes**: 10+

---

## Notes

1. **Legacy Fields**: Several tables contain legacy fields (e.g., `name`, `usn`, `code`) for backward compatibility during migration.
2. **Enum Fields**: Multiple ENUM types are used for status fields to ensure data integrity.
3. **Cascade Deletes**: Certain relationships use CASCADE DELETE (e.g., units→chapters→concepts) to maintain referential integrity.
4. **Unique Constraints**: Critical combinations have unique constraints to prevent duplicates (e.g., student-subject enrollment per academic year).
5. **Indexes**: Strategic indexes are placed on foreign keys and frequently queried columns for performance optimization.
