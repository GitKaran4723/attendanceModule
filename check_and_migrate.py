"""Check database tables and run migration"""
import sqlite3
import os

db_path = os.path.join('instance', 'attendance.db')

if not os.path.exists(db_path):
    print("Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

print("Existing tables:")
for table in tables:
    print(f"  - {table}")

if 'tests' not in tables:
    print("\n✗ 'tests' table does not exist!")
    print("Please run the application first to create all tables.")
    conn.close()
    exit(1)

# Check current columns
cursor.execute("PRAGMA table_info(tests)")
columns = {col[1]: col[2] for col in cursor.fetchall()}

print("\nCurrent columns in 'tests' table:")
for name, type in columns.items():
    print(f"  - {name}: {type}")

# Add missing columns
migrations = []
if 'component_type' not in columns:
    migrations.append(("component_type", "ALTER TABLE tests ADD COLUMN component_type TEXT NOT NULL DEFAULT 'test'"))
if 'weightage' not in columns:
    migrations.append(("weightage", "ALTER TABLE tests ADD COLUMN weightage REAL"))
if 'description' not in columns:
    migrations.append(("description", "ALTER TABLE tests ADD COLUMN description TEXT"))
if 'is_published' not in columns:
    migrations.append(("is_published", "ALTER TABLE tests ADD COLUMN is_published INTEGER NOT NULL DEFAULT 0"))

if not migrations:
    print("\n✓ All columns already exist!")
else:
    print(f"\nAdding {len(migrations)} columns...")
    for name, sql in migrations:
        print(f"  → {name}")
        cursor.execute(sql)
    conn.commit()
    print("\n✓ Migration completed!")

conn.close()
