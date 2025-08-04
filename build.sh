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
echo "Running makemigrations..."
python manage.py makemigrations student_management_app --noinput || echo "⚠️ No new migrations for student_management_app"
python manage.py makemigrations --noinput || echo "⚠️ No new migrations"

echo "Running migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --clear

# Set up production database with default data
echo "👤 Setting up default admin user and data..."
python setup_production_db.py

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
