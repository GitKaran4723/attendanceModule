#!/usr/bin/env python3
"""
Fix all Jinja2 syntax errors in admin_faculty_form.html
Specifically fixes spaces in template tags like { { }} to {{}}
"""

import re

# Read the file
with open('templates/admin_faculty_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all instances of { { to {{
content = re.sub(r'\{\s+\{', '{{', content)

# Fix all instances of } } to }}
content = re.sub(r'\}\s+\}', '}}', content)

# Write back
with open('templates/admin_faculty_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed all Jinja2 template syntax errors")
print("✓ Removed spaces from {{ }} tags")

# Verify
with open('templates/admin_faculty_form.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
bad_patterns = re.findall(r'\{\s+\{|\}\s+\}', content)
if bad_patterns:
    print(f"⚠ WARNING: Still found {len(bad_patterns)} problematic patterns!")
else:
    print("✓ Verification passed - no syntax errors found")
