# Script to add coordinator management section to admin_programs.html

with open('templates/admin_programs.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Coordinator management section to insert
coordinator_section = '''                <div class="form-group">
                    <label>Program Coordinators</label>
                    <div id="coordinatorsList" style="margin-bottom: 12px; max-height: 150px; overflow-y: auto;">
                        <div style="text-align: center; padding: 20px; color: #999;">Loading...</div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <select id="coordinatorSelect" style="flex: 1;">
                            <option value="">Select Faculty...</option>
                        </select>
                        <button type="button" class="admin-btn admin-btn-primary" onclick="addCoordinator()" style="white-space: nowrap; padding: 10px 16px;">
                            <i class="material-icons" style="font-size: 18px;">add</i> Add
                        </button>
                    </div>
                    <small style="color: #666;">Coordinators can manage this department's faculty and classes</small>
                </div>
'''

# Find and replace
search_text = '''                <div class="form-group">
                    <label>Current Academic Year</label>'''

replacement = coordinator_section + search_text

content = content.replace(search_text, replacement)

with open('templates/admin_programs.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added coordinator management section to admin_programs.html")
