# SehatMind - AI-based Dropout Prediction and Counseling System

## 🎯 Project Overview

SehatMind is an intelligent system designed to predict student dropout risk and provide early intervention counseling. Built for the Smart India Hackathon 2025, this system helps educational institutions identify at-risk students and take proactive measures to improve retention rates.

## 🚀 Features

### Core Functionality
- **AI-Powered Risk Prediction**: Machine learning algorithms analyze student data to predict dropout probability
- **Real-time Dashboard**: Interactive dashboard with comprehensive student analytics
- **Risk Assessment**: Multi-factor analysis including academic performance, attendance, mental health, and socio-economic factors
- **Early Warning System**: Automated alerts for high-risk students
- **Data Visualization**: Charts and graphs for better insights
- **Bulk Data Import**: CSV import functionality for easy data management

### User Management
- **Role-based Access**: Different access levels for teachers, counselors, and administrators
- **Secure Authentication**: JWT-based authentication system
- **User Registration**: Easy account creation and management

### Student Management
- **Comprehensive Profiles**: Detailed student information tracking
- **Academic Monitoring**: Attendance, CGPA, assignment tracking
- **Mental Health Assessment**: Mental health scoring system
- **Intervention Planning**: Counselor notes and intervention strategies

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL/SQLite**: Database management
- **scikit-learn**: Machine learning algorithms
- **pandas**: Data processing
- **Flask-JWT-Extended**: Authentication
- **Flask-Mail**: Email notifications

### Frontend
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Data visualization
- **Font Awesome**: Icons
- **Animate.css**: Animations

### AI/ML
- **Random Forest Classifier**: Primary prediction model
- **Rule-based Fallback**: Simple heuristic approach
- **Feature Engineering**: Multi-dimensional risk assessment

## 📋 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd SehatMind
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sehatmind

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this-in-production

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 5: Start PostgreSQL
Make sure PostgreSQL is running on your system with:
- Database: `sehatmind`
- Username: `postgres` 
- Password: `postgres`
- Port: `5432`

### Step 6: Run the Backend
```bash
python app.py
```

The application will be available at `http://localhost:5000`

Frontend is served by Flask at `/` using `frontend/index.html`.

## 📊 Usage Guide

### 1. Initial Setup
1. Open the application in your web browser
2. Register a new account (Admin/Teacher/Counselor role)
3. Login with your credentials

### 2. Adding Students
- **Manual Entry**: Use the "Add Student" button to enter individual student data
- **Bulk Import**: Use the "Import CSV" feature to upload student data from a spreadsheet

### 3. Risk Assessment
- Click "Predict Risk" to run AI analysis on all students
- View risk levels: High (Red), Medium (Yellow), Low (Green)
- Monitor the dashboard for real-time updates

### 4. Student Management
- Click on any student to view detailed information
- Add counselor notes and intervention plans
- Track academic progress and attendance

### 5. Data Visualization
- View risk distribution charts
- Monitor key performance indicators
- Track trends over time

## 📁 Project Structure

```
SehatMind/
├── backend/
│   ├── app.py                 # Flask API + server-rendered frontend
│   ├── run.py                 # Startup helper
│   ├── requirements.txt       # Backend dependencies
│   ├── .env.example           # Example env vars
│   ├── sample_students.csv    # Sample data
│   └── instance/
│       └── sehatmind.db       # SQLite database (auto-created)
├── frontend/
│   └── index.html             # Frontend (served by Flask)
└── README.md                  # Project documentation
```

## 🔧 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Student Management
- `GET /api/students` - Get all students
- `POST /api/students` - Add new student
- `PUT /api/students/<id>` - Update student
- `DELETE /api/students/<id>` - Delete student

### Risk Assessment
- `POST /api/predict-risk` - Run risk prediction
- `GET /api/dashboard/stats` - Get dashboard statistics

### Data Import
- `POST /api/import-students` - Import students from CSV

### Alerts
- `GET /api/alerts` - Get active alerts
- `POST /api/alerts` - Create new alert

## 🧠 AI Model Details

### Risk Factors
The system analyzes multiple factors to predict dropout risk:

1. **Academic Performance**
   - CGPA (Cumulative Grade Point Average)
   - Assignment submission rate
   - Exam attempts

2. **Attendance**
   - Overall attendance percentage
   - Recent attendance trends

3. **Mental Health**
   - Self-reported mental health score (1-10 scale)
   - Stress indicators

4. **Socio-economic Factors**
   - Family income
   - Financial stability indicators

5. **Academic Progress**
   - Semester progression
   - Course difficulty

### Prediction Algorithm
- **Primary**: Random Forest Classifier with feature scaling
- **Fallback**: Rule-based heuristic system
- **Risk Levels**: Low (0-40%), Medium (40-70%), High (70-100%)

## 📈 Sample Data Format

### CSV Import Format
```csv
student_id,name,email,phone,course,semester,attendance_percentage,cgpa,assignments_submitted,assignments_total,exam_attempts,family_income,mental_health_score
STU001,John Doe,john@example.com,9876543210,Computer Science,3,85.0,7.5,8,10,1,60000,6.0
```

### Required Fields
- `student_id`: Unique identifier
- `name`: Student's full name
- `email`: Contact email
- `course`: Academic program
- `semester`: Current semester

### Optional Fields
- `phone`: Contact number
- `attendance_percentage`: Attendance rate (0-100)
- `cgpa`: Academic performance (0-10)
- `assignments_submitted`: Completed assignments
- `assignments_total`: Total assigned work
- `exam_attempts`: Number of exam attempts
- `family_income`: Annual family income
- `mental_health_score`: Mental health rating (1-10)

## 🎨 UI/UX Features

### Design Principles
- **Modern & Clean**: Contemporary design with intuitive navigation
- **Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Accessible**: Color-coded risk indicators and clear typography
- **Interactive**: Smooth animations and hover effects

### Key Components
- **Dashboard**: Overview of all students and statistics
- **Student Cards**: Visual representation of student risk levels
- **Charts**: Interactive data visualization
- **Modals**: Detailed student information and forms
- **Alerts**: Real-time notifications for high-risk students

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: Different permissions for different user types
- **Data Validation**: Input sanitization and validation
- **CORS Protection**: Cross-origin resource sharing security

## 🚀 Deployment

### Local Development
From the `backend/` directory after activating the venv:
```bash
python app.py
```

### Production Deployment
1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables
3. Use a WSGI server like Gunicorn
4. Set up reverse proxy with Nginx
5. Enable HTTPS with SSL certificates

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is developed for the Smart India Hackathon 2025. All rights reserved.

## 👥 Team

**GoalGetters Team**
- AI-based Dropout Prediction and Counseling System
- Smart India Hackathon 2025
- Problem Statement ID: SIH25102

## 📞 Support

For technical support or questions:
- Email: support@sehatmind.com
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)

## 🔮 Future Enhancements

- **Advanced ML Models**: Deep learning and ensemble methods
- **Mobile App**: Native mobile application
- **Real-time Notifications**: Push notifications and SMS alerts
- **Integration APIs**: Connect with existing student management systems
- **Advanced Analytics**: Predictive analytics and trend analysis
- **Counselor Tools**: Advanced intervention planning tools

---

**Built with ❤️ for Smart India Hackathon 2025**

