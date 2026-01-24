"""
Clean Attendance Data Script
=============================
This script deletes all attendance-related data from the database:
- AttendanceRecord entries
- AttendanceSession entries  
- ClassSchedule entries

USE WITH CAUTION: This will permanently delete all attendance data!

Usage:
    python scripts/clean_attendance_data.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import AttendanceRecord, AttendanceSession, ClassSchedule


def clean_attendance_data():
    """
    Clean all attendance-related data from the database.
    Uses soft delete (sets is_deleted=True) to preserve data integrity.
    """
    with app.app_context():
        print("=" * 60)
        print("ATTENDANCE DATA CLEANUP")
        print("=" * 60)
        
        # Count current records
        print("\nCurrent data counts:")
        schedules_count = ClassSchedule.query.filter_by(is_deleted=False).count()
        sessions_count = AttendanceSession.query.filter_by(is_deleted=False).count()
        records_count = AttendanceRecord.query.filter_by(is_deleted=False).count()
        
        print(f"  ClassSchedule entries: {schedules_count}")
        print(f"  AttendanceSession entries: {sessions_count}")
        print(f"  AttendanceRecord entries: {records_count}")
        
        if schedules_count == 0 and sessions_count == 0 and records_count == 0:
            print("\n✓ No data to clean. Database is already empty.")
            return
        
        # Confirm deletion
        print("\n" + "!" * 60)
        print("WARNING: This will soft-delete all attendance data!")
        print("!" * 60)
        response = input("\nType 'DELETE' to confirm: ")
        
        if response.strip() != 'DELETE':
            print("\n✗ Cleanup cancelled.")
            return
        
        print("\nCleaning data...")
        
        try:
            # Soft delete all records (preserves referential integrity)
            # Order matters: delete children before parents
            
            # 1. Delete AttendanceRecord entries
            print("\n1. Soft-deleting AttendanceRecord entries...")
            deleted_records = AttendanceRecord.query.filter_by(is_deleted=False).update(
                {'is_deleted': True}
            )
            print(f"   ✓ Marked {deleted_records} records as deleted")
            
            # 2. Delete AttendanceSession entries
            print("\n2. Soft-deleting AttendanceSession entries...")
            deleted_sessions = AttendanceSession.query.filter_by(is_deleted=False).update(
                {'is_deleted': True}
            )
            print(f"   ✓ Marked {deleted_sessions} sessions as deleted")
            
            # 3. Delete ClassSchedule entries
            print("\n3. Soft-deleting ClassSchedule entries...")
            deleted_schedules = ClassSchedule.query.filter_by(is_deleted=False).update(
                {'is_deleted': True}
            )
            print(f"   ✓ Marked {deleted_schedules} schedules as deleted")
            
            # Commit all changes
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✓ CLEANUP COMPLETE")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  - {deleted_records} attendance records soft-deleted")
            print(f"  - {deleted_sessions} attendance sessions soft-deleted")
            print(f"  - {deleted_schedules} class schedules soft-deleted")
            print("\nYou can now re-enter attendance data with the fixed code.")
            print("The system will create new schedules matching the attendance dates.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error during cleanup: {str(e)}")
            import traceback
            traceback.print_exc()
            return


def hard_delete_attendance_data():
    """
    PERMANENTLY delete all attendance data (not recommended).
    This physically removes records from the database.
    """
    with app.app_context():
        print("=" * 60)
        print("HARD DELETE - PERMANENT REMOVAL")
        print("=" * 60)
        
        print("\n⚠️  WARNING: This will PERMANENTLY delete all data!")
        print("⚠️  This action CANNOT be undone!")
        response = input("\nType 'PERMANENT DELETE' to confirm: ")
        
        if response.strip() != 'PERMANENT DELETE':
            print("\n✗ Hard delete cancelled.")
            return
        
        try:
            # Hard delete in correct order
            deleted_records = AttendanceRecord.query.delete()
            deleted_sessions = AttendanceSession.query.delete()
            deleted_schedules = ClassSchedule.query.delete()
            
            db.session.commit()
            
            print(f"\n✓ Permanently deleted:")
            print(f"  - {deleted_records} attendance records")
            print(f"  - {deleted_sessions} attendance sessions")
            print(f"  - {deleted_schedules} class schedules")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    print("\nSelect cleanup method:")
    print("1. Soft delete (recommended - marks as deleted)")
    print("2. Hard delete (permanent removal)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        clean_attendance_data()
    elif choice == '2':
        hard_delete_attendance_data()
    else:
        print("Invalid choice. Exiting.")
