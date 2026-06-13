# Concurrency Counts API (FastAPI)

A high-performance asynchronous API and interactive dashboard that retrieves record counts from multiple database tables concurrently. Built with FastAPI, PostgreSQL, and asyncpg for optimal performance.

## Features

- **Asynchronous Endpoints:** Individual endpoints to fetch counts from each table
- **Concurrent Data Fetching:** `/overall_counts` endpoint uses `asyncio.gather()` to fetch all counts simultaneously
- **Interactive Dashboard:** HTML/CSS-based dashboard to visualize record counts in real-time
- **Structured Logging:** Comprehensive logging at all layers for monitoring and debugging
- **API Documentation:** Interactive Swagger UI and ReDoc for testing endpoints
- **Database Connection Pooling:** Efficient connection management with asyncpg

## Project Structure

```
.
├── app/
│   ├── core/
│   │   └── database.py          # Database connection and pool management
│   ├── routers/
│   │   └── counts.py            # API endpoints for counting records
│   ├── crud.py                  # CRUD operations for database queries
│   ├── static/
│   │   └── style.css            # Dashboard styling
│   ├── templates/
│   │   └── dashboard.html       # Interactive dashboard UI
│   ├── __init__.py
│   └── main.py                  # FastAPI application entry point
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Docker Compose configuration
├── README.md                    # This file
├── requirements.txt             # Python dependencies
└── seed.sql                     # Database schema and sample data
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **Docker Desktop** (optional but recommended) - [Download Docker](https://www.docker.com/products/docker-desktop)
- **Git** - [Download Git](https://git-scm.com/)

If not using Docker, you'll need PostgreSQL installed separately.

## Setup Instructions

### Step 1: Clone and Navigate to the Project

```powershell
# Navigate to the project directory
cd "C:\Users\rubin\OneDrive\Desktop\AI fellow\week2\task3"
```

### Step 2: Create and Activate a Virtual Environment

Creating a virtual environment isolates your project dependencies.

**On Windows (PowerShell):**
```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv myenv
source myenv/bin/activate
```

After activation, you should see `(myenv)` in your terminal prompt.

### Step 3: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `asyncpg` - PostgreSQL driver
- `jinja2` - Template engine
- `python-dotenv` - Environment variable management

### Step 4: Set Up Environment Variables

Create a `.env` file from the template:

```powershell
cp .env.example .env
```

Open `.env` and set your database connection string (it should already have defaults):

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mydb
```

**Connection String Format:**
- `postgresql://` - Protocol (required for asyncpg)
- `postgres` - Username
- `postgres` - Password
- `localhost` - Host
- `5432` - Port (default PostgreSQL port)
- `mydb` - Database name

### Step 5: Set Up PostgreSQL Database

#### Option A: Using Docker Compose (Recommended)

This is the easiest way to set up PostgreSQL without installing it locally.

```powershell
# Start the PostgreSQL container in the background
docker compose up -d

# Wait a few seconds for PostgreSQL to start, then seed the database
Get-Content .\seed.sql | docker exec -i task3-postgres psql -U postgres -d mydb
```

The Docker container will:
- Run PostgreSQL 15 on `localhost:5432`
- Create a database named `mydb`
- Use username `postgres` and password `postgres`

#### Option B: Using Docker CLI Directly

```powershell
# Start PostgreSQL container
docker run --name mydb -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mydb -p 5432:5432 -d postgres:15

# Wait for the container to be ready (usually 5-10 seconds), then seed the database
Get-Content .\seed.sql | docker exec -i mydb psql -U postgres -d mydb
```

#### Option C: Local PostgreSQL Installation

1. Ensure PostgreSQL is installed and running on your system
2. Create a database named `mydb`:
   ```powershell
   psql -U postgres -c "CREATE DATABASE mydb;"
   ```
3. Seed the database:
   ```powershell
   psql -U postgres -d mydb -f seed.sql
   ```

### Step 6: Run the Application

With the virtual environment activated and database running:

```powershell
python -m uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

## Accessing the Application

Once the application is running, you can access:

### 1. Interactive Dashboard
```
http://127.0.0.1:8000/
```
A visual dashboard showing counts from all tables in real-time.

### 2. API Documentation (Swagger UI)
```
http://127.0.0.1:8000/docs
```
Interactive API documentation where you can test endpoints directly.

### 3. Alternative API Docs (ReDoc)
```
http://127.0.0.1:8000/redoc
```
Alternative documentation format.

## API Endpoints

### Individual Count Endpoints

Get the count of records from a specific table:

```
GET /customers/count        → {"customers": 123}
GET /orders/count           → {"orders": 456}
GET /products/count         → {"products": 789}
GET /employees/count        → {"employees": 10}
GET /offices/count          → {"offices": 7}
GET /payments/count         → {"payments": 320}
GET /orderdetails/count     → {"orderdetails": 2996}
GET /productlines/count     → {"productlines": 7}
```

### Aggregated Count Endpoint

Get counts from all tables simultaneously (uses async concurrency):

```
GET /overall_counts
```

**Response:**
```json
{
  "customers": 123,
  "orders": 456,
  "products": 789,
  "employees": 10,
  "offices": 7,
  "payments": 320,
  "orderdetails": 2996,
  "productlines": 7
}
```

## Troubleshooting

### Issue: `DATABASE_URL is not set`

**Solution:** Ensure the `.env` file exists in the task3 directory and contains `DATABASE_URL`.

```powershell
# Check if .env file exists
Test-Path .\.env

# Verify DATABASE_URL is set
Get-Content .\.env
```

### Issue: `Connection refused` or `cannot connect to the database`

**Solution:** Ensure PostgreSQL is running:

```powershell
# If using Docker
docker ps  # Check if container is running

# If container is stopped, restart it
docker compose up -d
```

### Issue: `ModuleNotFoundError: No module named 'app'`

**Solution:** Ensure you're running the command from the task3 directory:

```powershell
cd "C:\Users\rubin\OneDrive\Desktop\AI fellow\week2\task3"
python -m uvicorn app.main:app --reload
```

### Issue: Port 8000 is already in use

**Solution:** Either kill the existing process or use a different port:

```powershell
# Use a different port
python -m uvicorn app.main:app --reload --port 8001
```

## Development

### Watch for Changes

With the `--reload` flag, the server automatically restarts when you modify files:

```powershell
python -m uvicorn app.main:app --reload
```

### View Application Logs

Logs are displayed in the terminal and show:
- Request start/completion
- Database operations
- Timing information for concurrent requests

### Testing Endpoints

Use the Swagger UI at `/docs` to test endpoints, or use curl/PowerShell:

```powershell
# Test individual endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:8000/customers/count"

# Test aggregated endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:8000/overall_counts"
```

## Stopping the Application

Press `CTRL+C` in the terminal to stop the application.

To stop the Docker container:

```powershell
docker compose down
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/mydb` |

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AsyncPG Documentation](https://magicstack.github.io/asyncpg/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)


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
