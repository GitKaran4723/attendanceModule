"""Helper functions for work diary processing and DOCX generation.

This module provides utilities for processing AttendanceSession records into
monthly/weekly structures for display and DOCX export, similar to the faculty
bills processing in bcaofficial.
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Exact combined header name required in the UI and DOCX
COMBINED_HEADER = "Particulars / chapter / lectures (as per Time Table) I / II / III / IV / V / VI Sem"


def contains_lab(*texts: Any) -> bool:
    """Return True if any text contains 'lab' or 'practical' (case-insensitive).
    
    Args:
        texts: Variable number of text values to check
        
    Returns:
        True if any text contains 'lab' or 'practical', False otherwise
    """
    for t in texts:
        if t is None:
            continue
        text_lower = str(t).lower()
        if "lab" in text_lower or "practical" in text_lower:
            return True
    return False


def build_months_structure_from_sessions(sessions: List) -> Tuple[Dict[str, List[Dict]], List[str]]:
    """
    Build months structure from AttendanceSession records (no SL assignment here).

    Args:
        sessions: List of AttendanceSession objects with related schedule, subject, section, faculty
        
    Returns:
        Tuple of (months_dict, faculty_list)
        
    months_dict structure:
      { "January 2026": [ 
          { 
            "week_start": date, 
            "week_end": date, 
            "entries": [...], 
            "week_total_actual": float, 
            "week_total_claiming": float 
          }, 
          ... 
        ] 
      }
      
    Each entry contains:
      "Diary No.", "Date_iso", "Date" (dd-mm-yyyy), COMBINED_HEADER, 
      "Actual hours", "Claiming hours", "Subject code", "Faculty"
    """
    if not sessions:
        return {}, []
    
    months = {}
    faculty_set = set()

    for session in sessions:
        # Get the date from session
        if not session.taken_at:
            continue
            
        d = session.taken_at.date()
        month_label = d.strftime("%B %Y")

        # Calculate week boundaries (Monday to Saturday)
        wd = d.weekday()  # 0 = Monday, 6 = Sunday
        week_start = d - timedelta(days=wd)
        week_end = week_start + timedelta(days=5)  # Saturday (Monday + 5 days)

        months.setdefault(month_label, [])
        weeks = months[month_label]

        # Find or create week object
        week_obj = next((w for w in weeks if w["week_start"] == week_start), None)
        if not week_obj:
            week_obj = {
                "week_start": week_start,
                "week_end": week_end,
                "entries": [],
                "week_total_actual": 0.0,
                "week_total_claiming": 0.0
            }
            weeks.append(week_obj)

        # Extract data from session and related objects
        schedule = session.schedule
        subject = schedule.subject if schedule else None
        section = schedule.section if schedule else None
        faculty = schedule.faculty if schedule else None

        # Calculate hours
        actual_hours = 0.0
        if schedule and schedule.start_time and schedule.end_time:
            dummy_date = date.today()
            start_dt = datetime.combine(dummy_date, schedule.start_time)
            end_dt = datetime.combine(dummy_date, schedule.end_time)
            actual_hours = (end_dt - start_dt).total_seconds() / 3600
            actual_hours = min(actual_hours, 12)  # Cap at 12 hours max

        # Detect lab/practical
        is_lab = False
        if subject:
            is_lab = contains_lab(subject.subject_type, subject.subject_name)

        # Claiming hours: Lab period reduced by 3/4 (multiply by 0.75)
        claiming_hours = round(actual_hours * 0.75, 2) if is_lab else round(actual_hours, 2)

        # Build particulars/combined field
        particulars = session.topic_taught or "Regular Class"
        sem_info = f"({section.current_semester} Sem)" if section and section.current_semester else ""
        subject_name = subject.subject_name if subject else "Unknown Subject"
        section_name = section.section_name if section else ""
        
        # Combined: Class/Section - Subject - Topic (Semester)
        combined_parts = []
        if section_name:
            combined_parts.append(section_name)
        if subject_name:
            combined_parts.append(subject_name)
        if particulars:
            combined_parts.append(particulars)
        combined_value = " - ".join(combined_parts)
        if sem_info:
            combined_value += f" {sem_info}"

        # Faculty name
        faculty_name = ""
        if faculty:
            faculty_name = f"{faculty.first_name} {faculty.last_name}"
            faculty_set.add(faculty_name)

        # Diary number
        diary_no = session.diary_number or f"DN-{session.attendance_session_id[:8].upper()}"

        # Subject code
        subject_code = subject.subject_code if subject else "N/A"

        # Store entry (no SL No assigned yet)
        entry = {
            "SL No": None,
            "Dairy No.": diary_no,
            "Date_iso": d.strftime("%Y-%m-%d"),
            "Date": d.strftime("%d-%m-%Y"),  # dd-mm-yyyy display
            COMBINED_HEADER: combined_value,
            "Actual hours": round(actual_hours, 2),
            "Claiming hours": claiming_hours,
            "Subject code": subject_code,
            "Faculty": faculty_name,
            "_is_lab": is_lab,
            "_session_id": session.attendance_session_id
        }

        week_obj["entries"].append(entry)
        week_obj["week_total_actual"] += entry["Actual hours"]
        week_obj["week_total_claiming"] += entry["Claiming hours"]

    # Finalize months: sort weeks and entries, round totals
    for mlabel, weeks in months.items():
        weeks.sort(key=lambda w: w["week_start"])
        for w in weeks:
            w["entries"].sort(key=lambda e: (e["Date_iso"], str(e.get("Dairy No.", ""))))
            w["week_total_actual"] = round(w["week_total_actual"], 2)
            w["week_total_claiming"] = round(w["week_total_claiming"], 2)

    faculty_list = sorted(faculty_set)
    return months, faculty_list


def filter_and_assign_sl(months: Dict[str, List[Dict]], selected_month: str, 
                          selected_faculty: str) -> List[Dict]:
    """
    Filter weeks by month and faculty, then assign sequential SL numbers.
    
    Args:
        months: Months structure from build_months_structure_from_sessions
        selected_month: Month to filter (e.g., "January 2026")
        selected_faculty: Faculty name to filter (or "All" for all faculty)
        
    Returns:
        List of week dictionaries with filtered entries and assigned SL numbers
    """
    if selected_month not in months:
        return []

    # Compute month boundaries
    try:
        first_day = datetime.strptime(selected_month, "%B %Y").date().replace(day=1)
    except ValueError:
        logger.error(f"Invalid month format: {selected_month}")
        return []
    
    next_month = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = next_month - timedelta(days=1)

    rendered_weeks = []
    for w in months[selected_month]:
        # Filter entries inside this month
        entries_in_month = []
        for e in w["entries"]:
            e_date = datetime.strptime(e["Date_iso"], "%Y-%m-%d").date()
            if not (first_day <= e_date <= last_day):
                continue
            # Filter by faculty if set
            if selected_faculty != "All":
                if e.get("Faculty", "") != selected_faculty:
                    continue
            entries_in_month.append(e)

        if not entries_in_month:
            continue

        display_start = max(w["week_start"], first_day)
        display_end = min(w["week_end"], last_day)

        rendered_weeks.append({
            "week_start": w["week_start"],
            "week_end": w["week_end"],
            "display_start": display_start,
            "display_end": display_end,
            "entries": entries_in_month,
            "week_total_actual": round(sum(e["Actual hours"] for e in entries_in_month), 2),
            "week_total_claiming": round(sum(e["Claiming hours"] for e in entries_in_month), 2)
        })

    # Sort weeks and assign week numbers
    rendered_weeks.sort(key=lambda x: x["display_start"])
    for idx, rw in enumerate(rendered_weeks, start=1):
        rw["week_number"] = idx

    # Now assign sequential SL No across the entire filtered month
    flat = []
    for rw in rendered_weeks:
        for e in rw["entries"]:
            flat.append(e)
    flat.sort(key=lambda e: (e["Date_iso"], str(e.get("Dairy No.", ""))))
    for idx, e in enumerate(flat, start=1):
        e["SL No"] = idx

    return rendered_weeks
