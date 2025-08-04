from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Import database setup endpoint
from setup_db_endpoint import setup_database

urlpatterns = [
    path('admin/', admin.site.urls),
    path('setup-database/', setup_database, name='setup_database'),
    path('', include('student_management_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
