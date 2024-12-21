from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Admin
from . import app, login_manager
import os

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    return Admin.query.get(int(user_id))

# --- Routes for User Authentication ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        cellphone = request.form['cellphone']
        password = request.form['password']
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
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.email = request.form['email']
        current_user.address = request.form['address']
        current_user.cellphone = request.form['cellphone']

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filename = current_user.name + "_" + file.filename
                file.save(os.path.join('static', filename))
                current_user.profile_pic = filename

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# --- Routes for Admin Functionality ---
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
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

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users, admin_name=current_user.name)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not isinstance(current_user, Admin):
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
    if not isinstance(current_user, Admin):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_admin = Admin(name=name, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        flash('New admin created!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('new_admin.html')

@app.route('/delete_admin', methods=['POST'])
@login_required
def delete_admin():
    if not isinstance(current_user, Admin):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    admin_id = current_user.id
    logout_user()

    admin = Admin.query.get_or_404(admin_id)
    db.session.delete(admin)
    db.session.commit()

    flash('Admin account deleted!', 'success')
    return redirect(url_for('index'))