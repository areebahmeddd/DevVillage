from flask import Flask, redirect, render_template, request, session, url_for
from auth_routes import auth_blueprint
from discover_routes import discover_blueprint
from dashboard_routes import dashboard_blueprint, acc_nav_details
from verify_routes import verify_blueprint
from acc_info_routes import acc_info_blueprint
from firebase_admin import auth
from firebase_admin._auth_utils import UserNotFoundError
from flask_socketio import SocketIO, emit
from database import init_db, add_chat_message, get_chat_history

# Database
import firebase_admin
from firebase_admin import db, auth
from firebase_admin import credentials

# Initializing database
cred = credentials.Certificate("codebase-secret.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://codebase-93435-default-rtdb.europe-west1.firebasedatabase.app/"})

# Initializing flask app
app = Flask(__name__)
socketio = SocketIO(app)
app.register_blueprint(auth_blueprint)
app.register_blueprint(discover_blueprint)
app.register_blueprint(dashboard_blueprint)
app.register_blueprint(verify_blueprint)
app.register_blueprint(acc_info_blueprint)

# Remove session if current user is unverified
def session_remove_if_not_verified():
    # Exclude the 'verify' route function
    if request.endpoint != 'auth.verify':
        if session.get('verify'):
            try:
                user = auth.get_user(session.get('verify'))
                if not user.email_verified:
                    print("Deleting session verify of user", user.display_name)
                    session.pop('verify', None)
            except UserNotFoundError:
                session.pop('verify', None)

        else:
            print("No session found.")

# Applying flask configurations     --- To be kept secret ---
app.config['SECRET_KEY'] = 'h#@hbJHB$@uygAHB!3137yugas_niGaJKH@#nlNAUBKJ~/AS,.69<>ASDfl..911,aSFOJ'
app.config['RECAPTCHA_ENABLED'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcxaoEpAAAAAH92Ayj9QRJnLO8FRHDulED4OZOY'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcxaoEpAAAAAEOeRtpgYt_PDprYUmkVw_ryUl2p'
app.config['RECAPTCHA_THEME'] = 'dark'

# HOME
@app.route('/')
def home():
    session_remove_if_not_verified()
    if session.get('user_id'):
        if session.get('user_id')[:2] == 'I-':
            return redirect(url_for('dashboard.individuals'))
        else:
            return redirect(url_for('dashboard.organization'))

    return render_template("home.html")

@app.route('/homecomp')
def homecomp():
    session_remove_if_not_verified()
    if session.get('user_id'):
        if session.get('user_id')[:2] == 'I-':
            return redirect(url_for('dashboard.individuals'))
        else:
            return redirect(url_for('dashboard.organization'))
        
    return render_template("homecomp.html")

@app.route('/indi/chat')
def indi_chat():
    init_db()
    user_data = acc_nav_details(session.get("user_id"))
    if 'user_id' not in session:
        return redirect(url_for('home'))
    else:
        # Mock info, update this with actual data from the user database
        chat_info = [
            {
                'type': 'individual',
                'profile_pic': '/static/images/taha.png',
                'first_name': 'Taha',
                'last_name': 'Zakir',
                'recent_chat': 'We have sent the admin info via email to your registered email address.'
            }
        ]
        chat_history = get_chat_history()
        return render_template('chat.html', chat_info=chat_info, chat_history=chat_history, user_data=user_data)

@app.route('/org/view_profile')
def view_profile():
    resume = False
    user_data = acc_nav_details(session.get("user_id"))
    profile_info = {
        "Rating": 4.5,
        "Expertise": ['balls','no balls'],
        "Bio": 'Before Time Began',
        "Phone": 971456223434,
        "Email": 'Yourmom@yourmom.com',
    }

    return render_template('viewprofile.html', user_data = user_data, profile_info = profile_info, resume = resume)

@app.route('/org/chat')
def org_chat():
    init_db()
    user_data = acc_nav_details(session.get("user_id"))
    if 'user_id' not in session:
        return redirect(url_for('home'))
    else:
        # Mock info, update this with actual data from the user database
        chat_info = [
            {
                'type': 'individual',
                'profile_pic': '/static/images/taha.png',
                'first_name': 'Taha',
                'last_name': 'Zakir',
                'recent_chat': 'We have sent the admin info via email to your registered email address.'
            }
        ]
        chat_history = get_chat_history()
        return render_template('chat.html', chat_info=chat_info, chat_history=chat_history, user_data=user_data)

@socketio.on('message')
def handle_message(data):
    print('Received Message:', data)
    emit('message', {'user_id': session.get('user_id'), 'message': data['message']}, broadcast=True)

    user_id = session.get('user_id')
    if user_id:
        add_chat_message(user_id, data['message'])

if __name__ == '__main__':
    app.run(debug=True)
