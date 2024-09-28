# Patient Assessment & Management System

## Overview

This project is a **Patient Assessment & Management System** built using Django, Django REST Framework, and PostgreSQL. It manages patient records, user authentication, assessments, and practitioners' details. The system includes models for users, patients, practitioners, medications, allergies, and other related entities, making it suitable for healthcare organizations to keep track of patient health information and perform assessments.

## Setup Instructions

### Prerequisites

- Python 3.8+

- PostgreSQL

- Django 3.x

- Redis (optional, for caching)

### Installation

1. **Clone the repository**:

    ``` bash
      git clone https://github.com/sisterMagret/patient_assessment_management_system_api.git/
      cd patient_assessment_management_system_api
    
     ```

2. **Setup database**

     ``` bash
      chmod +x setupdb.sh
      ./setupdb.sh
     ```

3. **Install dependencies**:

    ``` bash
      pip install -r requirements.txt
    
     ```

4. **Configure environment variables**:  
    Set up your `.env` file with the necessary configurations such as database settings.

5. **Run migrations**:

    ``` bash
      python manage.py makemigrations
      python manage.py migrate
    
     ```

6. **Create superuser**:

    ``` bash
      python manage.py createsuperuser
    
     ```

7. **Run the server**:

    ``` bash
      python manage.py runserver
    
     ```

---

## Steps to Run with Docker

1. **Build and start containers**:

    ``` bash
      docker-compose up --build
    
     ```

2. **Access the app**:  
    The app will be accessible at [http://localhost:8000/](http://localhost:8000/).
