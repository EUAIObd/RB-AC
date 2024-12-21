from flask import Flask  # Even though it's a standalone, we still need Flask for SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# --- Configure Flask App (for SQLAlchemy) ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Connect to users.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Define Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200))
    cellphone = db.Column(db.String(20))
    profile_pic = db.Column(db.String(200), default='defaultpic.png')  # You might need to adjust this later
    password = db.Column(db.String(200), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_main_admin = db.Column(db.Boolean, default=False)

# --- Create Database and Tables ---
def create_database():
    with app.app_context():  # Create an application context
        #db.create_all()

        # --- Optionally add an initial admin user ---
        try:
            hashed_password = generate_password_hash("wq")
            admin = Admin(name="wq", password=hashed_password, is_main_admin=True)  # Set to True
            db.session.add(admin)
            db.session.commit()
            print("Initial admin user created.")
        except Exception as e:
            print(f"Could not create initial admin user. Error: {e}")
            db.session.rollback() # Roll back any uncommited changes

        print("Database and tables created successfully!")

if __name__ == "__main__":
    create_database()