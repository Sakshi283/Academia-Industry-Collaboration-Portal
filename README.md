# CampusConnect — Academia–Industry Collaboration Portal

A Django web application connecting students, colleges and industry partners through skill mapping, internships and placement management.

## Technology
- Python 3.10+
- Django 5.2
- Official MongoDB Django Backend (`django-mongodb-backend`)
- PyMongo (installed automatically by the backend)
- MongoDB local server or MongoDB Atlas
- HTML and custom CSS (Bootstrap is not used)

## Implemented modules

### Student
- Register/login with a student role.
- Manage academic profile, phone and resume link.
- Add skills with Beginner, Intermediate or Advanced proficiency.
- Compare skills with company requirements and see match percentage plus missing skills.
- Browse internships and placement openings.
- Apply and track application status.

### Industry / Company
- Register/login with an industry role.
- Publish internship and placement opportunities.
- Specify required skills, eligibility, location, compensation and deadline.
- Edit or close opportunities.
- Review applications and update status.

### College / Admin
- Register/login with a college role.
- Dashboard with student, company and opportunity counts.
- Student activity report with skill and application counts.
- Recent application overview.

### Admin
- Django admin at `/admin/` for managing users, profiles, skills, opportunities and applications.

## Validation included

- Required fields and Django password validators on registration.
- Unique email address and username format checks.
- First/last name character validation.
- Phone number format validation.
- Graduation year range validation (2000–2100).
- Resume URL validation.
- Skill name length and character validation.
- Opportunity title and description length validation.
- Opportunity deadline cannot be in the past.
- Role checks: only students can add skills/apply; only industry accounts can post opportunities.
- Ownership checks: companies can edit only their own opportunities and manage only their own applications.
- Duplicate applications are prevented by a unique model constraint.
- CSRF protection is enabled for POST forms.

## Setup on Windows (local MongoDB)

### 1. Start MongoDB
Install MongoDB Community Server and make sure the MongoDB service is running on `localhost:27017`.
You can verify the server using MongoDB Compass or `mongosh`.

### 2. Extract and open the project
Extract the ZIP and open the `academia_industry_portal` folder in VS Code.

### 3. Create and activate virtual environment

```powershell
py -m venv venv
.\venv\Scripts\activate
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure MongoDB
The project defaults to:
- URI: `mongodb://localhost:27017`
- Database: `academia_industry_portal`

For a MongoDB Atlas database, copy `.env.example` to `.env` and set:

```env
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@YOUR-CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_NAME=academia_industry_portal
```

Replace the placeholders with your Atlas credentials. Do not share or commit `.env`.

### 6. Generate and apply migrations
The official Django MongoDB backend uses MongoDB-compatible migration files for Django's built-in apps. Run:

```powershell
python manage.py makemigrations admin auth contenttypes
python manage.py makemigrations collaboration
python manage.py migrate
```

If Django reports that built-in migrations already exist, keep the generated files under the `mongo_migrations` directory and continue with `migrate`.

### 7. Create admin account (optional)

```powershell
python manage.py createsuperuser
```

### 8. Start the portal

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Demo flow

1. Register an account with role **Industry/Company** and post an opportunity.
2. Register a **Student** account and add skills.
3. Open **Skill Mapping** to view matching and missing skills.
4. Apply to the opportunity.
5. Log in as the company and change the application status.
6. Register/login as **College/Admin** and inspect the student report.

## Notes

- MongoDB is the configured database; SQLite is not used by this version.
- MongoDB must be running and reachable before starting the application.
- This is an academic demonstration project. Before production deployment, set a strong secret key, disable debug mode, configure allowed hosts, enforce HTTPS, and review authentication and operational security.
- Database schema and validation rules may need further refinement to match your institution's final evaluation rubric.
