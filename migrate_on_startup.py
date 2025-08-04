#!/usr/bin/env python3
"""
Migration script that runs on application startup
This ensures database tables are created even if build script fails
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.color import make_style

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
    django.setup()

def check_database_connection():
    """Check if database is accessible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_tables_exist():
    """Check if required tables exist"""
    try:
        from student_management_app.models import CustomUser
        CustomUser.objects.count()
        return True
    except Exception:
        return False

def run_migrations():
    """Run database migrations"""
    style = make_style()
    
    print(style.SUCCESS("🚀 Starting migration process..."))
    
    try:
        # Make migrations
        print("📝 Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'student_management_app', '--noinput'])
        execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
        
        # Apply migrations
        print("🗄️ Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        print(style.SUCCESS("✅ Migrations completed successfully!"))
        return True
        
    except Exception as e:
        print(style.ERROR(f"❌ Migration failed: {e}"))
        return False

def setup_initial_data():
    """Setup initial admin user and data"""
    try:
        # Import and run the setup script
        import subprocess
        result = subprocess.run([sys.executable, 'setup_production_db.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Initial data setup completed!")
            return True
        else:
            print(f"⚠️ Initial data setup had issues: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Initial data setup failed: {e}")
        return False

def main():
    """Main migration function"""
    style = make_style()
    
    print("=" * 60)
    print(style.SUCCESS("🔧 STARTUP MIGRATION SCRIPT"))
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Check database connection
    if not check_database_connection():
        print(style.ERROR("❌ Cannot connect to database. Exiting."))
        return False
    
    print(style.SUCCESS("✅ Database connection successful"))
    
    # Check if tables exist
    if check_tables_exist():
        print(style.SUCCESS("✅ Database tables already exist"))
        
        # Check if admin user exists
        try:
            from student_management_app.models import CustomUser
            if CustomUser.objects.filter(username='admin').exists():
                print(style.SUCCESS("✅ Admin user already exists"))
                print("🎉 Database is ready!")
                return True
            else:
                print("⚠️ Admin user missing, creating...")
                setup_initial_data()
        except Exception:
            pass
    else:
        print("⚠️ Database tables missing, creating...")
        
        # Run migrations
        if run_migrations():
            print("🔧 Setting up initial data...")
            setup_initial_data()
        else:
            print(style.ERROR("❌ Failed to create database tables"))
            return False
    
    print("=" * 60)
    print(style.SUCCESS("🎉 STARTUP MIGRATION COMPLETED!"))
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
