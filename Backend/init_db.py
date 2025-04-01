from app import app, db, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have a test user
        test_user = User.query.filter_by(email="test@example.com").first()
        if not test_user:
            # Create a test user
            test_user = User(
                email="test@example.com",
                password_hash=generate_password_hash("password123"),
                prefers_fishing=True,
                prefers_hiking=True,
                prefers_solitude=False
            )
            db.session.add(test_user)
            db.session.commit()
            print("Created test user")
        else:
            print("Test user already exists")

if __name__ == "__main__":
    init_db() 