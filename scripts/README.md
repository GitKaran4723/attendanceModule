# Scripts & Helpers Directory

This folder contains utility scripts, migration scripts, and helper tools for the **BCA BUB Attendance System**.

## 📂 Script Categories

### 🔧 Setup & Initialization
- **[setup.py](setup.py)** - Initial project setup script
- **[verify_setup.py](verify_setup.py)** - Verify system configuration and dependencies
- **[create_users.py](create_users.py)** - Create initial user accounts

### 🔄 Database Migration Scripts
- **[migrate_active_status.py](migrate_active_status.py)** - Migrate active status fields
- **[migrate_attendance_topic.py](migrate_attendance_topic.py)** - Migrate attendance topic data
- **[migrate_diary_number.py](migrate_diary_number.py)** - Migrate work diary numbering system
- **[migrate_faculty_attendance.py](migrate_faculty_attendance.py)** - Migrate faculty attendance records
- **[migrate_specialization.py](migrate_specialization.py)** - Migrate specialization subject data

### 🛠️ Database Fix Scripts
- **[fix_bad_sections.py](fix_bad_sections.py)** - Fix malformed section data
- **[fix_db_enum.py](fix_db_enum.py)** - Fix ENUM type issues in database
- **[fix_schema_allocation.py](fix_schema_allocation.py)** - Fix subject allocation schema issues
- **[fix_section_constraint.py](fix_section_constraint.py)** - Fix section constraint violations
- **[check_duplicates.sql](check_duplicates.sql)** - SQL script to check for duplicate records

### 🔄 Data Update Scripts
- **[update_database.py](update_database.py)** - General database update utility
- **[update_student_credentials.py](update_student_credentials.py)** - Update student login credentials

### 🗑️ Data Management Scripts
- **[delete_attendance_data.py](delete_attendance_data.py)** - Delete attendance data (cleanup)
- **[reset_faculties.py](reset_faculties.py)** - Reset faculty data
- **[reset_student_passwords.py](reset_student_passwords.py)** - Reset student passwords

### 🔍 Verification & Testing Scripts
- **[check_attendance.py](check_attendance.py)** - Verify attendance data integrity
- **[verify_pass.py](verify_pass.py)** - Password verification utility

### 🎨 Asset Generation
- **[generate_icons.py](generate_icons.py)** - Generate PWA icons and app assets

### 📋 Routing Helpers
- **[insert_routes.py](insert_routes.py)** - Insert/update Flask routes

## ⚠️ Important Notes

### Before Running Scripts:
1. **Backup your database** before running any migration or fix scripts
2. **Review the script** to understand what changes it will make
3. **Test in development** environment first
4. **Check dependencies** - ensure required packages are installed

### Script Usage Pattern:
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run a script
python scripts/script_name.py
```

### Migration Scripts Order:
When setting up a fresh database or performing major updates, run migrations in this order:
1. `setup.py` - Initial setup
2. `create_users.py` - Create admin/test users
3. `migrate_*.py` - Run specific migrations as needed
4. `verify_setup.py` - Verify everything works

### Fix Scripts:
These are **one-time use** scripts created to fix specific issues. Only run them if you encounter the specific problem they address.

## 🚨 Dangerous Scripts

The following scripts modify or delete data. Use with extreme caution:
- `delete_attendance_data.py`
- `reset_faculties.py`
- `reset_student_passwords.py`
- Any script starting with `fix_*`

Always backup before running these!

## 📝 Adding New Scripts

When adding new helper scripts:
1. Place them in this `scripts` folder
2. Use descriptive names (e.g., `migrate_new_feature.py`, `fix_specific_issue.py`)
3. Include proper documentation/comments in the script
4. Update this README with a description
5. Test thoroughly before committing

## 🔗 Related Documentation

For comprehensive project documentation, see the [docs](../docs/) folder.
