class SystemSettings(db.Model):
    """
    Global system configuration settings
    Stores key-value pairs for system-wide settings like current academic year
    """
    __tablename__ = "system_settings"
    
    setting_key = db.Column(db.String(50), primary_key=True)
    setting_value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime)
    updated_by = db.Column(db.String(36), db.ForeignKey("users.user_id"))
    
    # Relationships
    updated_by_user = db.relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<SystemSettings {self.setting_key}={self.setting_value}>"
    
    @staticmethod
    def get_current_academic_year():
        """Get the current academic year from settings"""
        setting = SystemSettings.query.get('current_academic_year')
        if setting:
            return setting.setting_value
        # Default to current year if not set
        from datetime import datetime
        current_year = datetime.now().year
        return f"{current_year}-{current_year + 1}"
    
    @staticmethod
    def set_current_academic_year(year, user_id=None):
        """Set the current academic year"""
        from datetime import datetime
        setting = SystemSettings.query.get('current_academic_year')
        if setting:
            setting.setting_value = year
            setting.updated_at = datetime.now()
            setting.updated_by = user_id
        else:
            setting = SystemSettings(
                setting_key='current_academic_year',
                setting_value=year,
                description='Current academic year for the entire system',
                updated_at=datetime.now(),
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting
