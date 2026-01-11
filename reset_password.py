
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='karansj4723').first()
    if user:
        user.password_hash = generate_password_hash('password123')
        db.session.commit()
        print('Password reset successful for karansj4723')
    else:
        print('User not found')
