from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import logging
import os
from dotenv import load_dotenv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sehatmind',
    'user': 'postgres',
    'password': 'Akash9872'
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_database():
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(120) NOT NULL,
                role VARCHAR(20) DEFAULT 'teacher',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create students table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL,
                phone VARCHAR(20),
                course VARCHAR(100),
                semester INTEGER,
                attendance_percentage FLOAT,
                cgpa FLOAT,
                assignments_submitted INTEGER,
                assignments_total INTEGER,
                exam_attempts INTEGER,
                family_income FLOAT,
                study_hours FLOAT,
                mental_health_score FLOAT,
                dropout_risk_score FLOAT,
                risk_percentage FLOAT,
                risk_level VARCHAR(20),
                counselor_notes TEXT,
                intervention_plan TEXT,
                owner_user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                self_edit_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        
        # Add study_hours column if it doesn't exist (migration)
        try:
            cur.execute("ALTER TABLE students ADD COLUMN study_hours FLOAT DEFAULT 0.0")
            conn.commit()
            logger.info("Added study_hours column to students table")
        except Exception as e:
            # Column might already exist, rollback and continue
            conn.rollback()
            logger.info(f"Study_hours column already exists or error adding it: {e}")
        
        # Add risk_percentage column if it doesn't exist (migration)
        try:
            cur.execute("ALTER TABLE students ADD COLUMN risk_percentage FLOAT DEFAULT 0.0")
            conn.commit()
            logger.info("Added risk_percentage column to students table")
        except Exception as e:
            # Column might already exist, rollback and continue
            conn.rollback()
            logger.info(f"Risk_percentage column already exists or error adding it: {e}")
        
        # Add risk_level column if it doesn't exist (migration)
        try:
            cur.execute("ALTER TABLE students ADD COLUMN risk_level VARCHAR(20) DEFAULT 'unknown'")
            conn.commit()
            logger.info("Added risk_level column to students table")
        except Exception as e:
            # Column might already exist, rollback and continue
            conn.rollback()
            logger.info(f"Risk_level column already exists or error adding it: {e}")
        
        # Add teacher_id column if it doesn't exist (migration)
        try:
            cur.execute("ALTER TABLE students ADD COLUMN teacher_id INTEGER REFERENCES users(id)")
            conn.commit()
            logger.info("Added teacher_id column to students table")
        except Exception as e:
            # Column might already exist, rollback and continue
            conn.rollback()
            logger.info(f"Teacher_id column already exists or error adding it: {e}")
        
        # Add teacher_name column if it doesn't exist (migration)
        try:
            cur.execute("ALTER TABLE students ADD COLUMN teacher_name VARCHAR(100)")
            conn.commit()
            logger.info("Added teacher_name column to students table")
        except Exception as e:
            # Column might already exist, rollback and continue
            conn.rollback()
            logger.info(f"Teacher_name column already exists or error adding it: {e}")
        
        # Insert admin user
        cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        admin_exists = cur.fetchone()[0]
        
        if admin_exists == 0:
            cur.execute("""
                INSERT INTO users (username, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('admin', 'admin@sehatmind.local', 'admin123', 'admin'))
        
        # Insert sample teacher
        cur.execute("SELECT COUNT(*) FROM users WHERE username = 'teacher1'")
        teacher_exists = cur.fetchone()[0]
        
        if teacher_exists == 0:
            cur.execute("""
                INSERT INTO users (username, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('teacher1', 'teacher1@example.com', 'password', 'teacher'))
        
        # Insert sample students
        cur.execute("SELECT COUNT(*) FROM students")
        student_count = cur.fetchone()[0]
        
        if student_count == 0:
            sample_students = [
                ('STU001', 'John Doe', 'john@example.com', 'Computer Science', 3, 85.0, 7.5, 8, 10, 1, 60000, 6.0),
                ('STU002', 'Jane Smith', 'jane@example.com', 'Engineering', 2, 45.0, 4.2, 3, 10, 3, 35000, 3.0),
                ('STU003', 'Mike Johnson', 'mike@example.com', 'Business', 4, 92.0, 8.8, 12, 12, 0, 80000, 8.0)
            ]
            
            for student in sample_students:
                cur.execute("""
                    INSERT INTO students (student_id, name, email, course, semester,
                                        attendance_percentage, cgpa, assignments_submitted,
                                        assignments_total, exam_attempts, family_income,
                                        mental_health_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, student)
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info("Database tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

# Initialize database
init_database()

# Machine Learning Model
class DropoutPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def train_model(self, data):
        try:
            df = pd.DataFrame(data)
            X = df[['attendance_percentage', 'cgpa', 'assignments_submitted', 
                   'assignments_total', 'exam_attempts', 'family_income', 
                   'mental_health_score', 'semester']].fillna(0)
            
            # Create synthetic target variable based on rules
            y = ((X['attendance_percentage'] < 60) | 
                 (X['cgpa'] < 5.0) | 
                 (X['mental_health_score'] < 4.0)).astype(int)
            
            self.model.fit(X, y)
            self.is_trained = True
            return True
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return False
    
    def predict_dropout_risk(self, data):
        if not self.is_trained:
            self.train_model(data)
        
        try:
            df = pd.DataFrame(data)
            X = df[['attendance_percentage', 'cgpa', 'assignments_submitted', 
                   'assignments_total', 'exam_attempts', 'family_income', 
                   'mental_health_score', 'semester']].fillna(0)
            
            probabilities = self.model.predict_proba(X)[:, 1]
            return probabilities
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return [0.5] * len(data)

predictor = DropoutPredictor()

def calculate_risk_percentage(cgpa, attendance_percentage, assignments_submitted, assignments_total):
    """Calculate risk percentage based on CGPA, attendance, and assignment completion only"""
    
    # Calculate assignment completion percentage
    assignment_percentage = 0
    if assignments_total > 0:
        assignment_percentage = (assignments_submitted / assignments_total) * 100
    
    # Define risk boundaries based on CGPA, attendance, and assignment completion
    # High Risk: CGPA < 3.0 AND attendance 0-30% AND assignment 0-30%
    # Medium Risk: CGPA 3.0-5.0 AND attendance 30-50% AND assignment 30-50%
    # Low Risk: CGPA 5.0-8.0 AND attendance 50-80% AND assignment 50-80%
    # Safe: CGPA 8.0-10.0 AND attendance 80-100% AND assignment 80-100%
    
    # Check for High Risk conditions
    if cgpa < 3.0 and attendance_percentage <= 30 and assignment_percentage <= 30:
        return 85  # High risk percentage
    
    # Check for Medium Risk conditions
    elif 3.0 <= cgpa < 5.0 and 30 < attendance_percentage <= 50 and 30 < assignment_percentage <= 50:
        return 65  # Medium risk percentage
    
    # Check for Low Risk conditions
    elif 5.0 <= cgpa < 8.0 and 50 < attendance_percentage <= 80 and 50 < assignment_percentage <= 80:
        return 35  # Low risk percentage
    
    # Check for Safe conditions
    elif 8.0 <= cgpa <= 10.0 and 80 <= attendance_percentage <= 100 and 80 <= assignment_percentage <= 100:
        # Perfect scores should get the lowest risk
        if cgpa == 10.0 and attendance_percentage == 100 and assignment_percentage == 100:
            return 5  # Perfect scores get minimal risk
        else:
            return 15  # Safe risk percentage
    
    # For students who don't fit exact boundaries, calculate based on proximity
    else:
        # Calculate weighted average based on the three factors
        # Each factor contributes equally to the final risk assessment
        
        # Normalize CGPA to 0-100 scale (0 = worst, 100 = best)
        cgpa_score = min(100, (cgpa / 10.0) * 100)
        
        # Attendance and assignment scores are already percentages
        attendance_score = attendance_percentage
        assignment_score = assignment_percentage
        
        # Calculate average of the three scores
        average_score = (cgpa_score + attendance_score + assignment_score) / 3
        
        # Convert to risk percentage (higher score = lower risk)
        risk_percentage = 100 - average_score
        
        # Apply some adjustments for better distribution
        if risk_percentage < 20:
            risk_percentage = 15  # Minimum risk for high performers
        elif risk_percentage > 85:
            risk_percentage = 85  # Maximum risk cap
        
        return max(5, min(85, risk_percentage))  # Clamp between 5-85

def get_risk_level_from_percentage(percentage):
    """Convert risk percentage to risk level based on new boundaries"""
    if percentage >= 60:
        return 'high'
    elif percentage >= 40:
        return 'medium'
    elif percentage >= 20:
        return 'low'
    else:
        return 'safe'

# Authentication decorators
def require_login():
    if 'user' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return None

def require_roles(*roles):
    def decorator():
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session['user']['role'] not in roles:
            return jsonify({'error': 'Insufficient permissions'}), 403
        return None
    return decorator

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Only allow teacher and student roles for registration
        role = data.get('role', 'student')
        if role not in ['teacher', 'student']:
            return jsonify({'error': 'Only teacher and student roles are allowed for registration'}), 400
        
        # Prevent creating admin user via registration
        if data.get('username') == 'admin' or data.get('role') == 'admin':
            return jsonify({'error': 'Cannot create admin via registration'}), 403
    
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE username = %s", (data['username'],))
        if cur.fetchone():
            return jsonify({'error': 'Username already exists'}), 400
        
        cur.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
        if cur.fetchone():
            return jsonify({'error': 'Email already exists'}), 400
    
        # Create new user
        cur.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data['username'], data['email'], data['password'], data.get('role', 'teacher')))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    logger.info(f"Login attempt for username: {data.get('username')}")
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Check for admin login
        if data['username'] == 'admin' and data['password'] == 'admin123':
            logger.info("Admin login successful")
            session['user'] = {
                'id': 1,
                'username': 'admin',
                'email': 'admin@sehatmind.local',
                'role': 'admin'
            }
            return jsonify({'message': 'Login successful', 'user': session['user']})
        
        # Check regular users
        cur.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
        user = cur.fetchone()
        
        if user and user[3] == data['password']:  # user[3] is password
            logger.info(f"User login successful for: {user[1]}")
            session['user'] = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[4]
            }
            return jsonify({'message': 'Login successful', 'user': session['user']})
        
        logger.warning(f"Login failed for username: {data.get('username')}")
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    auth_error = require_login()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        current_user_id = session.get('user', {}).get('id')
        current_role = session.get('user', {}).get('role')
        
        if current_role == 'teacher':
            cur.execute("SELECT COUNT(*) FROM students WHERE owner_user_id = %s", (current_user_id,))
            total_students = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM students WHERE owner_user_id = %s AND risk_level = 'high'", (current_user_id,))
            high_risk = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM students WHERE owner_user_id = %s AND risk_level = 'medium'", (current_user_id,))
            medium_risk = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM students WHERE owner_user_id = %s AND risk_level = 'low'", (current_user_id,))
            low_risk = cur.fetchone()[0]
        else:
            cur.execute("SELECT COUNT(*) FROM students")
            total_students = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM students WHERE risk_level = 'high'")
            high_risk = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM students WHERE risk_level = 'medium'")
            medium_risk = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM students WHERE risk_level = 'low'")
            low_risk = cur.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_students': total_students,
            'high_risk_students': high_risk,
            'medium_risk_students': medium_risk,
            'low_risk_students': low_risk
        })
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    auth_error = require_login()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        current_user_id = session.get('user', {}).get('id')
        current_role = session.get('user', {}).get('role')
        current_email = session.get('user', {}).get('email')
        
        # Check if teacher_id is provided in query parameters (for admin viewing specific teacher's students)
        teacher_id = request.args.get('teacher_id')
        
        if teacher_id and current_role == 'admin':
            # Admin viewing specific teacher's students
            cur.execute("SELECT * FROM students WHERE owner_user_id = %s", (teacher_id,))
        elif current_role == 'teacher':
            cur.execute("SELECT * FROM students WHERE owner_user_id = %s", (current_user_id,))
        elif current_role == 'student':
            cur.execute("SELECT * FROM students WHERE email = %s", (current_email,))
        else:  # admin viewing all students
            cur.execute("SELECT * FROM students")
        
        students = cur.fetchall()
        
        students_list = []
        for student in students:
            # Calculate risk percentage and level from student data
            risk_percentage = calculate_risk_percentage(
                student[8],  # cgpa
                student[7],  # attendance_percentage
                student[9],  # assignments_submitted
                student[10]  # assignments_total
            )
            
            risk_level = get_risk_level_from_percentage(risk_percentage)
            
            students_list.append({
                'id': student[0],
                'student_id': student[1],
                'name': student[2],
                'email': student[3],
                'phone': student[4],
                'course': student[5],
                'semester': student[6],
                'attendance_percentage': student[7],
                'cgpa': student[8],
                'assignments_submitted': student[9],
                'assignments_total': student[10],
                'exam_attempts': student[11],
                'family_income': student[12],
                'study_hours': student[13],
                'mental_health_score': student[14],
                'dropout_risk_score': student[15],
                'risk_percentage': risk_percentage,
                'risk_level': risk_level,
                'counselor_notes': student[18],
                'intervention_plan': student[19],
                'teacher_id': student[22] if len(student) > 22 else None,
                'teacher_name': student[23] if len(student) > 23 else None,
                'created_at': student[21].isoformat() if student[21] and hasattr(student[21], 'isoformat') else str(student[21]) if student[21] else None
            })
        
        conn.close()
        return jsonify(students_list)
        
    except Exception as e:
        logger.error(f"Get students error: {e}")
        return jsonify({'error': 'Failed to fetch students'}), 500

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    auth_error = require_login()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        current_user_id = session.get('user', {}).get('id')
        current_role = session.get('user', {}).get('role')
        current_email = session.get('user', {}).get('email')
        
        # Check if user can access this student
        if current_role == 'teacher':
            cur.execute("SELECT * FROM students WHERE id = %s AND owner_user_id = %s", (student_id, current_user_id))
        elif current_role == 'student':
            cur.execute("SELECT * FROM students WHERE id = %s AND email = %s", (student_id, current_email))
        else:  # admin
            cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        
        student = cur.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Calculate risk percentage and level from student data
        risk_percentage = calculate_risk_percentage(
            student[8],  # cgpa
            student[7],  # attendance_percentage
            student[9],  # assignments_submitted
            student[10]  # assignments_total
        )
        
        risk_level = get_risk_level_from_percentage(risk_percentage)
        
        student_data = {
            'id': student[0],
            'student_id': student[1],
            'name': student[2],
            'email': student[3],
            'phone': student[4],
            'course': student[5],
            'semester': student[6],
            'attendance_percentage': student[7],
            'cgpa': student[8],
            'assignments_submitted': student[9],
            'assignments_total': student[10],
            'exam_attempts': student[11],
            'family_income': student[12],
            'study_hours': student[13],
            'mental_health_score': student[14],
            'dropout_risk_score': student[15],
            'risk_percentage': risk_percentage,
            'risk_level': risk_level,
            'counselor_notes': student[18],
            'intervention_plan': student[19],
            'owner_user_id': student[20],
            'teacher_id': student[22] if len(student) > 22 else None,
            'teacher_name': student[23] if len(student) > 23 else None
        }
        
        conn.close()
        return jsonify(student_data)
        
    except Exception as e:
        logger.error(f"Get student error: {e}")
        return jsonify({'error': 'Failed to fetch student'}), 500

@app.route('/api/students', methods=['POST'])
def add_student():
    role_check = require_roles('admin', 'teacher', 'student')
    auth_error = role_check()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        current_user_id = session.get('user', {}).get('id')
        current_role = session.get('user', {}).get('role')
        current_username = session.get('user', {}).get('username')
        current_email = session.get('user', {}).get('email')
        
        # Convert form data to proper types with error handling
        try:
            semester = int(data.get('semester', 1))
            attendance_percentage = float(data.get('attendance_percentage', 0.0))
            cgpa = float(data.get('cgpa', 0.0))
            assignments_submitted = int(data.get('assignments_submitted', 0))
            assignments_total = int(data.get('assignments_total', 0))
        except (ValueError, TypeError) as e:
            logger.error(f"Data conversion error: {e}")
            return jsonify({'error': 'Invalid data format. Please check your input values.'}), 400
        
        # For students creating their own profile, use their account info
        if current_role == 'student':
            student_email = current_email
            student_name = current_username
        else:
            student_email = data.get('email')
            student_name = data.get('name')
        
        # Calculate dropout risk using converted values
        student_data = {
            'attendance_percentage': attendance_percentage,
            'cgpa': cgpa,
            'assignments_submitted': assignments_submitted,
            'assignments_total': assignments_total,
            'semester': semester
        }
        
        # Calculate risk using new percentage-based method
        risk_percentage = calculate_risk_percentage(cgpa, attendance_percentage, assignments_submitted, assignments_total)
        risk_score = risk_percentage / 100  # Convert to 0-1 scale for compatibility
        risk_level = get_risk_level_from_percentage(risk_percentage)
        
        # Get teacher information if provided
        teacher_id = data.get('teacher_id')
        teacher_name = None
        if teacher_id:
            cur.execute("SELECT username FROM users WHERE id = %s AND role = 'teacher'", (teacher_id,))
            teacher = cur.fetchone()
            if teacher:
                teacher_name = teacher[0]
        
        cur.execute("""
            INSERT INTO students (student_id, name, email, phone, course, semester,
                                attendance_percentage, cgpa, assignments_submitted,
                                assignments_total, dropout_risk_score, risk_percentage, risk_level,
                                owner_user_id, teacher_id, teacher_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data.get('student_id'), student_name, student_email, data.get('phone'),
              data.get('course'), semester, attendance_percentage, cgpa,
              assignments_submitted, assignments_total, risk_score, risk_percentage, risk_level,
              current_user_id, teacher_id, teacher_name))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Student added successfully'}), 201
        
    except Exception as e:
        logger.error(f"Add student error: {e}")
        return jsonify({'error': 'Failed to add student'}), 500

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    role_check = require_roles('admin', 'teacher', 'student')
    auth_error = role_check()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        current_user_id = session.get('user', {}).get('id')
        current_role = session.get('user', {}).get('role')
        
        # Check if student exists and user has permission to edit
        cur.execute("SELECT owner_user_id FROM students WHERE id = %s", (student_id,))
        student = cur.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Check permissions
        if current_role == 'student' and student[0] != current_user_id:
            return jsonify({'error': 'You can only edit your own profile'}), 403
        elif current_role == 'teacher' and student[0] != current_user_id:
            return jsonify({'error': 'You can only edit your own students'}), 403
        
        # Convert form data to proper types
        try:
            semester = int(data.get('semester', 1))
            attendance_percentage = float(data.get('attendance_percentage', 0.0))
            cgpa = float(data.get('cgpa', 0.0))
            assignments_submitted = int(data.get('assignments_submitted', 0))
            assignments_total = int(data.get('assignments_total', 0))
        except (ValueError, TypeError) as e:
            logger.error(f"Data conversion error: {e}")
            return jsonify({'error': 'Invalid data format. Please check your input values.'}), 400
        
        # Calculate risk using new percentage-based method
        risk_percentage = calculate_risk_percentage(cgpa, attendance_percentage, assignments_submitted, assignments_total)
        risk_score = risk_percentage / 100  # Convert to 0-1 scale for compatibility
        risk_level = get_risk_level_from_percentage(risk_percentage)
        
        # Get teacher information if provided
        teacher_id = data.get('teacher_id')
        teacher_name = None
        if teacher_id:
            cur.execute("SELECT username FROM users WHERE id = %s AND role = 'teacher'", (teacher_id,))
            teacher = cur.fetchone()
            if teacher:
                teacher_name = teacher[0]
        
        # Update student
        cur.execute("""
            UPDATE students SET 
                name = %s, email = %s, phone = %s, course = %s, semester = %s,
                attendance_percentage = %s, cgpa = %s, assignments_submitted = %s,
                assignments_total = %s, dropout_risk_score = %s, risk_percentage = %s, risk_level = %s,
                teacher_id = %s, teacher_name = %s, last_updated = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (data.get('name'), data.get('email'), data.get('phone'), 
              data.get('course'), semester, attendance_percentage, cgpa,
              assignments_submitted, assignments_total, risk_score, risk_percentage, risk_level,
              teacher_id, teacher_name, student_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Student updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update student error: {e}")
        return jsonify({'error': 'Failed to update student'}), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    role_check = require_roles('admin', 'teacher')
    auth_error = role_check()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        current_user_id = session.get('user', {}).get('id')
        current_role = session.get('user', {}).get('role')
        
        # Check if student exists and user has permission to delete
        cur.execute("SELECT owner_user_id FROM students WHERE id = %s", (student_id,))
        student = cur.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Check permissions
        if current_role == 'teacher' and student[0] != current_user_id:
            return jsonify({'error': 'You can only delete your own students'}), 403
        
        # Delete student
        cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Student deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete student error: {e}")
        return jsonify({'error': 'Failed to delete student'}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    role_check = require_roles('admin')
    auth_error = role_check()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC")
        users = cur.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3],
                'created_at': user[4].isoformat() if user[4] else None
            })
        
        conn.close()
        return jsonify(users_list)
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    role_check = require_roles('admin')
    auth_error = role_check()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Update user
        cur.execute("""
            UPDATE users 
            SET username = %s, email = %s, role = %s
            WHERE id = %s
        """, (data['username'], data['email'], data['role'], user_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'User updated successfully'})
        
    except Exception as e:
        logger.error(f"Update user error: {e}")
        return jsonify({'error': 'Failed to update user'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    role_check = require_roles('admin')
    auth_error = role_check()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'User deleted successfully'})
        
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    """Get all available teachers for student assignment"""
    auth_error = require_login()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email FROM users WHERE role = 'teacher' ORDER BY username")
        teachers = cur.fetchall()
        
        teachers_list = []
        for teacher in teachers:
            teachers_list.append({
                'id': teacher[0],
                'username': teacher[1],
                'email': teacher[2]
            })
        
        conn.close()
        return jsonify(teachers_list)
        
    except Exception as e:
        logger.error(f"Get teachers error: {e}")
        return jsonify({'error': 'Failed to fetch teachers'}), 500

@app.route('/api/admin/teacher-stats', methods=['GET'])
def get_teacher_stats():
    role_check = require_roles('admin')
    auth_error = role_check()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Get teacher statistics with student counts
        cur.execute("""
            SELECT 
                u.id,
                u.username,
                u.email,
                COUNT(s.id) as student_count,
                COUNT(CASE WHEN s.risk_level = 'high' THEN 1 END) as high_risk_count,
                COUNT(CASE WHEN s.risk_level = 'medium' THEN 1 END) as medium_risk_count,
                COUNT(CASE WHEN s.risk_level = 'low' THEN 1 END) as low_risk_count
            FROM users u
            LEFT JOIN students s ON u.id = s.owner_user_id
            WHERE u.role = 'teacher'
            GROUP BY u.id, u.username, u.email
            ORDER BY student_count DESC
        """)
        
        teachers = cur.fetchall()
        
        teachers_list = []
        for teacher in teachers:
            teachers_list.append({
                'id': teacher[0],
                'username': teacher[1],
                'email': teacher[2],
                'student_count': teacher[3],
                'high_risk_count': teacher[4],
                'medium_risk_count': teacher[5],
                'low_risk_count': teacher[6]
            })
        
        conn.close()
        return jsonify(teachers_list)
        
    except Exception as e:
        logger.error(f"Get teacher stats error: {e}")
        return jsonify({'error': 'Failed to fetch teacher stats'}), 500

@app.route('/api/predict-risk', methods=['POST'])
def predict_risk():
    auth_error = require_login()
    if auth_error:
        return auth_error
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        current_user_id = session.get('user', {}).get('id')
        current_role = session.get('user', {}).get('role')
        
        if current_role == 'teacher':
            cur.execute("SELECT * FROM students WHERE owner_user_id = %s", (current_user_id,))
        else:
            cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        
        if not students:
            return jsonify({'error': 'No students found'}), 400
        
        # Convert to list of dicts
        for student in students:
            # Calculate risk using new percentage-based method
            risk_percentage = calculate_risk_percentage(
                student[8],  # cgpa
                student[7],  # attendance_percentage
                student[9],  # assignments_submitted
                student[10]  # assignments_total
            )
            risk_score = risk_percentage / 100  # Convert to 0-1 scale for compatibility
            risk_level = get_risk_level_from_percentage(risk_percentage)
            
            cur.execute("""
                UPDATE students SET dropout_risk_score = %s, risk_level = %s, last_updated = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (risk_score, risk_level, student[0]))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Risk prediction completed', 'updated_count': len(students)})
        
    except Exception as e:
        logger.error(f"Predict risk error: {e}")
        return jsonify({'error': 'Failed to predict risk'}), 500

def recalculate_all_student_risks():
    """Recalculate risk percentages for all students with the new logic"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all students
        cur.execute("SELECT id, cgpa, attendance_percentage, assignments_submitted, assignments_total FROM students")
        students = cur.fetchall()
        
        updated_count = 0
        for student in students:
            student_id, cgpa, attendance_percentage, assignments_submitted, assignments_total = student
            
            # Calculate new risk percentage
            new_risk_percentage = calculate_risk_percentage(cgpa, attendance_percentage, assignments_submitted, assignments_total)
            new_risk_level = get_risk_level_from_percentage(new_risk_percentage)
            
            # Update the student record
            cur.execute("""
                UPDATE students 
                SET risk_percentage = %s, risk_level = %s 
                WHERE id = %s
            """, (new_risk_percentage, new_risk_level, student_id))
            
            updated_count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"Recalculated risk for {updated_count} students")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error recalculating student risks: {e}")
        return 0

if __name__ == '__main__':
    # Recalculate all student risks on startup
    recalculate_all_student_risks()
    app.run(debug=True, host='0.0.0.0', port=5000)