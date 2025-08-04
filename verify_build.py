#!/usr/bin/env python3
"""
Verify that the build process will work on Render
This simulates what happens during deployment
"""

import os
import sys
import django

def verify_build():
    """Verify the build process"""
    print("🔍 Verifying build process...")
    
    # Set environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
    
    try:
        # Test Django setup
        print("1️⃣ Testing Django setup...")
        django.setup()
        print("✅ Django setup successful")
        
        # Test database connection
        print("2️⃣ Testing database connection...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        
        # Test migrations exist
        print("3️⃣ Checking migrations...")
        from django.core.management import call_command
        from io import StringIO
        
        # Capture output
        out = StringIO()
        call_command('showmigrations', 'student_management_app', stdout=out)
        migrations_output = out.getvalue()
        
        if 'student_management_app' in migrations_output:
            print("✅ Migrations found")
            print(f"📋 Migration status:\n{migrations_output}")
        else:
            print("❌ No migrations found")
            return False
            
        # Test models can be imported
        print("4️⃣ Testing model imports...")
        from student_management_app.models import CustomUser, AdminHOD, SessionYearModel
        print("✅ Models imported successfully")
        
        print("🎉 Build verification complete - all checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Build verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_build()
    sys.exit(0 if success else 1)
