# Task 2 - FastAPI + PostgreSQL (Classic Models)

This project implements a layered FastAPI API (database, schemas, CRUD, router) on top of the classicmodels schema from seed.sql. It includes logging, Docker Compose for PostgreSQL, and Swagger UI for testing.

## Project Structure

- app/database.py: database connection and session management
- app/schemas.py: Pydantic schemas for validation
- app/crud.py: database operations (Create, Read, Update, Delete)
- app/routers/customers.py: API endpoints
- app/core/logger.py: shared logging configuration
- docker-compose.yml: PostgreSQL container
- seed.sql: schema and sample data

## Requirements

- Python 3.12
- Docker Desktop (for PostgreSQL)

## Setup

1) Start PostgreSQL using Docker Compose

```powershell
docker compose up -d
```

2) Create and activate a Python virtual environment

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

3) Install dependencies

```powershell
pip install -r requirements.txt
```

4) Load the seed data

```powershell
Get-Content seed.sql | docker exec -i task2-postgres psql -U postgres -d mydb
```

5) Run the API

```powershell
uvicorn app.main:app --reload
```

Open Swagger UI:

- http://localhost:8000/docs

## Database Connection

The connection string is stored in .env:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/mydb
```

If port 5432 is already in use, either stop the other Postgres instance or change docker-compose.yml to map to 5433 and update DATABASE_URL accordingly.

## API Endpoints (Customers)

- GET /customers/?skip=0&limit=10
- GET /customers/{customerNumber}
- POST /customers/
- PUT /customers/{customerNumber}
- DELETE /customers/{customerNumber}
- GET /customers/{customerNumber}/orders
- GET /customers/{customerNumber}/payments

## Example Requests

### List customers

```
GET http://localhost:8000/customers/?skip=0&limit=5
```

### Get one customer

```
GET http://localhost:8000/customers/103
```

### Create a customer

Note: customerNumber is the primary key. Pick a number that does not already exist.

```json
{
  "customerNumber": 9998,
  "customerName": "Alice Johnson LLC",
  "contactLastName": "Johnson",
  "contactFirstName": "Alice",
  "phone": "555-123-4567",
  "addressLine1": "123 Main St",
  "addressLine2": null,
  "city": "Boston",
  "state": "MA",
  "postalCode": "02110",
  "country": "USA",
  "salesRepEmployeeNumber": 1165,
  "creditLimit": 50000.00
}
```

### Update a customer

```json
{
  "phone": "555-999-0000",
  "creditLimit": 75000.00
}
```

### Orders and payments

```
GET http://localhost:8000/customers/103/orders
GET http://localhost:8000/customers/103/payments
```

## Logging

Logs go to app.log and include:

- Database connection events
- CRUD operations
- HTTP requests
- Warnings and errors

## Troubleshooting

### Port 5432 already in use

- Stop the other PostgreSQL instance, or
- Change docker-compose.yml to map 5433:5432 and update DATABASE_URL.

### Duplicate key on customerNumber

If you see:

```
duplicate key value violates unique constraint "customers_pkey"
```

Choose a different customerNumber and try again.

### Python version issues

SQLAlchemy and dependencies may not work on Python 3.14. Use Python 3.12.

## Quick Test Flow (Swagger UI)

1) GET /customers?skip=0&limit=5
2) GET /customers/103
3) GET /customers/103/orders
4) GET /customers/103/payments
