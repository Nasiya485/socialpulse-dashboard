from app import create_app, db
from app.models import User, Keyword, SocialPost, SystemLog
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Keyword': Keyword, 'SocialPost': SocialPost, 'SystemLog': SystemLog}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✓ Database tables created!")
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created (username: admin, password: admin123)")
        
        # Create sample keyword if none exist
        if Keyword.query.count() == 0:
            sample_keywords = ['technology', 'innovation', 'startup', 'ai', 'machinelearning']
            admin_user = User.query.filter_by(username='admin').first()
            for kw in sample_keywords:
                keyword = Keyword(text=kw, created_by=admin_user.id if admin_user else None)
                db.session.add(keyword)
            db.session.commit()
            print(f"✓ Added {len(sample_keywords)} sample keywords")
    
    port = int(os.environ.get('PORT', 5001))
    print(f"\n{'='*50}")
    print(f"🚀 Social Media Analytics Dashboard")
    print(f"📍 URL: http://127.0.0.1:{port}")
    print(f"👤 Admin Login: admin / admin123")
    print(f"{'='*50}\n")
    app.run(debug=True, host='127.0.0.1', port=port)
