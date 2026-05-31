from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"✅ Admin user found:")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   Password hash: {admin.password_hash[:50]}...")
        
        # Test password verification
        test_password = "admin123"
        if admin.check_password(test_password):
            print(f"   ✅ Password '{test_password}' is CORRECT")
        else:
            print(f"   ❌ Password '{test_password}' is INCORRECT")
    else:
        print("❌ No admin user found!")
    
    # List all users
    all_users = User.query.all()
    print(f"\n📋 All users in database ({len(all_users)}):")
    for user in all_users:
        print(f"   - {user.username} ({user.email}) - Role: {user.role}")
