# Airport API

A Django REST Framework API for managing airports, routes, airplanes, flights, crew, tickets, and orders.

## Features

- Airport and route management.
- Airplane, airplane type, and crew management.
- Flight listing, filtering, searching, ordering, and pagination.
- JWT authentication and public user registration.
- Role-based permissions for regular and staff users.
- Order creation with multiple tickets.
- Ticket validation, including seat availability and airplane capacity.
- Flight available-seat endpoint.
- Interactive API documentation with Swagger UI.
- Docker support.

## Database Diagram

![Database diagram](Images_README/img.png)

## Requirements

- Python 3.10 or newer, compatible with the dependencies in `requirements.txt`.
- Git.
- Docker and Docker Compose (optional).

## Clone the Repository

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Rostyk-D/airport-api.git
cd airport-api
```

Switch to the development branch:

```bash
git switch develop
```

## Run Locally

### 1. Create a Virtual Environment

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Linux/macOS:

```bash
export DEBUG=True
export SECRET_KEY="local-development-only-change-me"
```

Windows PowerShell:

```powershell
$env:DEBUG = "True"
$env:SECRET_KEY = "local-development-only-change-me"
```

Use a private, randomly generated `SECRET_KEY` outside local development. Never commit production secrets to the repository.

The project supports a development fallback for `SECRET_KEY` only when `DEBUG=True`.

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser

Create an administrator account to access Django Admin and manage resources that require staff permissions:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter the username, email address, and password.

### 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at:

- API root: `http://127.0.0.1:8000/`
- Django Admin: `http://127.0.0.1:8000/admin/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

## Run with Docker

Docker Compose uses SQLite, so no separate PostgreSQL service is required.

Build and start the application:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000/`.

Migrations run automatically when the container starts.

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Stop the application:

```bash
docker compose down
```

The project directory is mounted into the container, allowing code changes and the SQLite database file to persist on the host.

## Authentication

The API uses JSON Web Token (JWT) authentication.

### 1. Register a User

Registration is public.

**Endpoint:** `POST /api/users/`

Example request:

```json
{
  "username": "testuser",
  "email": "user@example.com",
  "password": "StrongPass123!",
  "first_name": "Test",
  "last_name": "User"
}
```

Submit the request through Swagger UI or an HTTP client such as Postman.

The registration endpoint accepts the fields defined by the user serializer. Adjust the example if additional required fields are configured.

### 2. Obtain JWT Tokens

**Endpoint:** `POST /api/users/login/`

Example request:

```json
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

Use the returned access token to call protected endpoints:

```http
Authorization: Bearer <access_token>
```

### 3. Refresh an Access Token

**Endpoint:** `POST /api/users/login/refresh/`

Example request:

```json
{
  "refresh": "<refresh_token>"
}
```

Access tokens are valid for one day, and refresh tokens are valid for two days.

### 4. Access Protected Endpoints

After obtaining an access token, include it in the `Authorization` header when making requests to protected endpoints.

For example:

```http
GET /api/orders/
Authorization: Bearer <access_token>
```

## Permissions

### Public Resources

The following resources can be viewed without authentication:

- Airports
- Routes
- Crew
- Airplane types
- Airplanes
- Flights

Only staff users can create, update, or delete these resources.

### Users

- User registration is public.
- User listing and management require staff access after registration.

### Orders

- Authentication is required.
- Regular users can view only their own orders.
- Staff users can view all orders.
- Regular users can create orders but cannot update or delete them.
- Staff users can update and delete orders.

### Tickets

- Tickets are read-only through the API.
- Tickets are created together with an order.
- Authenticated users can list tickets belonging to their own orders.
- Staff users can view all tickets.

## Tickets and Baggage

Each ticket has a `baggage_type` field:

| Value | Baggage Type |
|---|---|
| `1` | Light |
| `2` | Medium |
| `3` | Heavy |

The API stores the baggage category; baggage weight is not stored as a separate ticket field.

### Create an Order with Two Tickets

**Endpoint:** `POST /api/orders/`

Example request:

```json
{
  "tickets": [
    {
      "row": 1,
      "seat": 1,
      "flight": 1,
      "baggage_type": 1
    },
    {
      "row": 1,
      "seat": 2,
      "flight": 1,
      "baggage_type": 3
    }
  ]
}
```

The API validates:

- Flight departure time.
- Row and seat limits for the airplane.
- Seat availability.
- Duplicate seats within an order.
- At least one ticket per order.

The request must be authenticated.

## Flights

The flights endpoint supports filtering, searching, ordering, and pagination.

### Filter by Route

```http
GET /api/flights/?route=1
```

### Filter by Airplane

```http
GET /api/flights/?airplane=1
```

### Filter by Source and Destination Airports

```http
GET /api/flights/?source=1&destination=2
```

### Filter by Departure Date

```http
GET /api/flights/?departure_date=2026-10-01
```

### Search by Airport, City, Airplane, or Airplane Type

```http
GET /api/flights/?search=Warsaw
```

### Order Results

```http
GET /api/flights/?ordering=departure_time
```

### Pagination

```http
GET /api/flights/?page=2&page_size=20
```

### Get Available Seats

```http
GET /api/flights/1/available-seats/
```

Replace the example IDs with existing database records.

## API Documentation

Interactive API documentation is available through Swagger UI.

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

Swagger UI can be used to inspect endpoints, review request and response schemas, and try API requests.

## Run Tests

Run the project's automated tests:

```bash
python manage.py test
```

Check the Django configuration:

```bash
python manage.py check
```

Check whether model changes require new migrations:

```bash
python manage.py makemigrations --check
```