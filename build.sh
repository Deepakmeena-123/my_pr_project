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

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "🗄️ Creating database tables..."
echo "Running makemigrations..."
python manage.py makemigrations student_management_app --noinput
python manage.py makemigrations --noinput

echo "Running migrations..."
python manage.py migrate --noinput

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
