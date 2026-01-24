"""
Hard Delete Attendance Data Script
===================================
This script PERMANENTLY deletes all attendance data from the database.

WARNING: This action CANNOT be undone!

Usage:
    python scripts/hard_delete_attendance.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import AttendanceRecord, AttendanceSession, ClassSchedule


def hard_delete_all():
    """Permanently delete all attendance data."""
    with app.app_context():
        print("=" * 60)
        print("HARD DELETE - PERMANENT REMOVAL OF ATTENDANCE DATA")
        print("=" * 60)
        
        # Count records before deletion
        records_count = AttendanceRecord.query.count()
        sessions_count = AttendanceSession.query.count()
        schedules_count = ClassSchedule.query.count()
        
        print(f"\nData to be PERMANENTLY deleted:")
        print(f"  AttendanceRecord: {records_count} entries")
        print(f"  AttendanceSession: {sessions_count} entries")
        print(f"  ClassSchedule: {schedules_count} entries")
        
        if records_count == 0 and sessions_count == 0 and schedules_count == 0:
            print("\n✓ No data to delete. Tables are already empty.")
            return
        
        try:
            print("\nDeleting data...")
            
            # Delete in correct order (children first)
            print("  1. Deleting AttendanceRecord entries...")
            deleted_records = AttendanceRecord.query.delete()
            
            print("  2. Deleting AttendanceSession entries...")
            deleted_sessions = AttendanceSession.query.delete()
            
            print("  3. Deleting ClassSchedule entries...")
            deleted_schedules = ClassSchedule.query.delete()
            
            # Commit the changes
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✓ HARD DELETE COMPLETE")
            print("=" * 60)
            print(f"\nPermanently deleted:")
            print(f"  - {deleted_records} attendance records")
            print(f"  - {deleted_sessions} attendance sessions")
            print(f"  - {deleted_schedules} class schedules")
            print("\nAll attendance data has been removed from the database.")
            print("You can now enter new attendance data with correct dates.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error during deletion: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    print("\n⚠️  WARNING: This will PERMANENTLY delete all attendance data!")
    print("⚠️  This action CANNOT be undone!\n")
    
    response = input("Type 'DELETE ALL' to confirm: ")
    
    if response.strip() == 'DELETE ALL':
        hard_delete_all()
    else:
        print("\n✗ Hard delete cancelled.")
