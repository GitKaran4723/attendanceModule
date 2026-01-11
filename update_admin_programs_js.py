# Script to add JavaScript functions for coordinator management to admin_programs.html

with open('templates/admin_programs.html', 'r', encoding='utf-8') as f:
    content = f.read()

# JavaScript functions to add before the closing script tag
js_functions = '''
        let currentProgramId = null;
        let allFaculties = [];

        async function loadFaculties() {
            try {
                const response = await fetch('/api/admin/faculties/available-coordinators');
                const data = await response.json();
                allFaculties = data.faculties || [];
                updateCoordinatorSelect();
            } catch (error) {
                console.error('Error loading faculties:', error);
            }
        }

        function updateCoordinatorSelect() {
            const select = document.getElementById('coordinatorSelect');
            select.innerHTML = '<option value="">Select Faculty...</option>';
            
            allFaculties.forEach(faculty => {
                const option = document.createElement('option');
                option.value = faculty.faculty_id;
                option.textContent = `${faculty.name} (${faculty.employee_id || 'N/A'}) - ${faculty.department || 'N/A'}`;
                select.appendChild(option);
            });
        }

        async function loadCoordinators(programId) {
            currentProgramId = programId;
            const container = document.getElementById('coordinatorsList');
            
            try {
                const response = await fetch(`/api/admin/programs/${programId}/coordinators`);
                const data = await response.json();
                
                if (data.coordinators && data.coordinators.length > 0) {
                    let html = '';
                    data.coordinators.forEach(coord => {
                        html += `
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #f9fafb; border-radius: 6px; margin-bottom: 8px;">
                                <div>
                                    <strong>${coord.faculty_name}</strong>
                                    <div style="font-size: 12px; color: #666;">Assigned: ${new Date(coord.assigned_at).toLocaleDateString()}</div>
                                </div>
                                <button type="button" onclick="removeCoordinator('${coord.assignment_id}')" 
                                    style="background: #fee2e2; color: #991b1b; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                    <i class="material-icons" style="font-size: 16px; vertical-align: middle;">delete</i> Remove
                                </button>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div style="text-align: center; padding: 20px; color: #999;">No coordinators assigned</div>';
                }
            } catch (error) {
                console.error('Error loading coordinators:', error);
                container.innerHTML = '<div style="text-align: center; padding: 20px; color: #f00;">Error loading coordinators</div>';
            }
        }

        async function addCoordinator() {
            const select = document.getElementById('coordinatorSelect');
            const facultyId = select.value;
            
            if (!facultyId) {
                alert('Please select a faculty member');
                return;
            }
            
            try {
                const response = await fetch(`/api/admin/programs/${currentProgramId}/coordinators`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ faculty_id: facultyId })
                });
                
                const result = await response.json();
                if (result.success) {
                    select.value = '';
                    loadCoordinators(currentProgramId);
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Failed to add coordinator');
                console.error(error);
            }
        }

        async function removeCoordinator(assignmentId) {
            if (!confirm('Remove this coordinator?')) return;
            
            try {
                const response = await fetch(`/api/admin/programs/${currentProgramId}/coordinators/${assignmentId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                if (result.success) {
                    loadCoordinators(currentProgramId);
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Failed to remove coordinator');
                console.error(error);
            }
        }

        // Load faculties on page load
        window.addEventListener('DOMContentLoaded', loadFaculties);

'''

# Find the closing script tag and insert before it
content = content.replace('    </script>', js_functions + '    </script>')

# Also update the openEditModal function to load coordinators
old_open_edit = '''        function openEditModal(programId, programCode, programName, durationYears, academicYear) {
            document.getElementById('editProgramId').value = programId;
            document.getElementById('editProgramCode').value = programCode;
            document.getElementById('editProgramName').value = programName;
            document.getElementById('editDurationYears').value = durationYears;
            document.getElementById('editAcademicYear').value = academicYear || '';
            document.getElementById('editModal').style.display = 'flex';
        }'''

new_open_edit = '''        function openEditModal(programId, programCode, programName, durationYears, academicYear) {
            document.getElementById('editProgramId').value = programId;
            document.getElementById('editProgramCode').value = programCode;
            document.getElementById('editProgramName').value = programName;
            document.getElementById('editDurationYears').value = durationYears;
            document.getElementById('editAcademicYear').value = academicYear || '';
            loadCoordinators(programId);
            document.getElementById('editModal').style.display = 'flex';
        }'''

content = content.replace(old_open_edit, new_open_edit)

with open('templates/admin_programs.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added JavaScript functions for coordinator management")
