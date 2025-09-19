#!/usr/bin/env python3
"""
Test script for SehatMind system
This script tests the basic functionality of the application
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def test_connection():
    """Test if the server is running"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def test_registration():
    """Test user registration"""
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "teacher"
        }
        response = requests.post(f"{BASE_URL}/api/register", json=data)
        if response.status_code == 201:
            print("✅ User registration successful")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    try:
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/login", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ User login successful")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_add_student(token):
    """Test adding a student"""
    try:
        headers = {"Content-Type": "application/json"}
        data = {
            "student_id": "TEST001",
            "name": "Test Student",
            "email": "teststudent@example.com",
            "course": "Computer Science",
            "semester": 3,
            "attendance_percentage": 75.0,
            "cgpa": 6.5,
            "assignments_submitted": 7,
            "assignments_total": 10,
            "exam_attempts": 1,
            "family_income": 50000,
            "mental_health_score": 6.0
        }
        response = requests.post(f"{BASE_URL}/api/students", json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Student added successfully")
            return True
        else:
            print(f"❌ Adding student failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Add student error: {e}")
        return False

def test_get_students(token):
    """Test getting students list"""
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Retrieved {len(students)} students")
            return True
        else:
            print(f"❌ Getting students failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get students error: {e}")
        return False

def test_dashboard_stats(token):
    """Test dashboard statistics"""
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Dashboard stats retrieved successfully")
            print(f"   Total students: {stats.get('total_students', 0)}")
            print(f"   High risk: {stats.get('high_risk', 0)}")
            print(f"   Medium risk: {stats.get('medium_risk', 0)}")
            print(f"   Low risk: {stats.get('low_risk', 0)}")
            return True
        else:
            print(f"❌ Getting dashboard stats failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard stats error: {e}")
        return False

def test_risk_prediction(token):
    """Test risk prediction"""
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BASE_URL}/api/predict-risk", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Risk prediction completed successfully")
            return True
        else:
            print(f"❌ Risk prediction failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Risk prediction error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing SehatMind System")
    print("=" * 40)
    
    # Test connection
    if not test_connection():
        print("\n❌ Cannot proceed with tests. Please start the server first.")
        print("Run: python app.py")
        sys.exit(1)
    
    print("\n📝 Testing API endpoints...")
    
    # Test registration
    test_registration()
    
    # Test login
    login_success = test_login()
    if not login_success:
        print("\n❌ Cannot proceed without successful login")
        sys.exit(1)
    
    # Test student management
    test_add_student(True)
    test_get_students(True)
    
    # Test dashboard
    test_dashboard_stats(True)
    
    # Test risk prediction
    test_risk_prediction(True)
    
    print("\n" + "=" * 40)
    print("🎉 All tests completed!")
    print("🌐 Open http://localhost:5000 in your browser to use the system")

if __name__ == "__main__":
    main()
