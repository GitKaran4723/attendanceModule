-- Check for duplicate class schedules
SELECT 
    sub.subject_name,
    COUNT(cs.schedule_id) as schedule_count,
    GROUP_CONCAT(cs.schedule_id) as schedule_ids
FROM class_schedules cs
JOIN subjects sub ON cs.subject_id = sub.subject_id
WHERE cs.section_id = (SELECT section_id FROM students WHERE roll_number = 'U03NK24S0108')
GROUP BY cs.subject_id, sub.subject_name
HAVING COUNT(cs.schedule_id) > 1;
