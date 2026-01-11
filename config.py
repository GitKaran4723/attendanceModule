"""
Configuration Settings for BCA BUB Attendance System
====================================================
This file contains all configuration settings for the application.
Different configurations can be used for development, testing, and production.
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration class with default settings.
    """
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    # SQLite for development (change to PostgreSQL/MySQL in production)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'attendance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security Settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # File Upload Settings (if needed in future)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    
    # Timezone Configuration
    TIMEZONE = 'Asia/Kolkata'  # Indian Standard Time (IST)


class DevelopmentConfig(Config):
    """
    Development configuration with debug mode enabled.
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log all SQL queries


class ProductionConfig(Config):
    """
    Production configuration with enhanced security.
    """
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE-THIS-IN-PRODUCTION'
    
    def __init__(self):
        if not os.environ.get('SECRET_KEY'):
            import warnings
            warnings.warn("SECRET_KEY not set! Using default. Set SECRET_KEY environment variable in production!")


class TestingConfig(Config):
    """
    Testing configuration for unit tests.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests
    WTF_CSRF_ENABLED = False


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
