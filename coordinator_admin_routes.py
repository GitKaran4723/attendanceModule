"""
Admin API endpoints for managing program coordinators
"""

from flask import request, jsonify
from models import db, ProgramCoordinator, Faculty, Program
from auth import admin_required, get_current_user


def register_coordinator_admin_routes(app):
    """Register coordinator management routes for admin"""
    
    @app.route('/api/admin/programs/<program_id>/coordinators', methods=['GET'])
    @admin_required
    def get_program_coordinators(program_id):
        """Get all coordinators for a program"""
        assignments = ProgramCoordinator.query.filter_by(
            program_id=program_id,
            is_deleted=False
        ).all()
        
        return jsonify({
            'coordinators': [assignment.to_dict() for assignment in assignments]
        })
    
    @app.route('/api/admin/programs/<program_id>/coordinators', methods=['POST'])
    @admin_required
    def add_program_coordinator(program_id):
        """Add a coordinator to a program"""
        data = request.json
        faculty_id = data.get('faculty_id')
        
        if not faculty_id:
            return jsonify({'success': False, 'error': 'Faculty ID required'}), 400
        
        # Check if already assigned
        existing = ProgramCoordinator.query.filter_by(
            program_id=program_id,
            faculty_id=faculty_id,
            is_deleted=False
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Faculty already assigned as coordinator'}), 400
        
        try:
            current_user = get_current_user()
            assignment = ProgramCoordinator(
                program_id=program_id,
                faculty_id=faculty_id,
                assigned_by=current_user.user_id
            )
            db.session.add(assignment)
            
            # Update faculty is_coordinator flag
            faculty = Faculty.query.get(faculty_id)
            if faculty:
                faculty.is_coordinator = True
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'assignment': assignment.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/admin/programs/<program_id>/coordinators/<assignment_id>', methods=['DELETE'])
    @admin_required
    def remove_program_coordinator(program_id, assignment_id):
        """Remove a coordinator from a program"""
        assignment = ProgramCoordinator.query.get(assignment_id)
        
        if not assignment or assignment.program_id != program_id:
            return jsonify({'success': False, 'error': 'Assignment not found'}), 404
        
        try:
            faculty_id = assignment.faculty_id
            assignment.is_deleted = True
            
            # Check if faculty is coordinator of any other program
            other_assignments = ProgramCoordinator.query.filter_by(
                faculty_id=faculty_id,
                is_deleted=False
            ).filter(ProgramCoordinator.assignment_id != assignment_id).count()
            
            # If no other coordinator assignments, update faculty flag
            if other_assignments == 0:
                faculty = Faculty.query.get(faculty_id)
                if faculty:
                    faculty.is_coordinator = False
            
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/admin/faculties/available-coordinators', methods=['GET'])
    @admin_required
    def get_available_coordinators():
        """Get all faculties that can be assigned as coordinators"""
        faculties = Faculty.query.filter_by(is_deleted=False).all()
        
        return jsonify({
            'faculties': [{
                'faculty_id': f.faculty_id,
                'name': f"{f.first_name} {f.last_name}",
                'employee_id': f.employee_id,
                'department': f.department,
                'is_coordinator': f.is_coordinator
            } for f in faculties]
        })
