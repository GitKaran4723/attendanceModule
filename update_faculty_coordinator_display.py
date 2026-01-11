# Update admin_faculty_form.html to show coordinator assignments instead of checkbox

with open('templates/admin_faculty_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the coordinator checkbox section
old_checkbox = '''                        <div class="form-group" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(99, 102, 241, 0.02) 100%); padding: 16px; border-radius: var(--admin-radius-md); border: 2px solid rgba(99, 102, 241, 0.1);">
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
                        </div>'''

# Replace with read-only display
new_display = '''                        {% if faculty %}
                        <div class="form-group" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(99, 102, 241, 0.02) 100%); padding: 16px; border-radius: var(--admin-radius-md); border: 2px solid rgba(99, 102, 241, 0.1);">
                            <label class="form-label" style="display: flex; align-items: center; gap: 12px;">
                                <i class="material-icons" style="color: var(--admin-primary); font-size: 24px;">supervisor_account</i>
                                <span style="flex: 1;">
                                    <strong style="color: var(--admin-primary);">Coordinator Assignments</strong>
                                    <small style="display: block; margin-top: 4px; color: #666; font-weight: normal;">
                                        Manage coordinator assignments in the Programs page
                                    </small>
                                </span>
                            </label>
                            <div id="coordinatorAssignments" style="margin-top: 12px;">
                                <div style="text-align: center; padding: 10px; color: #999;">Loading...</div>
                            </div>
                        </div>
                        {% endif %}'''

content = content.replace(old_checkbox, new_display)

with open('templates/admin_faculty_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Replaced coordinator checkbox with read-only display")
