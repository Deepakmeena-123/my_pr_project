#!/usr/bin/env python3
"""
Lightweight startup script for Render free tier
Handles database setup if build command fails
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_database():
    """Quick database setup"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
    django.setup()
    
    try:
        # Check if tables exist
        from student_management_app.models import CustomUser
        CustomUser.objects.count()
        print("✅ Database tables exist")
        return True
    except:
        print("🔧 Creating database tables...")
        try:
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            
            # Create admin user
            from django.contrib.auth.hashers import make_password
            admin_user = CustomUser.objects.create(
                username="admin",
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                user_type=1,
                password=make_password("admin123")
            )
            print("✅ Admin user created: admin@example.com / admin123")
            return True
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False

if __name__ == "__main__":
    setup_database()
