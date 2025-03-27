# School Payment Portal

Django-based student payment portal with admin management.

## Features
- Student dashboard
- Payment tracking
- Admin interface for user management

## Setup

1. Clone repository:
   ```bash
   git clone https://github.com/DIttoSensei/Student_portal.git
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```