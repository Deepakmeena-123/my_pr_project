#!/usr/bin/env python
"""
Production Database Setup Script
This script sets up the database with default data for production deployment.
"""

import os
import django
from django.core.management import execute_from_command_line

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from student_management_app.models import CustomUser, AdminHOD, SessionYearModel
from django.contrib.auth.hashers import make_password

def setup_database():
    """Set up the database with default data"""

    print("🔄 Setting up production database...")

    try:
        # Check if admin already exists
        if CustomUser.objects.filter(username='admin').exists():
            print("✅ Admin user already exists")
        else:
            # Create admin user
            print("👤 Creating admin user...")
            admin_user = CustomUser.objects.create(
                username="admin",
                email="admin@example.com",
                first_name="System",
                last_name="Administrator",
                user_type=1,
                password=make_password("admin123")
            )

            # Create AdminHOD instance
            admin_hod = AdminHOD.objects.create(admin=admin_user)
            print(f"✅ Admin user created: {admin_user.email}")

        # Create sample teacher
        if not CustomUser.objects.filter(username='teacher1').exists():
            print("👨‍🏫 Creating sample teacher...")
            teacher_user = CustomUser.objects.create(
                username="teacher1",
                email="teacher1@example.com",
                first_name="John",
                last_name="Teacher",
                user_type=2,
                password=make_password("teacher123")
            )
            print(f"✅ Teacher user created: {teacher_user.email}")

        # Create sample student
        if not CustomUser.objects.filter(username='student1').exists():
            print("👨‍🎓 Creating sample student...")
            student_user = CustomUser.objects.create(
                username="student1",
                email="student1@example.com",
                first_name="Jane",
                last_name="Student",
                user_type=3,
                password=make_password("student123")
            )
            print(f"✅ Student user created: {student_user.email}")

        # Create default session year
        if not SessionYearModel.objects.exists():
            print("📅 Creating default session year...")
            session_year = SessionYearModel.objects.create(
                session_start_year="2024-01-01",
                session_end_year="2024-12-31"
            )
            print("✅ Session year created")

        print("🎉 Database setup completed successfully!")
        print("\n📋 Login Credentials:")
        print("Admin: admin@example.com / admin123")
        print("Teacher: teacher1@example.com / teacher123")
        print("Student: student1@example.com / student123")

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_database()
