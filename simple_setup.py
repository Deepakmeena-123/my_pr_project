#!/usr/bin/env python3
"""
Simple database setup script
Run this to create tables and admin user
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.hashers import make_password

def setup_database():
    print("🔧 Setting up database...")
    
    try:
        # Run migrations
        print("📝 Creating migrations...")
        call_command('makemigrations', 'student_management_app', verbosity=0)
        call_command('makemigrations', verbosity=0)
        
        print("🗄️ Applying migrations...")
        call_command('migrate', verbosity=0)
        
        # Create users
        from student_management_app.models import CustomUser
        
        # Check if admin exists
        if not CustomUser.objects.filter(username='admin').exists():
            print("👤 Creating admin user...")
            CustomUser.objects.create(
                username="admin",
                email="admin@example.com",
                first_name="System",
                last_name="Administrator",
                user_type=1,
                password=make_password("admin123")
            )
            print("✅ Admin created: admin@example.com / admin123")
        else:
            print("✅ Admin user already exists")
            
        print("🎉 Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_database()
