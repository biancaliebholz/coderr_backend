<h1 align="center">Coderr Backend</h1>

<p align="center">
  <strong>REST API for a service marketplace built with Django and Django REST Framework</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-0F172A?style=flat-square&logo=python&logoColor=FF9800" alt="Python 3.14">
  <img src="https://img.shields.io/badge/Django-5.2-0F172A?style=flat-square&logo=django&logoColor=FF9800" alt="Django 5.2">
  <img src="https://img.shields.io/badge/Django_REST_Framework-3.18-0F172A?style=flat-square" alt="Django REST Framework 3.18">
  <img src="https://img.shields.io/badge/Tests-153_passing-0F172A?style=flat-square&labelColor=FF9800" alt="153 passing tests">
  <img src="https://img.shields.io/badge/Coverage-100%25-0F172A?style=flat-square&labelColor=FF9800" alt="100 percent coverage">
</p>

---

Coderr Backend is a REST API for a service marketplace where business users can publish service offers and customers can order and review those services.

The API provides token-based authentication, user profiles, offers with different service packages, orders, reviews, image uploads, filtering, pagination, permissions, and aggregated platform statistics.

## Table of Contents

- [Technologies](#technologies)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Authentication](#authentication)
- [API Structure](#api-structure)
- [Permissions](#permissions)
- [Testing](#testing)
- [Admin Interface](#admin-interface)
- [Project Structure](#project-structure)
- [Important Notes](#important-notes)

## Technologies

- Python 3.14
- Django 5.2
- Django REST Framework 3.18
- DRF Token Authentication
- django-filter
- Pillow
- python-dotenv
- SQLite
- Coverage.py

All required Python packages and their exact versions are listed in `requirements.txt`.

## Quick Start

The Quick Start is intended for developers who already have Python and Git installed and are familiar with virtual environments.

### macOS or Linux

```bash
git clone https://github.com/biancaliebholz/coderr_backend.git
cd coderr_backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 manage.py migrate
python3 manage.py runserver
```

Before using the project outside local development, replace the placeholder `SECRET_KEY` inside `.env` with a securely generated key.

The API is then available at:

```text
http://127.0.0.1:8000/api/
```

## Detailed Installation

### 1. Clone the repository

```bash
git clone https://github.com/biancaliebholz/coderr_backend.git
cd coderr_backend
```

### 2. Create a virtual environment

The virtual environment keeps the dependencies of this project separate from other Python projects.

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

macOS or Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, the terminal prompt should begin with `(.venv)`.

### 4. Install the dependencies

```bash
python3 -m pip install -r requirements.txt
```

The `requirements.txt` file contains the packages required to run and test the project. The local `.venv` directory itself is not included in the repository.

### 5. Create the environment file

macOS or Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Generate a Django secret key:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated value into `.env`:

```env
SECRET_KEY=your-generated-secret-key
```

The `.env` file contains local configuration values and is excluded from version control.

### 6. Apply the database migrations

```bash
python3 manage.py migrate
```

This creates the local SQLite database and its required tables.

### 7. Check the Django configuration

```bash
python3 manage.py check
```

Expected result:

```text
System check identified no issues (0 silenced).
```

### 8. Start the development server

```bash
python3 manage.py runserver
```

The API is available at:

```text
http://127.0.0.1:8000/api/
```

The Django admin interface is available at:

```text
http://127.0.0.1:8000/admin/
```

Stop the server with `Control + C`.

## Authentication

The API uses Django REST Framework Token Authentication.

A token is returned after successful registration or login. Protected requests must include the token in the HTTP header:

```text
Authorization: Token <your-token>
```

Registration and login are public. Other endpoints require authentication unless they are explicitly intended to be publicly accessible.

The available user roles are:

- `customer`
- `business`

These roles determine which resources a user may create or modify.

## API Structure

All API routes use the `/api/` prefix.

### Authentication and Profiles

The users domain provides:

- User registration
- User login
- Token generation
- Individual profile retrieval
- Profile updates
- Business profile lists
- Customer profile lists
- Profile image uploads

### Offers

The offers domain provides:

- Public offer lists
- Offer creation for business users
- Individual offer retrieval
- Offer updates
- Offer deletion
- Individual offer package retrieval
- Search, filtering, ordering, and pagination

Each offer contains three service packages:

- `basic`
- `standard`
- `premium`

Each package can define its own price, delivery time, number of revisions, and included features.

### Orders

The orders domain provides:

- Order creation from a selected offer package
- User-specific order lists
- Order status updates
- Administrative order deletion
- In-progress order counts
- Completed order counts

Order data is stored as a snapshot of the selected offer package. Later changes to the original offer therefore do not modify existing orders.

Supported order statuses are:

- `in_progress`
- `completed`
- `cancelled`

### Reviews

The reviews domain provides:

- Review lists
- Review creation
- Review updates
- Review deletion
- Filtering by business user
- Filtering by reviewer
- Ordering by rating or update time

A customer can review the same business user only once.

### Platform Information

The base-info endpoint provides aggregated public statistics:

- Number of reviews
- Average rating
- Number of business profiles
- Number of offers

## Permissions

The API uses role-based and object-level permissions.

- Anyone can register or log in.
- Offer lists and platform statistics are public.
- Protected resources require a valid authentication token.
- Only a profile owner may update their profile.
- Only business users may create offers.
- Only the owner of an offer may update or delete it.
- Only customer users may create orders.
- Only the assigned business user may update an order status.
- Only staff users may delete orders.
- Only customer users may create reviews.
- Only the author of a review may update or delete it.

## Testing

Run the complete test suite:

```bash
python3 manage.py test
```

The current project contains 153 automated tests.

Check the Django configuration:

```bash
python3 manage.py check
```

Check whether model changes are missing migrations:

```bash
python3 manage.py makemigrations --check --dry-run
```

Check changed files for whitespace errors:

```bash
git diff --check
```

### Test Coverage

Clear previously collected coverage data:

```bash
python3 -m coverage erase
```

Run the complete test suite with coverage:

```bash
python3 -m coverage run \
  --source=users_app,offers_app,orders_app,reviews_app,base_info_app \
  manage.py test
```

Display the coverage report:

```bash
python3 -m coverage report -m \
  --omit="*/migrations/*,*/tests/*"
```

The current test suite reaches 100% coverage for the application code. Migration files and test files are excluded from the coverage calculation.

## Admin Interface

Django includes a separate administration interface for managing application data.

Create an administrator account:

```bash
python3 manage.py createsuperuser
```

Follow the prompts to enter a username, email address, and password.

Start the development server:

```bash
python3 manage.py runserver
```

Open the following address in a browser:

```text
http://127.0.0.1:8000/admin/
```

Log in with the superuser credentials created previously.

The admin interface is intended for internal administration. It allows authorized staff to inspect and manage users, profiles, offers, offer packages, orders, reviews, and authentication tokens. It is separate from the customer-facing frontend.

## Project Structure

```text
coderr_backend/
├── base_info_app/
│   ├── api/
│   └── tests/
├── offers_app/
│   ├── api/
│   ├── migrations/
│   └── tests/
├── orders_app/
│   ├── api/
│   ├── migrations/
│   └── tests/
├── reviews_app/
│   ├── api/
│   ├── migrations/
│   └── tests/
├── users_app/
│   ├── api/
│   ├── migrations/
│   └── tests/
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

Each domain app organizes its API-specific serializers, views, URLs, permissions, and tests according to its responsibilities.

Filtering and pagination are implemented only for endpoints that require them. The `base_info_app` does not contain a database model because it calculates aggregated information from the other domain models.

## Important Notes

- A custom user model based on Django's `AbstractUser` is used.
- Additional user information is stored in a one-to-one profile model.
- Every regular user has either a `customer` or `business` profile.
- Token Authentication is used for protected API requests.
- Profile and offer images are processed with Pillow.
- Uploaded files are stored inside the local `media/` directory.
- The secret key is loaded from a local `.env` file.
- The `.env` file is excluded from version control.
- The `.venv` directory is excluded from version control.
- The local SQLite database is excluded from version control.
- Uploaded media and coverage files are excluded from version control.
- The frontend is maintained separately and is not included in this repository.
- SQLite is used for local development.
- A production deployment should use a production-ready database such as PostgreSQL.
- `DEBUG` is enabled for local development and must be disabled before production deployment.
- The test and coverage badges represent the current project state and must be updated if these values change.
- This project was developed for educational purposes.
