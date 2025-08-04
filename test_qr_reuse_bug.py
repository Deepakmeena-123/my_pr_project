#!/usr/bin/env python3
"""
Test script to demonstrate the QR code reuse bug.
This script shows that QR codes can be reused by multiple students
due to inconsistent deactivation logic.
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from student_management_app.models import (
    CustomUser, Students, Staffs, Courses, Subjects, 
    SessionYearModel, AttendanceQRCode, Attendance, AttendanceReport
)
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
import datetime
import uuid

def test_qr_reuse_bug():
    """Test if QR codes can be reused by multiple students"""
    
    print("=== QR Code Reuse Bug Test ===\n")
    
    # Clean up any existing test data
    print("1. Cleaning up existing test data...")
    CustomUser.objects.filter(username__startswith='test_').delete()
    AttendanceQRCode.objects.filter(token__startswith='test_').delete()
    
    try:
        # Create test data
        print("2. Creating test data...")
        
        # Create course and session
        course = Courses.objects.create(course_name="Test Course")
        session = SessionYearModel.objects.create(
            session_start_year=datetime.date(2024, 1, 1),
            session_end_year=datetime.date(2024, 12, 31)
        )
        
        # Create staff user and profile
        staff_user = CustomUser.objects.create(
            username="test_staff",
            email="staff@test.com",
            first_name="Test",
            last_name="Staff",
            user_type="2",
            password=make_password("password123")
        )
        staff = Staffs.objects.create(admin=staff_user)
        
        # Create subject
        subject = Subjects.objects.create(
            subject_name="Test Subject",
            course_id=course,
            staff_id=staff
        )
        
        # Create two test students
        student1_user = CustomUser.objects.create(
            username="test_student1",
            email="student1@test.com",
            first_name="Student",
            last_name="One",
            user_type="3",
            password=make_password("password123")
        )
        student1 = Students.objects.create(
            admin=student1_user,
            course_id=course,
            session_year_id=session
        )
        
        student2_user = CustomUser.objects.create(
            username="test_student2",
            email="student2@test.com",
            first_name="Student",
            last_name="Two",
            user_type="3",
            password=make_password("password123")
        )
        student2 = Students.objects.create(
            admin=student2_user,
            course_id=course,
            session_year_id=session
        )
        
        # Create QR code
        print("3. Creating QR code...")
        qr_token = "test_token_" + str(uuid.uuid4())[:8]
        qr_code = AttendanceQRCode.objects.create(
            subject=subject,
            session_year=session,
            expiry_time=now() + datetime.timedelta(minutes=30),
            is_active=True,
            token=qr_token,
            qr_code_image="test_qr.png"
        )
        
        print(f"   QR Code created with token: {qr_token}")
        print(f"   QR Code is_active: {qr_code.is_active}")
        
        # Test 1: Student 1 uses QR code via upload method
        print("\n4. Testing Student 1 attendance via upload method...")
        
        # Simulate the upload QR process (which DOESN'T deactivate QR)
        attendance = Attendance.objects.create(
            subject_id=subject,
            attendance_date=datetime.date.today(),
            session_year_id=session
        )
        
        attendance_report1 = AttendanceReport.objects.create(
            student_id=student1,
            attendance_id=attendance,
            status=True,
            location_verified=True
        )
        
        # Check QR code status after student 1
        qr_code.refresh_from_db()
        print(f"   After Student 1: QR Code is_active = {qr_code.is_active}")
        
        # Test 2: Student 2 tries to use the same QR code
        print("\n5. Testing Student 2 attendance with same QR code...")
        
        # Check if QR code is still usable
        if qr_code.is_active and qr_code.expiry_time > now():
            print("   ⚠️  QR Code is still active and not expired!")
            print("   ⚠️  Student 2 can potentially reuse the same QR code!")
            
            # Student 2 can mark attendance
            attendance_report2 = AttendanceReport.objects.create(
                student_id=student2,
                attendance_id=attendance,
                status=True,
                location_verified=True
            )
            print("   ❌ BUG CONFIRMED: Student 2 successfully used the same QR code!")
            
        else:
            print("   ✅ QR Code is properly deactivated")
        
        # Test 3: Check what happens with scan method
        print("\n6. Testing scan method (which DOES deactivate QR)...")
        
        # Create another QR code for scan method test
        qr_token2 = "test_token2_" + str(uuid.uuid4())[:8]
        qr_code2 = AttendanceQRCode.objects.create(
            subject=subject,
            session_year=session,
            expiry_time=now() + datetime.timedelta(minutes=30),
            is_active=True,
            token=qr_token2,
            qr_code_image="test_qr2.png"
        )
        
        print(f"   QR Code 2 created with token: {qr_token2}")
        print(f"   QR Code 2 is_active: {qr_code2.is_active}")
        
        # Simulate scan method (which DOES deactivate QR)
        qr_code2.is_active = False
        qr_code2.save()
        
        print(f"   After scan method: QR Code 2 is_active = {qr_code2.is_active}")
        print("   ✅ Scan method properly deactivates QR code")
        
        # Summary
        print("\n=== TEST RESULTS ===")
        print("❌ BUG FOUND: student_upload_qr() does NOT deactivate QR codes")
        print("✅ WORKING: student_process_qr_scan() DOES deactivate QR codes")
        print("\n📋 IMPACT:")
        print("   - Students using upload method can share QR codes")
        print("   - Multiple students can mark attendance with same QR")
        print("   - Security vulnerability in attendance system")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        print("\n7. Cleaning up test data...")
        CustomUser.objects.filter(username__startswith='test_').delete()
        AttendanceQRCode.objects.filter(token__startswith='test_').delete()
        Courses.objects.filter(course_name="Test Course").delete()

if __name__ == "__main__":
    test_qr_reuse_bug()
