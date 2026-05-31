from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from datetime import datetime
from app.models import db, User, SystemLog
import re

auth_bp = Blueprint('auth', __name__)

def log_activity(log_type, message, user_id=None, ip_address=None):
    log = SystemLog(
        log_type=log_type,
        message=message,
        user_id=user_id,
        ip_address=ip_address or request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    log_activity('auth', f'New user registration: {user.username}', user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.check_password(data['password']):
        log_activity('auth', f'Failed login attempt for {data["username"]}', ip_address=request.remote_addr)
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity={'id': user.id, 'role': user.role})
    
    log_activity('auth', f'Successful login: {user.username}', user.id)
    
    # Create response with cookie
    response = make_response(jsonify({
        'message': 'Login successful',
        'user': {'id': user.id, 'username': user.username, 'role': user.role}
    }))
    set_access_cookies(response, access_token)
    
    return response, 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    log_activity('auth', 'User logout', current_user['id'])
    
    response = make_response(jsonify({'message': 'Logged out successfully'}))
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_identity = get_jwt_identity()
    user = User.query.get(current_user_identity['id'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200
