# Airport API

Django REST Framework API for airports, routes, airplanes, flights, tickets and orders.

## Authentication

The API uses JWT authentication.

### Login

`POST /api/users/login/`

```json
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

Use the returned access token in the header:

```
Authorization: Bearer <access_token>
```

Refresh an access token:

`POST /api/users/login/refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

Access tokens live for 1 day and refresh tokens live for 2 days.

## Permissions

Airports, routes, crew, airplane types, airplanes and flights can be viewed publicly.

Only staff users can create, update or delete those resources.

Users can register publicly. The users endpoint is admin-only after registration.

Orders require authentication:
- regular users see only their own orders;
- admins see all orders;
- regular users can create orders, but cannot update or delete them;
- admins can update or delete orders.

Tickets are read-only through the API. Tickets are created together with an order.

## Tickets and baggage

Each ticket has a type:
- `1` — Light: 1–2 kg
- `2` — Medium: 3–5 kg
- `3` — Heavy: 6–10 kg

The buyer provides both the ticket type and the baggage weight. The API validates that the selected weight belongs to the selected type.

Example order with two tickets:

```json
{
  "tickets": [
    {
      "row": 5,
      "seat": 10,
      "flight": 1,
      "ticket_type": 1,
      "baggage_weight": 2
    },
    {
      "row": 5,
      "seat": 11,
      "flight": 1,
      "ticket_type": 3,
      "baggage_weight": 10
    }
  ]
}
```

The API also validates the flight date, row and seat limits, seat availability, duplicate seats inside one order, and the minimum of one ticket per order.

## Flights

Filter by route:

`GET /api/flights/?route=1`

Filter by airplane:

`GET /api/flights/?airplane=1`

Filter by airports:

`GET /api/flights/?source=1&destination=2`

Filter by departure date:

`GET /api/flights/?departure_date=2026-10-01`

Search by airport, city, airplane or airplane type:

`GET /api/flights/?search=Warsaw`

Order results:

`GET /api/flights/?ordering=departure_time`

Pagination:

`GET /api/flights/?page=2&page_size=20`

Available seats for a flight:

`GET /api/flights/1/available-seats/`

## API documentation

Swagger UI:

`GET /api/docs/`

OpenAPI schema:

`GET /api/schema/`

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Run the server:

```bash
python manage.py runserver
```

Run tests:

```bash
python manage.py test
```
