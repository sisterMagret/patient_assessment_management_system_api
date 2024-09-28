# Patient Assessment & Management System

## Overview

This project is a **Patient Assessment & Management System** built using Django, Django REST Framework, and PostgreSQL. It manages patient records, user authentication, assessments, and practitioners' details. The system includes models for users, patients, practitioners, medications, allergies, and other related entities, making it suitable for healthcare organizations to keep track of patient health information and perform assessments.

## Setup Instructions

## Tech Stack

- **Backend**: Django, Django REST Framework

- **Database**: PostgreSQL

- **Authentication**: JWT and Oauth

- **File Storage**: Local storage for profile images and documents

- **API Documentation**: DRF-YASG 


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

In my own words, the deployment process to AWS would look something like this:

1. **Prepare the application**:
   First, make sure the application is production-ready by packaging all necessary files, dependencies, and configuration settings. For instance, if it's a web app, I would ensure the application is containerized (e.g., using Docker) or create the necessary artifacts for deployment.

2. **Choose the appropriate AWS services**:
   Depending on the nature of the application, I would decide which AWS service best fits the deployment. For instance, if it’s a web application, I would likely use **EC2** to launch instances to host the app. I would also determine whether I need a **Load Balancer** for traffic distribution or **Auto Scaling** to handle changing traffic loads.

3. **Set up the AWS environment**:
   Before deployment, I would set up the necessary AWS resources. This includes launching EC2 instances, configuring an **S3 bucket** if the application needs file storage, and ensuring that **RDS** or another database service is properly configured if the app requires database support.

4. **Configure security**:
   Proper security settings are crucial, so I would define **security groups**, set up **IAM roles** for the application, and ensure necessary ports are open while keeping others closed. At this stage, SSL certificates might also be applied if the application needs HTTPS access.

5. **Deploy the application**:
   The deployment process could vary depending on the tools being used. For EC2, I would typically SSH into the instance and use deployment tools like **Git**, **Ansible**, or even an automated CI/CD tool such as **AWS CodeDeploy** or **Jenkins** to push the app onto the server. 

6. **Monitor with CloudWatch**:
   Once deployed, I would set up **CloudWatch** for monitoring the health of the EC2 instance, tracking logs, and setting up alarms if something goes wrong. This allows for real-time monitoring and proactive handling of issues.

7. **Finalize and Test**:
   After deployment, I would perform a thorough round of testing to ensure the app is running as expected. This includes functional testing, load testing, and checking the application's integration with other AWS services like S3, databases, and API Gateway (if applicable).
