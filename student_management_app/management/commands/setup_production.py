"""
Django management command to set up production database
Usage: python manage.py setup_production
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.hashers import make_password
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Set up production database with tables and users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force setup even if tables exist',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔧 Setting up production database...")
        
        try:
            # Step 1: Check database connection
            self.stdout.write("1️⃣ Checking database connection...")
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0]
                self.stdout.write(f"✅ Connected to: {db_version}")

            # Step 2: Run migrations
            self.stdout.write("2️⃣ Creating and applying migrations...")
            
            # Create migrations
            self.stdout.write("📝 Creating migrations...")
            call_command('makemigrations', 'student_management_app', verbosity=0)
            call_command('makemigrations', verbosity=0)
            
            # Apply migrations
            self.stdout.write("🗄️ Applying migrations...")
            call_command('migrate', verbosity=1)
            
            # Step 3: Check if tables exist
            self.stdout.write("3️⃣ Verifying tables...")
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'student_management_app_customuser'
                    );
                """)
                tables_exist = cursor.fetchone()[0]
                
            if not tables_exist:
                self.stdout.write(self.style.ERROR("❌ Tables still don't exist after migration"))
                return
                
            self.stdout.write("✅ Database tables verified")

            # Step 4: Create users
            self.stdout.write("4️⃣ Creating users...")
            self.create_users(options['force'])
            
            self.stdout.write(self.style.SUCCESS("🎉 Production database setup complete!"))
            self.stdout.write("\n📋 Login Credentials:")
            self.stdout.write("Admin: admin@example.com / admin123")
            self.stdout.write("Teacher: teacher1@example.com / teacher123")
            self.stdout.write("Student: student1@example.com / student123")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Setup failed: {e}"))
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def create_users(self, force=False):
        """Create admin, teacher, and student users"""
        from student_management_app.models import CustomUser, AdminHOD, SessionYearModel
        
        # Create admin user
        if not CustomUser.objects.filter(username='admin').exists() or force:
            if force:
                CustomUser.objects.filter(username='admin').delete()
                
            self.stdout.write("👤 Creating admin user...")
            admin_user = CustomUser.objects.create(
                username="admin",
                email="admin@example.com",
                first_name="System",
                last_name="Administrator",
                user_type=1,
                password=make_password("admin123")
            )
            
            # Create AdminHOD instance
            AdminHOD.objects.get_or_create(admin=admin_user)
            self.stdout.write(f"✅ Admin user created: {admin_user.email}")
        else:
            self.stdout.write("✅ Admin user already exists")

        # Create teacher user
        if not CustomUser.objects.filter(username='teacher1').exists() or force:
            if force:
                CustomUser.objects.filter(username='teacher1').delete()
                
            self.stdout.write("👨‍🏫 Creating teacher user...")
            teacher_user = CustomUser.objects.create(
                username="teacher1",
                email="teacher1@example.com",
                first_name="John",
                last_name="Teacher",
                user_type=2,
                password=make_password("teacher123")
            )
            self.stdout.write(f"✅ Teacher user created: {teacher_user.email}")
        else:
            self.stdout.write("✅ Teacher user already exists")

        # Create student user
        if not CustomUser.objects.filter(username='student1').exists() or force:
            if force:
                CustomUser.objects.filter(username='student1').delete()
                
            self.stdout.write("👨‍🎓 Creating student user...")
            student_user = CustomUser.objects.create(
                username="student1",
                email="student1@example.com",
                first_name="Jane",
                last_name="Student",
                user_type=3,
                password=make_password("student123")
            )
            self.stdout.write(f"✅ Student user created: {student_user.email}")
        else:
            self.stdout.write("✅ Student user already exists")

        # Create default session year
        if not SessionYearModel.objects.exists() or force:
            if force:
                SessionYearModel.objects.all().delete()
                
            self.stdout.write("📅 Creating default session year...")
            SessionYearModel.objects.create(
                session_start_year="2024-01-01",
                session_end_year="2024-12-31"
            )
            self.stdout.write("✅ Session year created")
        else:
            self.stdout.write("✅ Session year already exists")
