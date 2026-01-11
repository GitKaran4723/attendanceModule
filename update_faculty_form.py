# Script to add coordinator checkbox to admin_faculty_form.html

with open('templates/admin_faculty_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Coordinator checkbox section to insert
coordinator_checkbox = '''                        <div class="form-group" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(99, 102, 241, 0.02) 100%); padding: 16px; border-radius: var(--admin-radius-md); border: 2px solid rgba(99, 102, 241, 0.1);">
                            <label class="form-label" style="display: flex; align-items: center; gap: 12px; cursor: pointer;">
                                <input type="checkbox" name="is_coordinator" value="1" 
                                    {% if faculty and faculty.is_coordinator %}checked{% endif %}
                                    style="width: 20px; height: 20px; accent-color: var(--admin-primary); cursor: pointer;">
                                <span style="flex: 1;">
                                    <strong style="color: var(--admin-primary);">Program Coordinator</strong>
                                    <small style="display: block; margin-top: 4px; color: #666; font-weight: normal;">
                                        <i class="material-icons" style="font-size: 14px; vertical-align: middle;">info</i>
                                        Coordinators can manage department faculty, view attendance, and monitor classes
                                    </small>
                                </span>
                            </label>
                        </div>
'''

# Find the workload section and insert after it
search_text = '''                        <div class="form-group">
                            <label class="form-label">Workload (Hours/Week)</label>
                            <input type="number" name="workload_hours_per_week" class="form-input" min="0" max="60"
                                value="{{ faculty.workload_hours_per_week if faculty else 0 }}" placeholder="e.g., 18">
                            <small style="display: block; margin-top: 6px; color: #666; font-size: 13px;">
                                <i class="material-icons" style="font-size: 14px; vertical-align: middle;">info</i>
                                Total teaching hours assigned per week
                            </small>
                        </div>'''

replacement = search_text + '\n' + coordinator_checkbox

content = content.replace(search_text, replacement)

with open('templates/admin_faculty_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added coordinator checkbox to admin_faculty_form.html")
