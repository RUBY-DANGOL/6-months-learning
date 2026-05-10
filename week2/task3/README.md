# Concurrency Counts API (FastAPI)

High-performance API dashboard that retrieves record counts from multiple database tables concurrently using asyncio.gather().

## Features
- 8 modular count endpoints (one per table)
- Aggregated /overall_counts endpoint using concurrency
- Structured logging at router and CRUD layers, plus total timing for concurrency
- Simple HTML dashboard

## File Structure
```
.
|- app/
|  |- __init__.py
|  |- main.py
|  |- router.py
|  |- crud.py
|  |- db.py
|  |- templates/
|  |  |- dashboard.html
|  |- static/
|     |- style.css
|- seed.sql
|- requirements.txt
|- .env
|- Task3_Week2.pdf
```

## Requirements
- Python 3.11+
- PostgreSQL (local or Docker)

## Setup

### 1) Create virtual environment
```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Configure environment
Create a .env file:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mydb
```

### 4) Start PostgreSQL (Docker option)
```powershell
docker run --name mydb -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mydb -p 5432:5432 -d postgres:15
```

### 5) Seed the database
```powershell
Get-Content .\seed.sql | docker exec -i mydb psql -U postgres -d mydb
```

### 6) Run the API
```powershell
uvicorn app.main:app --reload --env-file .env
```

## Endpoints

### Individual Count Endpoints
- GET /customers/count
- GET /orders/count
- GET /products/count
- GET /employees/count
- GET /offices/count
- GET /payments/count
- GET /orderdetails/count
- GET /productlines/count

### Aggregated Endpoint
- GET /overall_counts

Example response:
```json
{
  "customers": 122,
  "orders": 326,
  "products": 110,
  "employees": 23,
  "offices": 7,
  "payments": 273,
  "orderdetails": 2996,
  "productlines": 7
}
```

## Dashboard
Open http://127.0.0.1:8000/

## Logging
- Router: request start and success/failure
- CRUD: query start, completion, and errors
- Aggregated endpoint: concurrency start, completion, and timing
