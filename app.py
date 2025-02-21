from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_very_secret_key'  # Replace with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Database Models ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200))
    cellphone = db.Column(db.String(20))
    profile_pic = db.Column(db.String(200), default='defaultpic.png')
    password = db.Column(db.String(200), nullable=False)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_main_admin = db.Column(db.Boolean, default=False)  # Add this field

#validate Password

def validate_password(password):
    """
    Validates password complexity.

    Args:
        password: The password to validate.

    Returns:
        True if the password meets the criteria, False otherwise.
    """

    if len(password) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return False

    if not re.search("[a-z]", password):
        flash('Password must contain at least one lowercase letter.', 'danger')
        return False

    if not re.search("[A-Z]", password):
        flash('Password must contain at least one uppercase letter.', 'danger')
        return False

    if not re.search("[0-9]", password):
        flash('Password must contain at least one digit.', 'danger')
        return False

    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        flash('Password must contain at least one special character.', 'danger')
        return False

    # Optional: Check against a list of common passwords
    # with open("common_passwords.txt", "r") as f:
    #     common_passwords = [line.strip() for line in f]
    #     if password in common_passwords:
    #         flash('Password is too common. Please choose a different one.', 'danger')
    #         return False

    return True

# --- User Loader for Flask-Login ---

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    return None  # Explicitly return None if no user/admin is found

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':  # Add Cache-Control headers for GET requests
        response = make_response(render_template('login.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        user = User.query.filter((User.name == identifier) | (User.email == identifier)).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username/email or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        response = make_response(render_template('signup.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        cellphone = request.form['cellphone']
        password = request.form['password']

        # Validate password complexity
        if not validate_password(password):
            return render_template('signup.html')  # Stay on the signup page

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, address=address, cellphone=cellphone, password=hashed_password, profile_pic='defaultpic.png')
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_authenticated:
        flash('Access denied. Please log in.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.email = request.form['email']
        current_user.address = request.form['address']
        current_user.cellphone = request.form['cellphone']

        # if 'profile_pic' in request.files:
        #     file = request.files['profile_pic']
        #     if file.filename != '':
        #         filename = current_user.name + "_" + file.filename
        #         file.save(os.path.join('static', filename))
        #         current_user.profile_pic = filename

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))

    response = make_response(render_template('profile.html', user=current_user))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':  # Add Cache-Control headers for GET requests
        response = make_response(render_template('admin_login.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        admin = Admin.query.filter_by(name=name).first()

        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin name or password.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    if current_user.is_main_admin:
        # Main admin: Fetch all users, secondary admins, and main admins
        users = User.query.all()
        secondary_admins = Admin.query.filter_by(is_main_admin=False).all()
        main_admins = Admin.query.filter_by(is_main_admin=True).all()  # Fetch main admins
    else:
        # Secondary admin: Only fetch all users
        users = User.query.all()
        secondary_admins = []  # Empty list for secondary admins
        main_admins = []  # Empty list for main admins

    response = make_response(render_template('admin_dashboard.html', users=users, secondary_admins=secondary_admins, main_admins=main_admins, admin_name=current_user.name, is_main_admin=current_user.is_main_admin))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_authenticated or not isinstance(current_user, Admin):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/new_admin', methods=['GET', 'POST'])
@login_required
def new_admin():
    if not current_user.is_authenticated or not isinstance(current_user, Admin):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'GET':  # Add Cache-Control headers for GET requests
        response = make_response(render_template('new_admin.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        # Validate password complexity
        if not validate_password(password):
            return render_template('new_admin.html')  # Stay on the new_admin page


        # Check if admin name already exists
        existing_admin = Admin.query.filter_by(name=name).first()
        if existing_admin:
            flash('Admin name already taken. Please choose a different name.', 'danger')
            return render_template('new_admin.html')  # Stay on the form

        if current_user.is_main_admin:
            is_main_admin = request.form.get('is_main_admin') == 'on'  # Checkbox value
        else:
            is_main_admin = False  # Default to False if not main admin creating the admin

        hashed_password = generate_password_hash(password)
        new_admin = Admin(name=name, password=hashed_password, is_main_admin=is_main_admin)  # Set is_main_admin directly
        db.session.add(new_admin)

        try:
            db.session.commit()
            flash('New admin created!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating admin: {e}', 'danger')
            return render_template('new_admin.html')  # Stay on the form

    return render_template('new_admin.html')

@app.route('/delete_admin', methods=['POST'])
@login_required
def delete_admin():
    if not current_user.is_authenticated or not isinstance(current_user, Admin):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    admin_id = current_user.id
    admin_to_delete = Admin.query.get_or_404(admin_id)

    # Allow secondary admins to delete their own accounts
    if not current_user.is_main_admin and admin_to_delete.id != current_user.id:
        flash('Access denied. You can only delete your own account.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Prevent main admin deletion from this route if there are other admins
    if admin_to_delete.is_main_admin:
        flash('Main admin account cannot be deleted from here.', 'warning')
        return redirect(url_for('admin_dashboard'))

    logout_user()

    db.session.delete(admin_to_delete)
    db.session.commit()

    flash('Admin account deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_secondary_admin/<int:admin_id>', methods=['POST'])
@login_required
def delete_secondary_admin(admin_id):
    if not current_user.is_authenticated or not current_user.is_main_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    admin = Admin.query.get_or_404(admin_id)

    # Prevent main admin deletion
    if admin.is_main_admin:
        flash('Cannot delete main admin accounts.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Prevent main admin deletion and self-deletion
    if admin.is_main_admin or admin.id == current_user.id:
        flash('Cannot delete main admin or yourself.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(admin)
    db.session.commit()
    flash('Secondary admin deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# @app.route('/change_password', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     if request.method == 'POST':
#         old_password = request.form['old_password']
#         new_password = request.form['new_password']
#         confirm_new_password = request.form['confirm_new_password']

#         # Check if old password is correct
#         if not check_password_hash(current_user.password, old_password):
#             flash('Incorrect old password.', 'danger')
#             return render_template('change_password.html')

#         # Check if new password and confirmation match
#         if new_password != confirm_new_password:
#             flash('New passwords do not match.', 'danger')
#             return render_template('change_password.html')

#         # Update the password
#         current_user.password = generate_password_hash(new_password)
#         db.session.commit()

#         flash('Password changed successfully!', 'success')
#         # Redirect to profile or admin dashboard based on user type
#         if isinstance(current_user, Admin):
#             return redirect(url_for('admin_dashboard'))
#         else:
#             return redirect(url_for('profile'))

#     return render_template('change_password.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    # Determine the correct back URL
    if isinstance(current_user, Admin):
        back_url = url_for('admin_dashboard')
    else:
        back_url = url_for('profile')

    if request.method == 'GET':
        response = make_response(render_template('change_password.html', back_url=back_url))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    elif request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        # Check if old password is correct
        if not check_password_hash(current_user.password, old_password):
            flash('Incorrect old password.', 'danger')
            return render_template('change_password.html', back_url=back_url)

        # Check if new password and confirmation match
        if new_password != confirm_new_password:
            flash('New passwords do not match.', 'danger')
            return render_template('change_password.html', back_url=back_url)

        # Validate password complexity
        if not validate_password(new_password):
            return render_template('change_password.html', back_url=back_url)

        # Update the password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        flash('Password changed successfully!', 'success')
        # Redirect based on user type
        if isinstance(current_user, Admin):
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('profile'))
        
@app.route('/update_profile_pic', methods=['POST'])
@login_required
def update_profile_pic():
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename != '':
            filename = current_user.name + "_" + file.filename
            file.save(os.path.join('static', filename))
            current_user.profile_pic = filename
            db.session.commit()
            flash('Profile picture updated!', 'success')

    return redirect(url_for('profile'))  # Redirect back to the profile page

if __name__ == '__main__':
    app.run(debug=True)