
class StudentEnrollment(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Track which students are enrolled in which subjects
    Handles both core (auto) and elective (manual) enrollments
    """
    __tablename__ = "student_enrollments"
    
    enrollment_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    student_id = db.Column(db.String(36), db.ForeignKey("students.student_id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.subject_id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.section_id"), nullable=True, index=True)
    
    enrollment_type = db.Column(db.Enum("core", "elective", "specialization", name="enrollment_type_enum"), default="core")
    enrollment_status = db.Column(db.Enum("active", "dropped", "completed", name="enrollment_status_enum"), default="active")
    
    # Academic tracking
    semester_enrolled = db.Column(db.Integer)  # Which semester they enrolled
    academic_year = db.Column(db.String(20))  # e.g., "2023-24"
    
    # Relationships
    student = db.relationship("Student", backref=db.backref("enrollments", lazy="dynamic"))
    subject = db.relationship("Subject", backref=db.backref("enrollments", lazy="dynamic"))
    section = db.relationship("Section")
    
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "is_deleted", name="uix_student_subject_enrollment"),
    )
    
    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'section_id': self.section_id,
            'enrollment_type': self.enrollment_type,
            'enrollment_status': self.enrollment_status,
            'semester_enrolled': self.semester_enrolled,
            'academic_year': self.academic_year,
            'student_name': self.student.name if self.student else None,
            'subject_name': self.subject.subject_name if self.subject else None
        }
    
    def __repr__(self):
        return f"<StudentEnrollment {self.student_id} -> {self.subject_id}>"
