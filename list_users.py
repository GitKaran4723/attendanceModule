
from app import app
from models import db, User, Role

with app.app_context():
    users = db.session.query(User.username, Role.role_name).join(Role).all()
    print("--- USERS ---")
    for u in users:
        print(f"{u.username}: {u.role_name}")
    print("--- END ---")
