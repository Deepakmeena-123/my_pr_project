#!/usr/bin/env python
"""
Ultra-lightweight WSGI application for Render free tier
Memory optimized for 512MB limit
"""

import os
import sys
import gc

# Memory optimization
gc.set_threshold(700, 10, 10)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')

# Quick database setup on startup
try:
    import django
    django.setup()

    # Check if database needs setup
    from student_management_app.models import CustomUser
    if not CustomUser.objects.filter(username='admin').exists():
        print("🔧 Setting up database...")
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])

        # Create admin user
        from django.contrib.auth.hashers import make_password
        CustomUser.objects.create(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            user_type=1,
            password=make_password("admin123")
        )
        print("✅ Admin created: admin@example.com / admin123")
except Exception as e:
    print(f"⚠️ Startup setup: {e}")

# Import WSGI application
from student_management_system.wsgi import application
app = application

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
