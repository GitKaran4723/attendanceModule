import sys

# Read the original app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Read the student routes
with open('student_routes_temp.py', 'r', encoding='utf-8') as f:
    student_routes = f.read()

# Find the insertion point (before "if __name__ == '__main__':")
insertion_marker = "if __name__ == '__main__':"
insertion_index = app_content.find(insertion_marker)

if insertion_index == -1:
    print("ERROR: Could not find insertion point")
    sys.exit(1)

# Insert the student routes
new_content = (
    app_content[:insertion_index] +
    "\n" + student_routes + "\n\n" +
    app_content[insertion_index:]
)

# Write the new content
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: Student routes inserted into app.py")
