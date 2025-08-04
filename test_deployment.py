#!/usr/bin/env python
"""
Test deployment configuration and database connectivity
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings_production')

def test_deployment():
    """Test deployment configuration"""
    print("🧪 DEPLOYMENT TEST")
    print("=" * 50)
    
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
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
        
        # Test models import
        print("3️⃣ Testing models import...")
        from student_management_app.models import CustomUser
        print("✅ Models import successful")
        
        # Test user count
        print("4️⃣ Testing user count...")
        user_count = CustomUser.objects.count()
        print(f"✅ Found {user_count} users in database")
        
        # Test admin user
        print("5️⃣ Testing admin user...")
        if CustomUser.objects.filter(username='admin').exists():
            admin = CustomUser.objects.get(username='admin')
            print(f"✅ Admin user found: {admin.email}")
        else:
            print("⚠️ Admin user not found")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("Your deployment should work correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_production_settings():
    """Test production settings"""
    print("\n🔧 PRODUCTION SETTINGS TEST")
    print("=" * 50)
    
    try:
        from student_management_system import settings_production
        
        # Check database configuration
        if hasattr(settings_production, 'DATABASES'):
            db_engine = settings_production.DATABASES['default']['ENGINE']
            print(f"✅ Database engine: {db_engine}")
            
            if 'postgresql' in db_engine:
                print("✅ Using PostgreSQL (production ready)")
            else:
                print("⚠️ Using SQLite (development mode)")
        
        # Check debug setting
        debug = getattr(settings_production, 'DEBUG', True)
        print(f"✅ DEBUG setting: {debug}")
        
        # Check allowed hosts
        allowed_hosts = getattr(settings_production, 'ALLOWED_HOSTS', [])
        print(f"✅ ALLOWED_HOSTS: {allowed_hosts}")
        
        return True
        
    except Exception as e:
        print(f"❌ Production settings test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_production_settings() and test_deployment()
    
    if success:
        print("\n🚀 DEPLOYMENT READY!")
        print("You can now deploy to Render.")
    else:
        print("\n⚠️ DEPLOYMENT ISSUES FOUND")
        print("Please fix the issues before deploying.")
        sys.exit(1)
