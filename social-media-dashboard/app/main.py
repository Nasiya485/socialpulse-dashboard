from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.models import db, SocialPost, Keyword
from textblob import TextBlob
import random

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/analytics/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    current_user = get_jwt_identity()
    
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    total_posts = SocialPost.query.count()
    posts_24h = SocialPost.query.filter(SocialPost.created_at >= last_24h).count()
    
    sentiment_counts = db.session.query(
        SocialPost.sentiment_label, func.count(SocialPost.id)
    ).group_by(SocialPost.sentiment_label).all()
    
    sentiment_data = {'positive': 0, 'negative': 0, 'neutral': 0}
    for label, count in sentiment_counts:
        if label:
            sentiment_data[label] = count
    
    avg_sentiment = db.session.query(func.avg(SocialPost.sentiment_score)).scalar() or 0
    active_keywords = Keyword.query.filter_by(is_active=True).count()
    
    return jsonify({
        'overview': {
            'total_posts_analyzed': total_posts,
            'posts_last_24h': posts_24h,
            'average_sentiment': round(avg_sentiment, 2),
            'active_keywords': active_keywords
        },
        'sentiment_distribution': sentiment_data
    }), 200

@main_bp.route('/api/analytics/simulate', methods=['POST'])
@jwt_required()
def simulate_posts():
    current_user = get_jwt_identity()
    
    sample_posts = [
        "I love this product! It's amazing!",
        "Terrible experience, would not recommend.",
        "It's okay, nothing special.",
        "Best purchase I've ever made!",
        "Very disappointed with the quality.",
        "Average product, does the job.",
        "Absolutely fantastic! Highly recommend!",
        "Waste of money, very unhappy.",
        "Pretty good, some minor issues.",
        "Excellent service and fast delivery."
    ]
    
    platforms = ['Twitter', 'Facebook', 'Instagram', 'LinkedIn']
    
    posts_created = []
    for _ in range(50):
        content = random.choice(sample_posts)
        blob = TextBlob(content)
        sentiment_score = blob.sentiment.polarity
        
        if sentiment_score > 0.1:
            label = 'positive'
        elif sentiment_score < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        post = SocialPost(
            platform=random.choice(platforms),
            author=f"user_{random.randint(1, 100)}",
            content=content,
            sentiment_score=sentiment_score,
            sentiment_label=label,
            like_count=random.randint(0, 1000),
            share_count=random.randint(0, 500),
            analyzed_by_id=current_user['id']
        )
        db.session.add(post)
        posts_created.append(post)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Created {len(posts_created)} simulated posts',
        'posts_count': len(posts_created)
    }), 201
