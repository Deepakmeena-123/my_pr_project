#!/usr/bin/env python
"""
Emergency database fix script for Render deployment
Run this if the database tables are missing
"""

import os
import sys
import django
from django.core.management import execute_from_command_line, call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings_production')

def fix_database():
    """Fix database issues by recreating tables"""
    print("🔧 EMERGENCY DATABASE FIX")
    print("=" * 50)
    
    try:
        # Setup Django
        django.setup()
        
        # Test database connection
        print("1️⃣ Testing database connection...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✅ Connected to: {version}")
        
        # Check if tables exist
        print("2️⃣ Checking if tables exist...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%customuser%'
            """)
            table_count = cursor.fetchone()[0]
            
            if table_count > 0:
                print(f"✅ Found {table_count} CustomUser table(s)")
                
                # Test if we can query the table
                try:
                    from student_management_app.models import CustomUser
                    user_count = CustomUser.objects.count()
                    print(f"✅ Database is working! Found {user_count} users")
                    return True
                except Exception as e:
                    print(f"⚠️ Table exists but query failed: {e}")
                    print("Proceeding with migration reset...")
            else:
                print("❌ CustomUser table not found")
        
        # Reset migrations and recreate tables
        print("3️⃣ Resetting migrations...")
        
        # Drop migration history
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS django_migrations CASCADE")
            print("✅ Migration history cleared")
        
        # Create fresh migrations
        print("4️⃣ Creating fresh migrations...")
        call_command('makemigrations', 'student_management_app', verbosity=1)
        call_command('makemigrations', verbosity=1)
        
        # Apply migrations
        print("5️⃣ Applying migrations...")
        call_command('migrate', verbosity=1)
        
        # Verify tables were created
        print("6️⃣ Verifying tables...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%customuser%'
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"✅ Tables created: {[t[0] for t in tables]}")
            else:
                print("❌ Tables still not found!")
                return False
        
        # Create admin user
        print("7️⃣ Creating admin user...")
        from student_management_app.models import CustomUser, AdminHOD, SessionYearModel, Courses
        from django.contrib.auth.hashers import make_password
        from datetime import datetime, timedelta
        
        # Create admin if doesn't exist
        if not CustomUser.objects.filter(username='admin').exists():
            admin_user = CustomUser.objects.create(
                username="admin",
                email="admin@example.com",
                first_name="System",
                last_name="Administrator",
                user_type=1,
                password=make_password("admin123")
            )
            AdminHOD.objects.create(admin=admin_user)
            print(f"✅ Admin user created: {admin_user.email}")
        else:
            print("✅ Admin user already exists")
        
        # Create default data
        if not SessionYearModel.objects.exists():
            today = datetime.now()
            next_year = today + timedelta(days=365)
            SessionYearModel.objects.create(
                session_start_year=today.date(),
                session_end_year=next_year.date()
            )
            print("✅ Session year created")
        
        if not Courses.objects.exists():
            Courses.objects.create(course_name="General Studies")
            print("✅ Default course created")
        
        print("🎉 DATABASE FIX COMPLETED!")
        print("\n📋 Login Credentials:")
        print("Admin: admin@example.com / admin123")
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_database()
    if not success:
        sys.exit(1)
