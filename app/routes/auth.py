from flask import Blueprint, render_template,redirect,url_for,session,request
from app.database.models import db,User,Admin
import os

auth_bp = Blueprint('auth', __name__)
UPLOAD_FOLDER = 'app/static/faces'



@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user:
            if user.password == password:
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                return redirect(url_for('main.user', user=user))
            else:
                return "Invalid username/email or password. Please try again."
        else:
            return "Invalid username/email or password. Please try again."
    else:
        return render_template('signin.html')



@auth_bp.route('/signin_admin', methods=['GET', 'POST'])
def signin_admin():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        admin = Admin.query.filter((Admin.username == username_or_email) | (Admin.email == username_or_email)).first()

        if admin:
            if admin.password == password:
                session['admin_id'] = admin.id
                session['username'] = admin.username
                return redirect(url_for('main.admin', admin=admin))
            else:
                return "Invalid username/email or password. Please try again."
        else:
            return "Invalid username/email or password. Please try again."
    else:
        return render_template('adminsignin.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        is_admin = 'is_admin' in request.form

        if password != confirm_password:
            return "Password and Confirm Password do not match. Please try again."

        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename == '':
                avatar_data = None
            else:
                user_dir = os.path.join(UPLOAD_FOLDER, username)
                os.makedirs(user_dir, exist_ok=True)
                avatar_path = os.path.join(user_dir, avatar.filename)
                avatar.save(avatar_path)
                with open(avatar_path, 'rb') as f:
                    avatar_data = f.read()
        else:
            avatar_data = None

        new_user = User(username=username, email=email, password=password, is_admin=is_admin, avatar=avatar_data)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.signin'))

    return render_template('signup.html')
