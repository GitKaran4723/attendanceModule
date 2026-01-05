# 🚀 QUICK START GUIDE - BCA BUB

## 1️⃣ Setup (First Time Only)
```bash
python setup.py
```
This installs everything and creates sample users.

## 2️⃣ Start the Server
```bash
python app.py
```

## 3️⃣ Login
Open browser: **http://localhost:5000/login**

### Default Credentials
| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | admin     | admin123    |
| HOD     | hod       | hod123      |
| Faculty | faculty1  | faculty123  |
| Student | student1  | student123  |
| Parent  | parent1   | parent123   |

⚠️ **Change passwords immediately!**

## 4️⃣ Key Features

### For Faculty
📖 **Work Diary**
- Automatically created when you take attendance
- Manually add: invigilation, meetings, etc.
- Submit for HOD/Admin approval

### For Admin
📥 **Bulk Import**
- Import students, faculty, subjects, schedules
- Use CSV or Excel files
- Templates in `sample_imports/` folder

## 5️⃣ Common Tasks

### Take Attendance → Auto-Create Diary
1. Login as faculty
2. Go to Attendance
3. Mark attendance
4. Check Work Diary - entry auto-created!

### Create Manual Diary Entry
1. Work Diary → Click + button
2. Select activity type
3. Fill details → Save
4. Submit for approval

### Bulk Import Data
1. Login as admin
2. Admin > Bulk Import
3. Select type (Students/Faculty/Subjects/Schedules)
4. Upload CSV/Excel file
5. Click "Start Import"

## 6️⃣ File Locations

```
AttendanceModule/
├── app.py                    # Main application
├── auth.py                   # Authentication
├── models.py                 # Database models
├── setup.py                  # Setup script
├── create_users.py          # Create users
├── templates/
│   ├── login.html           # Login page
│   ├── work_diary.html      # Diary list
│   ├── work_diary_form.html # Diary form
│   └── admin_import.html    # Import interface
└── sample_imports/          # CSV templates
    ├── students_template.csv
    ├── faculty_template.csv
    ├── subjects_template.csv
    └── schedules_template.csv
```

## 7️⃣ Troubleshooting

### Can't login?
```bash
python create_users.py
```

### Database error?
```bash
# Delete database and restart
rm instance/attendance.db
python app.py
python create_users.py
```

### Import failing?
- Check CSV column names match exactly
- Ensure no duplicate IDs
- Review `ImportLog` table for errors

## 8️⃣ URLs

| Page              | URL                            |
|-------------------|--------------------------------|
| Login             | /login                         |
| Dashboard         | /                              |
| Work Diary        | /work-diary                    |
| Create Diary      | /work-diary/create            |
| Bulk Import       | /admin/import (admin only)     |
| Faculty           | /faculty                       |
| Students          | /students                      |
| Attendance        | /attendance                    |

## 9️⃣ Mobile Access

From your phone:
1. Find your computer's IP address
   ```bash
   ipconfig  # Windows
   ```
2. Open browser on phone
3. Go to: **http://YOUR_IP:5000/login**
4. Install as PWA (Add to Home Screen)

## 🔟 Documentation

📚 **Full Guides**
- `README.md` - Main documentation
- `WORK_DIARY_GUIDE.md` - Work diary & auth details
- `IMPLEMENTATION_SUMMARY.md` - What's been added
- `QUICKSTART.md` - Original quick start

## 💡 Pro Tips

1. **Auto-Diary**: Take attendance to automatically create diary entries
2. **Batch Import**: Use Excel for bulk data entry
3. **Mobile First**: Designed for mobile use - install as PWA
4. **Offline Support**: Service worker caches for offline access
5. **Role-Based**: Different features for different roles

## 🆘 Need Help?

1. Check terminal for error messages
2. Review documentation files
3. Check `ImportLog` table for import errors
4. Ensure database is initialized
5. Verify user roles are correct

## ⚡ One-Line Commands

```bash
# Complete setup
python setup.py

# Start server
python app.py

# Create users only
python create_users.py

# Install dependencies only
pip install -r requirements.txt
```

---

**That's it! You're ready to go! 🎉**

Run `python setup.py` if first time, then `python app.py` to start!
