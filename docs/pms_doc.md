# Patient Assessment & Management System

## Overview

This project is a **Patient Assessment & Management System** built using Django, Django REST Framework, and PostgreSQL. It manages patient records, user authentication, assessments, and practitioners' details. The system includes models for users, patients, practitioners, medications, allergies, and other related entities, making it suitable for healthcare organizations to keep track of patient health information and perform assessments.

## Assumptions Made During Development

- **User Roles**: It was assumed that there would be a clear distinction between user roles (Patients, Practitioners) to manage permissions and data access effectively.

- **Data Relationships**: I assumed that users would have one-to-one relationships with patients and practitioners, which influenced the design of the models.

- **Network Availability**: I assumed that the application would be deployed in an environment with stable internet access for external API integrations, like sending emails or verifying tokens.

---

## Challenges Faced

One of the significant challenges encountered during development was **data modeling**. Ensuring that the relationships between users, patients, and their respective data were correctly defined required careful planning and iteration.

To overcome this challenge, I:

- Conducted thorough research on Django's ORM capabilities and best practices for relational data.

- Iterated through the models multiple times, soliciting feedback to refine the relationships and attributes.

- Validating user inputs, especially for medical records, was tricky. I created custom validation methods in the models to ensure that only valid data was processed, which enhanced data integrity.

---

## Additional Features or Improvements

While the core functionality was the primary focus, I also added several improvements:

- **Custom Validation Logic**: Implemented custom validation methods within models to ensure data integrity (e.g., ensuring a user can only be linked to a patient if they have the appropriate role).

- **User-Friendly Error Messages**: Enhanced error handling to provide clearer feedback to users on what went wrong during data submission.

- **Modular Code Structure**: Organized the code into logical modules for better maintainability and scalability.

## Authentication

All API endpoints (except the authentication-related ones) require an authorization header to be included in the request. The system uses **Bearer Token Authentication** to authorize requests.

To obtain the token, make a `POST` request to the `/auth/login` endpoint with valid user credentials. Upon successful authentication, the API will return a **JWT token**.

Include the token in the `Authorization` header of your requests as follows:

Authorization:

## Table of Contents

- [Tech Stack](#tech-stack)

- [Project Structure](#project-structure)

- [Database Models](#database-models)

- [Custom Features](#custom-features)

- [Admin Customization](#admin-customization)

- [Code Patterns](#code-patterns)

- [Setup Instructions](#setup-instructions)

- [Docker Integration](#docker-integration)

---

## Tech Stack

- **Backend**: Django, Django REST Framework

- **Database**: PostgreSQL

- **Authentication**: JWT and Oauth

- **File Storage**: Local storage for profile images and documents

- **API Documentation**: DRF-YASG (optional)

---

## Project Structure

- **apps/users**: Handles user authentication, user management. Manages patient-related models like allergies, medications, and emergency contacts. Also Contains details about practitioners, their specialization, and certifications.

- **apps/assessment**: Manages assessment-related models

- **apps/utils**: Contains utility code like enums, abstract models (e.g., `AbstractUUID`), and custom validators.

- **setupdb.py**: Used to setup project database

- **config**: Contains django configuration files

---

## Database Models

### 1\. **User Model**

- Extends Django's `AbstractUser`.

- Custom fields:

  - `user_role`: Role of the user (e.g., Admin, Practitioner, Patient).

  - `phone_number`, `address`, `avatar`, `gender`, etc.

- Properties:

  - `age`: Automatically calculates the age based on the user's `date_of_birth`.

- Relations:

  - `address`: Linked to an `Address` model.

### 2\. **Patient Model**

- A `OneToOneField` relationship with the `User` model.

- Fields:

  - `blood_group`, `genotype`, `nationality`, and `emergency_contact`.

- Relations:

  - `allergies`: A `ManyToManyField` with the `Allergy` model.

  - `medications`: A `ManyToManyField` with the `Medication` model.

- **Validation**: Ensures that the `user_role` is `PATIENT` before saving.

### 3\. **Practitioner Model**

- Linked to the `User` model via a `OneToOneField`.

- Fields:

  - `license_number`, `means_of_identification`, `certificate`, etc.

- Relations:

  - `specializations`: A `ManyToManyField` to `PractitionerSpecialization`.

### 4\. **Other Models**

- **Allergy**: Represents patient allergies.

- **Medication**: Represents medications taken by patients.

- **EmergencyContact**: Stores emergency contacts for patients.

- **AuthToken**: Used for handling user authentication tokens (e.g., verification, password resets).

---

## Custom Features

### 1\. **User Role Management**

The `User` model includes a `user_role` field, which can be one of several roles (e.g., Admin, Practitioner, Patient). This is implemented using a Django `PositiveSmallIntegerField` with predefined choices stored in the `UserType` enum.

### 2\. **Profile Images and Documents**

The system allows users (patients and practitioners) to upload documents such as:

- **Profile pictures**: Stored in `/media/profile/`.

- **Certificates and IDs**: Uploaded documents are stored in `/media/documents/`.

### 3\. **Custom Validation**

- The `Patient` model includes custom validation logic to ensure that the linked user has the `PATIENT` role.

- Custom validation for `Practitioner` ensures that the practitioner uploads valid identification and certificates.

---

## Admin Customization

The admin panel is customized to make management easier for users, patients, and practitioners. Key features include:

- Search fields for quick filtering (`first_name`, `last_name`, `phone_number`, etc.).

- List display for key model fields.

- Filters for model-specific fields such as `user_role`, `blood_group`, etc.

---

## Code Patterns

1. **Abstract Models**  
    Common attributes like UUID fields are abstracted into `AbstractUUID` to avoid duplication. All models inherit from this.

2. **Choices and Enums**  
    Predefined choices for fields like `UserType`, `GenderType`, and `BloodGroupType` are implemented using enums to ensure data consistency and improve maintainability.

3. **Custom Validators**

    - The `Patient` model uses a `clean()` method to ensure only users with the `PATIENT` role can be linked.

    - Practitioners must upload valid documents, validated using custom validation logic.

---

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

```bash
    EMAIL_HOST=
    EMAIL_HOST_USER=sistermagret@gmail.com
    EMAIL_HOST_PASSWORD=test1234
    REDIS_PASSWORD='django.db.backends.postgresql_psycopg2'
    BASE_BE_URL=localhost:8000
    DATABASE_NAME=pms
    DATABASE_USER=admin
    DATABASE_PASSWORD=adminpassword
    DATABASE_HOST=local
    DATABASE_PORT=5432
    DATABASE_ENGINE=
```

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

---

## Future Improvements

1. **API Documentation**:  
    Add DRF-YASG or Swagger for better API documentation.
