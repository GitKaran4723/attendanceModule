"""Add elective support columns

Revision ID: 16519974a722
Revises: 
Create Date: 2026-01-10 12:04:46.264367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16519974a722'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Only add the columns we actually need for the elective feature
    # We skip 'sections' table modifications because they were applied via fix_sections_fk.py
    
    # 1. Subject Columns
    with op.batch_alter_table('subjects', schema=None) as batch_op:
        # Check if column exists first? No, Alembic script implies it doesn't.
        # But to be safe, we can try. However, standardized way is just to run it.
        # If it fails with "duplicate column", we know it's there.
        batch_op.add_column(sa.Column('subject_category', sa.Enum('compulsory', 'language', 'specialization', 'elective', name='subject_category_enum'), nullable=True))
        batch_op.add_column(sa.Column('elective_group', sa.String(length=100), nullable=True))

    # 2. StudentSubjectEnrollment Columns
    with op.batch_alter_table('student_subject_enrollments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('section_id', sa.String(length=36), nullable=True))
        batch_op.create_index(batch_op.f('ix_student_subject_enrollments_section_id'), ['section_id'], unique=False)
        batch_op.create_foreign_key('fk_student_subject_enrollments_section_id', 'sections', ['section_id'], ['section_id'])


def downgrade():
    with op.batch_alter_table('subjects', schema=None) as batch_op:
        batch_op.drop_column('elective_group')
        batch_op.drop_column('subject_category')

    with op.batch_alter_table('student_subject_enrollments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_student_subject_enrollments_section_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_student_subject_enrollments_section_id'))
        batch_op.drop_column('section_id')
