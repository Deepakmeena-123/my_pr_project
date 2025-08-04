#!/usr/bin/env python3
"""
Database setup endpoint for Render free tier
Visit /setup-database/ to create tables and admin user
"""

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import execute_from_command_line
import os
import sys

@csrf_exempt
def setup_database(request):
    """Setup database tables and admin user"""
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
        import django
        django.setup()
        
        response_text = "<h1>🔧 Database Setup</h1><pre>"
        
        # Check if tables exist
        try:
            from student_management_app.models import CustomUser
            user_count = CustomUser.objects.count()
            response_text += f"✅ Database connected. Current users: {user_count}\n"
            
            if user_count > 0:
                response_text += "✅ Database already set up!\n"
                response_text += "Login: admin@example.com / admin123\n"
                response_text += "</pre><a href='/'>Go to Login</a>"
                return HttpResponse(response_text)
                
        except Exception as e:
            response_text += f"⚠️ Tables missing: {e}\n"
            response_text += "🔧 Creating database tables...\n"
            
            # Run migrations
            from django.core.management import call_command
            from io import StringIO
            
            # Capture output
            out = StringIO()
            
            # Make migrations
            response_text += "📝 Creating migrations...\n"
            call_command('makemigrations', 'student_management_app', stdout=out)
            call_command('makemigrations', stdout=out)
            
            # Apply migrations
            response_text += "🗄️ Applying migrations...\n"
            call_command('migrate', stdout=out)
            
            migration_output = out.getvalue()
            response_text += migration_output + "\n"
            
            # Create admin user
            response_text += "👤 Creating admin user...\n"
            from django.contrib.auth.hashers import make_password
            
            admin_user = CustomUser.objects.create(
                username="admin",
                email="admin@example.com",
                first_name="System",
                last_name="Administrator",
                user_type=1,
                password=make_password("admin123")
            )
            response_text += "✅ Admin user created: admin@example.com / admin123\n"
            
            # Create sample teacher
            teacher_user = CustomUser.objects.create(
                username="teacher1",
                email="teacher1@example.com", 
                first_name="Sample",
                last_name="Teacher",
                user_type=2,
                password=make_password("teacher123")
            )
            response_text += "✅ Teacher user created: teacher1@example.com / teacher123\n"
            
            # Create sample student
            student_user = CustomUser.objects.create(
                username="student1",
                email="student1@example.com",
                first_name="Sample", 
                last_name="Student",
                user_type=3,
                password=make_password("student123")
            )
            response_text += "✅ Student user created: student1@example.com / student123\n"
            
            response_text += "\n🎉 Database setup complete!\n"
            response_text += "</pre>"
            response_text += "<h2>✅ Ready to use!</h2>"
            response_text += "<p><a href='/'>Go to Login Page</a></p>"
            response_text += "<p><strong>Login credentials:</strong></p>"
            response_text += "<ul>"
            response_text += "<li>Admin: admin@example.com / admin123</li>"
            response_text += "<li>Teacher: teacher1@example.com / teacher123</li>"
            response_text += "<li>Student: student1@example.com / student123</li>"
            response_text += "</ul>"
            
            return HttpResponse(response_text)
            
    except Exception as e:
        error_text = f"<h1>❌ Database Setup Failed</h1><pre>Error: {e}</pre>"
        error_text += "<p><a href='/setup-database/'>Try Again</a></p>"
        return HttpResponse(error_text)
