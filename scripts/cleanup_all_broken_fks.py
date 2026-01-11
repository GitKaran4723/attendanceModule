import sqlite3
import os
import re

DB_PATH = os.path.join("instance", "attendance.db")

def cleanup_fks():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys=OFF;")
    
    # Regex to capture broken table names in REFERENCES clause
    # Looks for: REFERENCES "something_broken" or REFERENCES something_broken
    # Suffixes: _old, _broken, _broken_fk, _cleanup_X
    pattern = re.compile(r'REFERENCES\s+(?:"?(\w+(?:_old|_broken|_broken_fk|_cleanup_\d+))"?)', re.IGNORECASE)

    repaired_count = 0
    max_passes = 5 # Avoid infinite loop
    
    for pass_num in range(max_passes):
        print(f"\n--- Pass {pass_num + 1} ---")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL;")
        tables = cursor.fetchall()
        
        tables_to_fix = []
        for name, sql in tables:
            matches = pattern.findall(sql)
            if matches:
                # Deduplicate matches
                broken_refs = set(matches)
                tables_to_fix.append((name, sql, broken_refs))
        
        if not tables_to_fix:
            print("No broken references found!")
            break
            
        print(f"Found {len(tables_to_fix)} tables with broken references.")
        
        for table, current_sql, broken_refs in tables_to_fix:
            print(f"Repairing {table} (Broken refs: {broken_refs})...")
            
            fixed_sql = current_sql
            for broken in broken_refs:
                # Derive corrected name: strip known suffixes
                # Order matters: _broken_fk is longer than _broken. _cleanup_X matches via regex.
                corrected = broken
                # Remove cleanup suffix via regex first
                corrected = re.sub(r'_cleanup_\d+$', '', corrected)
                
                for suffix in ["_broken_fk", "_broken", "_old"]:
                    if corrected.endswith(suffix):
                        corrected = corrected[:-len(suffix)]
                        break # Only remove one suffix
                
                print(f"  Mapping {broken} -> {corrected}")
                # Replace quoted and unquoted
                fixed_sql = fixed_sql.replace(f'"{broken}"', f'"{corrected}"')
                fixed_sql = fixed_sql.replace(f' {broken}', f' {corrected}') # simplistic word boundary check
                # A better replace might be needed but usually broken FK is preceded by whitespace
            
            if fixed_sql == current_sql:
                print("  No changes made to SQL (maybe replacement failed?). Skipping.")
                continue

            try:
                temp_table = f"{table}_cleanup_{pass_num}"
                cursor.execute(f"ALTER TABLE {table} RENAME TO {temp_table};")
                cursor.execute(fixed_sql)
                cursor.execute(f"INSERT INTO {table} SELECT * FROM {temp_table};")
                cursor.execute(f"DROP TABLE {temp_table};")
                print(f"  Success!")
                repaired_count += 1
                conn.commit()
            except Exception as e:
                print(f"  Error repairing {table}: {e}")
                conn.rollback()

    conn.close()
    print(f"\nCleanup finished. Total tables repaired: {repaired_count}")

if __name__ == "__main__":
    cleanup_fks()
