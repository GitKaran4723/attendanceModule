# Add JavaScript to load coordinator assignments and fix template

with open('templates/admin_faculty_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add JavaScript function before the closing script tag
js_function = '''
        // Load coordinator assignments for this faculty
        {% if faculty %}
        async function loadCoordinatorAssignments() {
            try {
                const response = await fetch('/api/admin/faculties/available-coordinators');
                const data = await response.json();
                const currentFaculty = data.faculties.find(f => f.faculty_id === '{{ faculty.faculty_id }}');
                
                const container = document.getElementById('coordinatorAssignments');
                if (currentFaculty && currentFaculty.is_coordinator) {
                    // Fetch actual assignments
                    const programs = {{ programs | tojson }};
                    let html = '<div style="font-size: 14px;">';
                    html += '<strong style="color: #10b981;">✓ This faculty is a Program Coordinator</strong><br>';
                    html += '<small style="color: #666;">Manage assignments in the Programs page</small>';
                    html += '</div>';
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div style="font-size: 14px; color: #999;">Not assigned as coordinator</div>';
                }
            } catch (error) {
                console.error('Error loading coordinator assignments:', error);
                document.getElementById('coordinatorAssignments').innerHTML = '<div style="font-size: 14px; color: #999;">Not assigned as coordinator</div>';
            }
        }
        
        // Load on page load
        window.addEventListener('DOMContentLoaded', loadCoordinatorAssignments);
        {% endif %}

'''

# Insert before the closing script tag
content = content.replace('    </script>', js_function + '    </script>')

with open('templates/admin_faculty_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added JavaScript to load coordinator assignments")
