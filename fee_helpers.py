"""
Fee Assignment Helper Functions
Automatic fee assignment based on joining year, academic year, and seat type
"""

from models import db, Student, FeeTemplate, FeeStructure
from datetime import datetime
import json

def assign_fee_to_student(student_id, user_id=None):
    """
    Automatically assign fee to student based on:
    - joining_academic_year (batch year)
    - current_academic_year
    - seat_type (GOVERNMENT/MANAGEMENT)
    - quota_type (MERIT/CATEGORY/NULL)
    
    Returns:
        dict: Success status and details
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return {'success': False, 'error': 'Student not found'}
        
        # Validate required fields
        if not student.joining_academic_year:
            return {'success': False, 'error': 'Student joining year not set'}
        
        if not student.current_academic_year:
            return {'success': False, 'error': 'Student current academic year not set'}
        
        if not student.seat_type:
            return {'success': False, 'error': 'Student seat type not set'}
        
        # Find matching template
        template = FeeTemplate.query.filter_by(
            batch_year=student.joining_academic_year,
            academic_year=student.current_academic_year,
            seat_type=student.seat_type,
            quota_type=student.quota_type,
            is_deleted=False
        ).first()
        
        if not template:
            # Try without quota_type for management seats
            if student.seat_type == 'MANAGEMENT':
                template = FeeTemplate.query.filter_by(
                    batch_year=student.joining_academic_year,
                    academic_year=student.current_academic_year,
                    seat_type=student.seat_type,
                    quota_type=None,
                    is_deleted=False
                ).first()
        
        if not template:
            return {
                'success': False,
                'error': f'No fee template found for: Batch {student.joining_academic_year}, Year {student.current_academic_year}, {student.seat_type} seat'
            }
        
        # Check if fee structure already exists for this academic year
        existing = FeeStructure.query.filter_by(
            student_id=student_id,
            academic_year=student.current_academic_year,
            is_deleted=False
        ).first()
        
        if existing:
            # Update existing structure
            existing.template_id = template.fee_template_id
            existing.base_fees = template.base_fees
            
            # Recalculate total (base + additional fees)
            additional_total = 0
            if existing.additional_fees:
                try:
                    additional_fees_list = json.loads(existing.additional_fees)
                    additional_total = sum(float(f.get('amount', 0)) for f in additional_fees_list)
                except:
                    pass
            
            existing.total_fees = template.base_fees + additional_total
            # Note: balance is a calculated property, not a database column
            # It's automatically calculated as: total_fees - sum(approved receipts)
            
            db.session.commit()
            
            return {
                'success': True,
                'action': 'updated',
                'fee_structure_id': existing.fee_structure_id,
                'template': template.to_dict(),
                'base_fees': template.base_fees,
                'total_fees': existing.total_fees
            }
        else:
            # Create new fee structure
            fee_structure = FeeStructure(
                student_id=student_id,
                section_id=student.section_id,
                template_id=template.fee_template_id,
                academic_year=student.current_academic_year,
                base_fees=template.base_fees,
                total_fees=template.base_fees,
                # amount_paid and balance are calculated properties now
                is_auto_generated=True,
                set_by_user_id=user_id
            )
            
            db.session.add(fee_structure)
            db.session.commit()
            
            return {
                'success': True,
                'action': 'created',
                'fee_structure_id': fee_structure.fee_structure_id,
                'template': template.to_dict(),
                'base_fees': template.base_fees,
                'total_fees': template.base_fees
            }
            
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}


def add_additional_fee(student_id, academic_year, fee_name, amount, remarks=None, user_id=None):
    """
    Add additional fee to student's fee structure
    
    Args:
        student_id: Student ID
        academic_year: Academic year for the fee
        fee_name: Name of the additional fee (e.g., "Hostel Fee", "Transport Fee")
        amount: Fee amount
        remarks: Optional remarks
        user_id: User adding the fee
        
    Returns:
        dict: Success status and updated fee structure
    """
    try:
        # Get fee structure
        fee_structure = FeeStructure.query.filter_by(
            student_id=student_id,
            academic_year=academic_year,
            is_deleted=False
        ).first()
        
        if not fee_structure:
            return {'success': False, 'error': 'Fee structure not found for this academic year'}
        
        # Parse existing additional fees
        additional_fees = []
        if fee_structure.additional_fees:
            try:
                additional_fees = json.loads(fee_structure.additional_fees)
            except:
                additional_fees = []
        
        # Add new fee
        new_fee = {
            'name': fee_name,
            'amount': float(amount),
            'added_by': user_id,
            'added_at': datetime.now().isoformat(),
            'remarks': remarks
        }
        additional_fees.append(new_fee)
        
        # Update fee structure
        fee_structure.additional_fees = json.dumps(additional_fees)
        
        # Recalculate total
        additional_total = sum(float(f['amount']) for f in additional_fees)
        fee_structure.total_fees = fee_structure.base_fees + additional_total
        # balance is a calculated property
        
        db.session.commit()
        
        return {
            'success': True,
            'fee_structure_id': fee_structure.fee_structure_id,
            'base_fees': fee_structure.base_fees,
            'additional_fees': additional_fees,
            'additional_total': additional_total,
            'total_fees': fee_structure.total_fees,
            'balance': fee_structure.balance
        }
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}


def remove_additional_fee(student_id, academic_year, fee_index):
    """
    Remove an additional fee from student's fee structure
    
    Args:
        student_id: Student ID
        academic_year: Academic year
        fee_index: Index of fee to remove in the additional_fees array
        
    Returns:
        dict: Success status
    """
    try:
        fee_structure = FeeStructure.query.filter_by(
            student_id=student_id,
            academic_year=academic_year,
            is_deleted=False
        ).first()
        
        if not fee_structure:
            return {'success': False, 'error': 'Fee structure not found'}
        
        # Parse additional fees
        additional_fees = []
        if fee_structure.additional_fees:
            try:
                additional_fees = json.loads(fee_structure.additional_fees)
            except:
                return {'success': False, 'error': 'Invalid additional fees data'}
        
        # Remove fee at index
        if 0 <= fee_index < len(additional_fees):
            removed_fee = additional_fees.pop(fee_index)
        else:
            return {'success': False, 'error': 'Invalid fee index'}
        
        # Update fee structure
        fee_structure.additional_fees = json.dumps(additional_fees) if additional_fees else None
        
        # Recalculate total
        additional_total = sum(float(f['amount']) for f in additional_fees)
        fee_structure.total_fees = fee_structure.base_fees + additional_total
        # Note: balance is automatically calculated as a property
        
        db.session.commit()
        
        return {
            'success': True,
            'removed_fee': removed_fee,
            'total_fees': fee_structure.total_fees
        }
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}


def get_student_fee_breakdown(student_id, academic_year=None):
    """
    Get complete fee breakdown for a student
    
    Args:
        student_id: Student ID
        academic_year: Optional academic year filter
        
    Returns:
        dict: Fee breakdown with all details
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return {'success': False, 'error': 'Student not found'}
        
        # Use current academic year if not specified
        if not academic_year:
            academic_year = student.current_academic_year
        
        fee_structure = FeeStructure.query.filter_by(
            student_id=student_id,
            academic_year=academic_year,
            is_deleted=False
        ).first()
        
        if not fee_structure:
            return {
                'success': True,
                'has_fee': False,
                'message': 'No fee structure assigned for this academic year'
            }
        
        # Parse additional fees
        additional_fees = []
        if fee_structure.additional_fees:
            try:
                additional_fees = json.loads(fee_structure.additional_fees)
            except:
                pass
        
        return {
            'success': True,
            'has_fee': True,
            'student': {
                'student_id': student.student_id,
                'name': student.name,
                'roll_number': student.roll_number,
                'seat_type': student.seat_type,
                'quota_type': student.quota_type,
                'joining_year': student.joining_academic_year,
                'current_year': student.current_academic_year
            },
            'fee_structure': {
                'fee_structure_id': fee_structure.fee_structure_id,
                'academic_year': fee_structure.academic_year,
                'base_fees': fee_structure.base_fees,
                'additional_fees': additional_fees,
                'additional_total': sum(float(f['amount']) for f in additional_fees),
                'total_fees': fee_structure.total_fees,
                'amount_paid': fee_structure.amount_paid or 0,
                'balance': fee_structure.balance or fee_structure.total_fees
            },
            'template': fee_structure.template.to_dict() if fee_structure.template else None
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
