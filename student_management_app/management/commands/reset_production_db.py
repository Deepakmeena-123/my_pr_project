from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.hashers import make_password
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Reset production database - DROP ALL TABLES and recreate'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to DROP ALL TABLES',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.ERROR("⚠️ This command will DROP ALL TABLES!"))
            self.stdout.write("Use --confirm flag if you're sure:")
            self.stdout.write("python manage.py reset_production_db --confirm")
            return

        self.stdout.write("🔥 RESETTING PRODUCTION DATABASE...")
        self.stdout.write(self.style.WARNING("This will DROP ALL TABLES!"))
        
        try:
            # Step 1: Drop all tables
            self.stdout.write("1️⃣ Dropping all tables...")
            with connection.cursor() as cursor:
                # Get all table names
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                """)
                tables = cursor.fetchall()
                
                if tables:
                    # Drop all tables
                    for table in tables:
                        table_name = table[0]
                        self.stdout.write(f"Dropping table: {table_name}")
                        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                    
                    self.stdout.write(f"✅ Dropped {len(tables)} tables")
                else:
                    self.stdout.write("✅ No tables to drop")

            # Step 2: Reset migrations
            self.stdout.write("2️⃣ Resetting migrations...")
            
            # Remove migration records
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS django_migrations CASCADE")
                self.stdout.write("✅ Migration history cleared")

            # Step 3: Create fresh migrations
            self.stdout.write("3️⃣ Creating fresh migrations...")
            call_command('makemigrations', 'student_management_app', verbosity=1)
            call_command('makemigrations', verbosity=1)

            # Step 4: Apply migrations
            self.stdout.write("4️⃣ Applying migrations...")
            call_command('migrate', verbosity=1)

            # Step 5: Create users
            self.stdout.write("5️⃣ Creating users...")
            self.create_users()
            
            self.stdout.write(self.style.SUCCESS("🎉 Database reset complete!"))
            self.stdout.write("\n📋 Login Credentials:")
            self.stdout.write("Admin: admin@example.com / admin123")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Reset failed: {e}"))
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def create_users(self):
        """Create admin user"""
        from student_management_app.models import CustomUser, AdminHOD, SessionYearModel, Courses
        from datetime import datetime, timedelta
        
        # Create admin user
        admin_user = CustomUser.objects.create(
            username="admin",
            email="admin@example.com",
            first_name="System",
            last_name="Administrator",
            user_type=1,
            password=make_password("admin123")
        )
        
        # Create AdminHOD instance
        AdminHOD.objects.create(admin=admin_user)
        self.stdout.write(f"✅ Admin user created: {admin_user.email}")

        # Create default session year
        today = datetime.now()
        next_year = today + timedelta(days=365)
        
        SessionYearModel.objects.create(
            session_start_year=today.date(),
            session_end_year=next_year.date()
        )
        self.stdout.write("✅ Session year created")

        # Create default course
        Courses.objects.create(course_name="General Studies")
        self.stdout.write("✅ Default course created")
