-- ============================================
-- CLEANUP SCRIPT: Delete All Attendance Data
-- ============================================
-- This script PERMANENTLY deletes all attendance records and sessions
-- Use with caution - this cannot be undone!

-- Step 1: Delete all attendance records
DELETE FROM attendance_records;

-- Step 2: Delete all attendance sessions
DELETE FROM attendance_sessions;

-- Step 3: Verify deletion
SELECT 'Attendance Records Remaining: ' || COUNT(*) FROM attendance_records;
SELECT 'Attendance Sessions Remaining: ' || COUNT(*) FROM attendance_sessions;

-- Done!
SELECT 'All attendance data has been permanently deleted from the database.';
