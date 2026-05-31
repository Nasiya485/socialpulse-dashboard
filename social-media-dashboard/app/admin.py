from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Keyword, SocialPost, SystemLog
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/keywords', methods=['GET'])
@admin_required
def get_keywords():
    keywords = Keyword.query.all()
    return jsonify({'keywords': [k.to_dict() for k in keywords]}), 200

@admin_bp.route('/keywords', methods=['POST'])
@admin_required
def create_keyword():
    data = request.get_json()
    
    if not data.get('text'):
        return jsonify({'error': 'Keyword text is required'}), 400
    
    existing = Keyword.query.filter_by(text=data['text'].lower()).first()
    if existing:
        return jsonify({'error': 'Keyword already exists'}), 409
    
    current_user = get_jwt_identity()
    keyword = Keyword(text=data['text'].lower(), created_by=current_user['id'])
    
    db.session.add(keyword)
    db.session.commit()
    
    return jsonify({'message': 'Keyword created', 'keyword': keyword.to_dict()}), 201

@admin_bp.route('/keywords/<int:keyword_id>', methods=['PUT'])
@admin_required
def update_keyword(keyword_id):
    keyword = Keyword.query.get(keyword_id)
    if not keyword:
        return jsonify({'error': 'Keyword not found'}), 404
    
    data = request.get_json()
    
    if 'text' in data:
        keyword.text = data['text'].lower()
    if 'is_active' in data:
        keyword.is_active = data['is_active']
    
    db.session.commit()
    return jsonify({'message': 'Keyword updated', 'keyword': keyword.to_dict()}), 200

@admin_bp.route('/keywords/<int:keyword_id>', methods=['DELETE'])
@admin_required
def delete_keyword(keyword_id):
    keyword = Keyword.query.get(keyword_id)
    if not keyword:
        return jsonify({'error': 'Keyword not found'}), 404
    
    db.session.delete(keyword)
    db.session.commit()
    return jsonify({'message': 'Keyword deleted'}), 200

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_system_stats():
    total_users = User.query.count()
    total_posts = SocialPost.query.count()
    total_keywords = Keyword.query.count()
    
    return jsonify({
        'users': {'total': total_users},
        'content': {'posts_analyzed': total_posts, 'tracked_keywords': total_keywords}
    }), 200
