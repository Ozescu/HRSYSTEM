# HR System

## Project Overview
A comprehensive Human Resource Management System built with Django and Django REST Framework. This system manages employee accounts, job postings, applications, assessments, and core HR operations.

## Tech Stack
- **Backend**: Django 6.0.3
- **API**: Django REST Framework 3.17.1
- **Database**: SQLite (Development)
- **Image Processing**: Pillow 12.1.1
- **Additional**: asgiref, sqlparse, tzdata

## Project Structure

### Core Applications

#### **Accounts** (`/accounts`)
- User authentication and authorization
- User registration and login functionality
- Custom user models and managers
- User profile management
- Templates:
  - `base.html` - Base template
  - `landing.html` - Landing page
  - `login.html` - Login page
  - `register.html` - Registration page

#### **Jobs** (`/jobs`)
- Job posting management
- Job listings and details
- Job-related operations

#### **Applications** (`/applications`)
- Job application handling
- Application tracking and management
- Application status workflow

#### **Assessments** (`/assessments`)
- Assessment creation and management
- Assessment tracking
- Candidate assessment evaluation

#### **Core** (`/core`)
- Core business logic
- Central data models
- Common utilities and helpers

### Project Configuration
- **Backend Settings**: `backend/settings.py`
- **URL Routing**: `backend/urls.py`
- **ASGI Config**: `backend/asgi.py`
- **WSGI Config**: `backend/wsgi.py`

## Development Setup

### Prerequisites
- Python 3.x
- Virtual Environment (penv)

### Installation
```bash
# Activate virtual environment
./penv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## Database
- SQLite database: `db.sqlite3` (Development)

## Key Features
- User authentication and account management
- Job posting and management
- Job application tracking
- Assessment system
- RESTful API endpoints

## Development Notes
- Custom user authentication with managers
- Signal handlers for automated tasks
- Custom serializers for API responses
- Comprehensive admin interface configuration
