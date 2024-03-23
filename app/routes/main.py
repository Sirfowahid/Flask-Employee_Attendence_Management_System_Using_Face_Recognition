from flask import Blueprint, render_template,redirect,url_for,session,request,Response
from app.database.models import User,Admin,db
import cv2
import os
import shutil

main_bp = Blueprint('main', __name__)
camera = None

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/user')
def user():
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)
        return render_template('user.html', user=user)
    else:
        return redirect(url_for('auth.signin'))


@main_bp.route('/admin')
def admin():
    admin_id = session.get('admin_id')

    if admin_id:
        admin = Admin.query.get(admin_id)
        users = User.query.all()
        return render_template('admin_userlist.html', admin=admin, users=users)
    else:
        return redirect(url_for('auth.signin_admin'))


@main_bp.route('/admin/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):

    admin_id = session.get('admin_id')
    if not admin_id:
        return redirect(url_for('auth.signin_admin'))

    admin = Admin.query.get(admin_id)

    user = User.query.get(user_id)

    if request.method == 'POST':
        
        user.username = request.form['username']
        user.email = request.form['email']


        db.session.commit()

        return redirect(url_for('main.admin'))

    return render_template('update.html', admin=admin, user=user)


@main_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user:
        user_directory = os.path.join('app', 'static', 'faces', user.username)

        try:
            shutil.rmtree(user_directory)
        except OSError as e:
            print(f"Error deleting user's directory: {e}")

        db.session.delete(user)
        db.session.commit()
    else:
        print(f"User with ID {user_id} not found.")

    return redirect(url_for('main.admin'))

    
@main_bp.route('/attendence')
def attendence():
    return render_template('attendence.html')


################## Camera #################
def gen_frames():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@main_bp.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main_bp.before_request
def before_request():
    global camera
    if request.path != '/video_feed':
        if camera is not None:
            camera.release()  
            camera = None

@main_bp.after_request
def after_request(response):
    global camera
    if request.path == '/video_feed':
        if camera is None:
            camera = cv2.VideoCapture(0)  
    return response
