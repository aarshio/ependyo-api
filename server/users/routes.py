import jwt
import datetime
import uuid
from flask import request, jsonify, Blueprint, current_app
from server import db, bcrypt, mail
from server.models import User
from flask_mail import Message


users = Blueprint('users', __name__)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Ependyo Password Reset Request', sender='noreply@ependyo.com',recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
https://www.ependyo.com/password?token={token}

If you did not make this request, please ignore this email.
    '''
    mail.send(msg)

@users.route('/api/reset', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':
        init_data = request.get_json(silent=True)
        email = init_data.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            return jsonify({'status': '200'})
        else:
            return jsonify({'status': '403'})

    return jsonify({'status': '403'})

@users.route('/api/password', methods=['POST', 'GET'])
def password():
    init_data = request.get_json(silent=True)
    token = init_data.get('token')
    password = init_data.get('password')
    user = User.verify_reset_token(token)
    if user == None:
        return({'status':'403'})
    else:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        return jsonify({'status': '200'})

    return jsonify({'status': '403'})    

@users.route('/api/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        init_data = request.get_json(silent=True)
        data = {'username': init_data.get(
            'username'), 'password': init_data.get('password'), 'email': init_data.get('email')}
        if data['email']:
            user = User.query.filter_by(email=data['username']).first()
        else:
             user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            token = jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(hours=24)}, current_app.config['SECRET_KEY'])
            return jsonify({'token': token.decode('UTF-8')})
        else:
            return jsonify({'token': 'invalid'})
    return jsonify({'token': 'invalid'})

@users.route('/api/logout', methods=['POST', 'GET'])
def logout():
    # for key in session.keys():
    #     session.pop(key)
    # session.clear()
    return jsonify({'status': '200'})

@users.route('/api/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        init_data = request.get_json(silent=True)
        data = {'username': init_data.get('username'), 'email': init_data.get(
            'email'), 'password': init_data.get('password')}
        hashed_password = bcrypt.generate_password_hash(
            data['password']).decode('utf-8')
        check_username = User.query.filter_by(
            username=data['username']).first()
        check_email = User.query.filter_by(email=data['email']).first()
        if check_username:
            return jsonify({'error': "user exists"})
        elif check_email:
            return jsonify({'error': "email exists"})
        else:
            user = User(id=uuid.uuid4(
            ).hex, username=data['username'], email=data['email'], password=hashed_password)
            db.session.add(user)
            db.session.commit()
            token = jwt.encode({'username': data['username'], 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(hours=24)}, current_app.config['SECRET_KEY'])
            return({'token': token.decode('UTF-8')})
    else:
        return jsonify({'status': '404'})


@users.route('/api/get_user', methods=['GET', 'POST'])
def get_user():
    if request.method == 'GET':
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        return jsonify({'user': user.to_json()})


@users.route('/api/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        init_data = request.get_json(silent=True)
        data = {'user': init_data.get('user')["username"]}
        User.query.filter_by(username=data['user']).delete()
        db.session.commit()
        return jsonify({'status': '200'})


@users.route('/api/update_bio', methods=['GET', 'POST'])
def update_bio():
    if request.method == 'POST':
        init_data = request.get_json(silent=True)
        data = {'username': init_data.get(
            'username'), 'bio': init_data.get('bio')}
        user = User.query.filter_by(username=data['username']).first()
        user.bio = data['bio']
        db.session.commit()
        return jsonify({'status': "updated"})
