<div align="center">

# Coderr Backend

REST API for a service marketplace where business users offer services and customers place orders and submit reviews.

![Python](https://img.shields.io/badge/Python-3.14-0F172A?style=flat-square&logo=python&logoColor=FF9800)
![Django](https://img.shields.io/badge/Django-5.2-0F172A?style=flat-square&logo=django&logoColor=FF9800)
![Django REST Framework](https://img.shields.io/badge/DRF-3.18-0F172A?style=flat-square)

</div>

## Contents

- [Features](#features)
- [Technologies](#technologies)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Permissions](#permissions)
- [Testing](#testing)
- [Admin Interface](#admin-interface)
- [Project Structure](#project-structure)
- [Notes](#notes)

## Features

The API provides:

- User registration and login
- Customer and business profiles
- Profile image uploads
- Offers with multiple service packages
- Offer filtering, searching, ordering and pagination
- Orders based on offer packages
- Order status management
- Reviews for business users
- Aggregated platform statistics

## Technologies

- Python
- Django
- Django REST Framework
- Token Authentication
- django-filter
- Pillow
- python-dotenv
- SQLite
- coverage.py

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/biancaliebholz/coderr_backend.git
cd coderr_backend
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On Windows, use `python` instead of `python3` if required.

### 3. Install the dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Configure the environment

Create the local environment file:

```bash
cp .env.example .env
```

Generate a Django secret key:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add the generated value to `.env`:

```env
SECRET_KEY=your-generated-secret-key
```

### 5. Apply the migrations

```bash
python3 manage.py migrate
```

### 6. Start the development server

```bash
python3 manage.py runserver
```

The API is available under:

```text
http://127.0.0.1:8000/api/
```

## Authentication

The API uses Django REST Framework Token Authentication.

A token is returned after successful registration or login. Include it in protected requests:

```http
Authorization: Token <your-token>
```

## Permissions

Protected endpoints require authentication. Access to offers, orders and reviews depends on the user's role, ownership and staff status.

## Testing

Run the complete test suite:

```bash
python3 manage.py test
```

Check the Django configuration:

```bash
python3 manage.py check
```

Verify that no migrations are missing:

```bash
python3 manage.py makemigrations --check --dry-run
```

Run the tests with coverage:

```bash
python3 -m coverage erase
python3 -m coverage run \
  --source=users_app,offers_app,orders_app,reviews_app,base_info_app \
  manage.py test
python3 -m coverage report -m \
  --omit="*/migrations/*,*/tests/*"
```

The current test suite contains 153 tests and reaches 100% application-code coverage.

## Admin Interface

Create an administrator account:

```bash
python3 manage.py createsuperuser
```

Start the development server and open:

```text
http://127.0.0.1:8000/admin/
```

The Django admin interface can be used to inspect and manage the application data.

## Project Structure

```text
coderr_backend/
├── base_info_app/
│   ├── api/
│   └── tests/
├── offers_app/
│   ├── api/
│   └── tests/
├── orders_app/
│   ├── api/
│   └── tests/
├── reviews_app/
│   ├── api/
│   └── tests/
├── users_app/
│   ├── api/
│   └── tests/
├── core/
├── manage.py
├── requirements.txt
└── README.md
```

Each domain app contains the API modules and tests required for its responsibilities. Filtering and pagination are implemented only where needed.

## Notes

- The frontend is maintained separately and is not included in this repository.
- SQLite is used for local development. A production deployment should use a production-ready database such as PostgreSQL.
- The local database, virtual environment, environment variables, uploaded media and coverage files are excluded from version control.
- This project was created for educational purposes.
