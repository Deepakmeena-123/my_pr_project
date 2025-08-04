#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."
echo "🔍 Environment check..."
echo "DATABASE_URL: ${DATABASE_URL:0:20}..." # Show first 20 chars only for security
echo "Python version: $(python --version)"

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Checking environment..."
echo "DATABASE_URL exists: $([ -n "$DATABASE_URL" ] && echo "Yes" || echo "No")"
echo "SECRET_KEY exists: $([ -n "$SECRET_KEY" ] && echo "Yes" || echo "No")"

echo "🗄️ Creating database tables..."

# First, check if we can connect to the database
echo "Testing database connection..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings_production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

echo "Running makemigrations..."
python manage.py makemigrations student_management_app --noinput || echo "⚠️ No new migrations for student_management_app"
python manage.py makemigrations --noinput || echo "⚠️ No new migrations"

echo "Running migrations..."
python manage.py migrate --noinput --verbosity=2 || {
    echo "❌ Migration failed! Attempting database reset..."
    python manage.py reset_production_db --confirm || {
        echo "❌ Database reset also failed! Manual intervention required."
        exit 1
    }
}

echo "Verifying tables were created..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings_production')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%customuser%'\")
    tables = cursor.fetchall()
    if tables:
        print(f'✅ CustomUser table found: {tables}')
    else:
        print('❌ CustomUser table not found!')
        # Try to list all tables
        cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\")
        all_tables = cursor.fetchall()
        print(f'Available tables: {all_tables}')
        exit(1)
"

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --clear

# Set up production database with default data
echo "👤 Setting up default admin user and data..."
python manage.py setup_production || {
    echo "❌ Production setup failed, trying alternative setup..."
    python setup_production_db.py
}

echo "🔍 Verifying database setup..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()
from django.db import connection
print(f'Database engine: {connection.settings_dict[\"ENGINE\"]}')
if 'postgresql' in connection.settings_dict['ENGINE']:
    print('✅ Using PostgreSQL (persistent storage)')
else:
    print('⚠️ Using SQLite (temporary storage)')

from student_management_app.models import CustomUser
print(f'Total users in database: {CustomUser.objects.count()}')
if CustomUser.objects.filter(username='admin').exists():
    print('✅ Admin user exists')
else:
    print('❌ Admin user missing')
"

echo "✅ Build completed successfully!"
