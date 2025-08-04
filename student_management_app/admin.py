from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm
from .models import (
    CustomUser, AdminHOD, Staffs, Courses, Subjects, Students,
    Attendance, AttendanceReport, SessionYearModel, AttendanceQRCode, StudentResult
)

# Custom User Admin with better data integrity
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )

    def save_model(self, request, obj, form, change):
        # Ensure email is unique and required
        if not obj.email:
            raise ValidationError("Email is required for all users.")
        super().save_model(request, obj, form, change)

# Session Year Admin with validation
class SessionYearAdmin(admin.ModelAdmin):
    list_display = ('session_display', 'session_start_year', 'session_end_year')
    list_filter = ('session_start_year', 'session_end_year')
    ordering = ('-session_start_year',)

    def clean(self):
        # Validate that end year is after start year
        if self.session_end_year <= self.session_start_year:
            raise ValidationError("Session end year must be after start year.")

    def save_model(self, request, obj, form, change):
        # Additional validation
        if obj.session_end_year <= obj.session_start_year:
            raise ValidationError("Session end year must be after start year.")
        super().save_model(request, obj, form, change)

# Course Admin with better management
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'created_at', 'updated_at')
    search_fields = ('course_name',)
    ordering = ('course_name',)

    def save_model(self, request, obj, form, change):
        # Ensure course name is unique (case-insensitive)
        if Courses.objects.filter(course_name__iexact=obj.course_name).exclude(pk=obj.pk).exists():
            raise ValidationError(f"A course with name '{obj.course_name}' already exists.")
        super().save_model(request, obj, form, change)

# Subject Admin with proper relationships
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'course_id', 'staff_id', 'created_at')
    list_filter = ('course_id', 'staff_id')
    search_fields = ('subject_name', 'course_id__course_name', 'staff_id__admin__username')
    ordering = ('subject_name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "staff_id":
            # Only show staff users in the dropdown
            kwargs["queryset"] = Staffs.objects.select_related('admin')
        elif db_field.name == "course_id":
            # Only show active courses
            kwargs["queryset"] = Courses.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Ensure subject name is unique within a course
        if Subjects.objects.filter(
            subject_name__iexact=obj.subject_name,
            course_id=obj.course_id
        ).exclude(pk=obj.pk).exists():
            raise ValidationError(f"Subject '{obj.subject_name}' already exists in course '{obj.course_id.course_name}'.")
        super().save_model(request, obj, form, change)

# Student Admin with proper validation
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_email', 'course_id', 'session_year_id', 'created_at')
    list_filter = ('course_id', 'session_year_id', 'gender')
    search_fields = ('admin__username', 'admin__email', 'admin__first_name', 'admin__last_name')
    ordering = ('admin__username',)

    def get_student_name(self, obj):
        return f"{obj.admin.first_name} {obj.admin.last_name}"
    get_student_name.short_description = 'Student Name'

    def get_email(self, obj):
        return obj.admin.email
    get_email.short_description = 'Email'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "admin":
            # Only show users with student type
            kwargs["queryset"] = CustomUser.objects.filter(user_type='3')
        elif db_field.name == "course_id":
            # Only show available courses
            kwargs["queryset"] = Courses.objects.all()
        elif db_field.name == "session_year_id":
            # Only show available session years
            kwargs["queryset"] = SessionYearModel.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Staff Admin
class StaffAdmin(admin.ModelAdmin):
    list_display = ('get_staff_name', 'get_email', 'created_at')
    search_fields = ('admin__username', 'admin__email', 'admin__first_name', 'admin__last_name')
    ordering = ('admin__username',)

    def get_staff_name(self, obj):
        return f"{obj.admin.first_name} {obj.admin.last_name}"
    get_staff_name.short_description = 'Staff Name'

    def get_email(self, obj):
        return obj.admin.email
    get_email.short_description = 'Email'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "admin":
            # Only show users with staff type
            kwargs["queryset"] = CustomUser.objects.filter(user_type='2')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Attendance Admin with validation
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('subject_id', 'attendance_date', 'session_year_id', 'created_at')
    list_filter = ('attendance_date', 'subject_id', 'session_year_id')
    search_fields = ('subject_id__subject_name',)
    ordering = ('-attendance_date',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subject_id":
            kwargs["queryset"] = Subjects.objects.select_related('course_id', 'staff_id')
        elif db_field.name == "session_year_id":
            kwargs["queryset"] = SessionYearModel.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Attendance Report Admin
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_subject', 'get_date', 'status', 'location_verified')
    list_filter = ('status', 'location_verified', 'attendance_id__attendance_date')
    search_fields = ('student_id__admin__username', 'attendance_id__subject_id__subject_name')
    ordering = ('-attendance_id__attendance_date',)

    def get_student_name(self, obj):
        return f"{obj.student_id.admin.first_name} {obj.student_id.admin.last_name}"
    get_student_name.short_description = 'Student'

    def get_subject(self, obj):
        return obj.attendance_id.subject_id.subject_name
    get_subject.short_description = 'Subject'

    def get_date(self, obj):
        return obj.attendance_id.attendance_date
    get_date.short_description = 'Date'

# Register models with improved admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SessionYearModel, SessionYearAdmin)
admin.site.register(Courses, CourseAdmin)
admin.site.register(Subjects, SubjectAdmin)
admin.site.register(Students, StudentAdmin)
admin.site.register(Staffs, StaffAdmin)
admin.site.register(AdminHOD)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(AttendanceReport, AttendanceReportAdmin)
admin.site.register(AttendanceQRCode)
admin.site.register(StudentResult)

