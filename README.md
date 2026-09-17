# Coderr Backend

Coderr Backend is a REST API for a service marketplace where business users can offer services and customers can order and review them.

The backend is built with Django and Django REST Framework. It provides token-based authentication, user profiles, offers, orders, reviews, image uploads, filtering, pagination, permissions, and aggregated platform statistics.

## Table of Contents

- [Technologies](#technologies)
- [Quick Start](#quick-start)
- [Step-by-Step Installation](#step-by-step-installation)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Permissions](#permissions)
- [Testing](#testing)
- [Admin Interface](#admin-interface)
- [Project Structure](#project-structure)
- [Important Notes](#important-notes)

## Technologies

- Python 3.14
- Django 5.2
- Django REST Framework
- DRF Token Authentication
- django-filter
- Pillow
- python-dotenv
- SQLite
- Coverage.py

## Quick Start

The following commands provide a compact setup for macOS and Linux:

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

Before starting the server, replace the placeholder `SECRET_KEY` inside `.env` with a generated Django secret key.

Generate one with:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

The API is then available at:

```text
http://127.0.0.1:8000/api/
```

For a platform-specific explanation, follow the detailed installation below.

## Step-by-Step Installation

### 1. Clone the repository

```bash
git clone https://github.com/biancaliebholz/coderr_backend.git
cd coderr_backend
```

### 2. Create a virtual environment

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

### 4. Install the dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 5. Create the environment file

macOS or Linux:

```bash
cp .env.example .env
```

Windows:

```powershell
copy .env.example .env
```

Generate a Django secret key:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Replace the placeholder inside `.env` with the generated value:

```env
SECRET_KEY=your-generated-secret-key
```

The local `.env` file must not be committed to version control.

### 6. Apply the database migrations

```bash
python3 manage.py migrate
```

### 7. Start the development server

```bash
python3 manage.py runserver
```

The API endpoints use the following base URL:

```text
http://127.0.0.1:8000/api/
```

The Django admin interface is available at:

```text
http://127.0.0.1:8000/admin/
```

## Authentication

The API uses Django REST Framework Token Authentication.

A token is returned after successful registration or login. Protected requests must include the token in the HTTP header:

```text
Authorization: Token <your-token>
```

Registration and login are public. Other endpoints require authentication unless they are explicitly documented as public.

## API Endpoints

### Authentication and Profiles

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/registration/` | Register a customer or business user |
| POST | `/api/login/` | Authenticate a user and return a token |
| GET | `/api/profile/{id}/` | Retrieve a user profile |
| PATCH | `/api/profile/{id}/` | Update the authenticated user's profile |
| GET | `/api/profiles/business/` | List all business profiles |
| GET | `/api/profiles/customer/` | List all customer profiles |

### Offers

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/offers/` | List, filter, search, order, and paginate offers |
| POST | `/api/offers/` | Create an offer with its package details |
| GET | `/api/offers/{id}/` | Retrieve a specific offer |
| PATCH | `/api/offers/{id}/` | Partially update an owned offer |
| DELETE | `/api/offers/{id}/` | Delete an owned offer |
| GET | `/api/offerdetails/{id}/` | Retrieve a specific offer package |

Each offer contains three package types:

- `basic`
- `standard`
- `premium`

The offer list supports:

- Filtering by creator
- Filtering by minimum price
- Filtering by maximum delivery time
- Searching by title and description
- Ordering by update time or minimum price
- Configurable page size

### Orders

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/orders/` | List orders related to the authenticated user |
| POST | `/api/orders/` | Create an order from an offer package |
| PATCH | `/api/orders/{id}/` | Update an order status |
| DELETE | `/api/orders/{id}/` | Delete an order as a staff user |
| GET | `/api/order-count/{business_user_id}/` | Count in-progress orders |
| GET | `/api/completed-order-count/{business_user_id}/` | Count completed orders |

Order data is stored as a snapshot of the selected offer package. Later changes to an offer therefore do not alter an existing order.

Supported order statuses are:

- `in_progress`
- `completed`
- `cancelled`

### Reviews

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reviews/` | List, filter, and order reviews |
| POST | `/api/reviews/` | Create a review for a business user |
| PATCH | `/api/reviews/{id}/` | Update an owned review |
| DELETE | `/api/reviews/{id}/` | Delete an owned review |

Reviews can be:

- Filtered by business user
- Filtered by reviewer
- Ordered by rating
- Ordered by update time

A customer can review the same business user only once.

### Platform Information

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/base-info/` | Return public aggregated platform statistics |

The response contains:

- Number of reviews
- Average rating
- Number of business profiles
- Number of offers

## Permissions

The API uses role-based and object-level permissions:

- Anyone can register or log in.
- The offer list and platform statistics are public.
- Profile lists and individual profiles require authentication.
- Only a profile owner may update their profile.
- Only business users may create offers.
- Only the offer owner may update or delete an offer.
- Only customer users may create orders.
- Only the assigned business user may update an order status.
- Only staff users may delete orders.
- Only customer users may create reviews.
- Only the review author may update or delete a review.

## Testing

Run the complete test suite:

```bash
python3 manage.py test
```

Check the Django configuration:

```bash
python3 manage.py check
```

Check whether model changes are missing migrations:

```bash
python3 manage.py makemigrations --check --dry-run
```

Check the changes for whitespace errors:

```bash
git diff --check
```

Run the complete test suite with coverage:

```bash
python3 -m coverage erase
python3 -m coverage run \
  --source=users_app,offers_app,orders_app,reviews_app,base_info_app \
  manage.py test
```

Display the coverage report:

```bash
python3 -m coverage report -m \
  --omit="*/migrations/*,*/tests/*"
```

The project currently contains 153 automated tests and reaches 100% coverage for the application code.

## Admin Interface

Create an administrator account:

```bash
python3 manage.py createsuperuser
```

Start the development server:

```bash
python3 manage.py runserver
```

Open the admin interface:

```text
http://127.0.0.1:8000/admin/
```

The main project models are registered and manageable through the Django admin interface.

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

Each domain app contains its API-specific serializers, views, URLs, permissions, filters, pagination, and tests where required.

## Important Notes

- A custom user model based on Django's `AbstractUser` is used.
- Additional user information is stored in a one-to-one profile model.
- Every user has either a `customer` or `business` profile.
- Profile and offer images are processed with Pillow.
- Uploaded images are stored inside the local `media/` directory.
- The secret key is loaded from a local `.env` file.
- The `.env` file is excluded from version control.
- The local SQLite database is excluded from version control.
- Uploaded media and coverage files are excluded from version control.
- The frontend is maintained separately and is not included in this repository.
- SQLite is used for local development.
- `DEBUG` is enabled for local development and must be disabled before production deployment.
- This project is intended for development and educational purposes.
