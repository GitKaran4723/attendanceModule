"""
Script to delete all attendance data from the database
This will clear:
- AttendanceSession records
- AttendanceRecord records
"""

from app import db, app
from models import AttendanceSession, AttendanceRecord

app.app_context().push()

print("Starting to delete attendance data...")

# Delete all attendance records
deleted_records = AttendanceRecord.query.delete()
print(f"Deleted {deleted_records} AttendanceRecord entries")

# Delete all attendance sessions
deleted_sessions = AttendanceSession.query.delete()
print(f"Deleted {deleted_sessions} AttendanceSession entries")

# Commit the changes
db.session.commit()
print("\n✓ All attendance data has been deleted successfully!")
print("You can now start fresh with new attendance sessions.")
