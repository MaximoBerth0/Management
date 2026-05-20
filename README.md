# Management API

A modular, async backend built with **FastAPI**, focused on **backoffice systems for businesses and companies**.

Designed to support real-world business workflows such as user management, roles and permissions, inventory, orders, and internal operations, following a **clean layered architecture** with a strong separation of concerns.

The project is infrastructure-ready, with support for **Docker**, **PostgreSQL**, and **Redis**, and is developed incrementally with new modules added over time.


---

## Architecture

The project follows a modular, layered, and decoupled architecture:

- **Schemas**: data validation and serialization (Pydantic)
- **Models**: ORM models (SQLAlchemy 2.0)
- **Repositories**: data access layer
- **Services**: business logic
- **Routers**: HTTP endpoints (FastAPI)

Each module is isolated and designed for long-term scalability.

---

## Key characteristics

- Async-first architecture
- SQLAlchemy 2.0 (typed, async ORM)
- Testing (pytest) with sqlite-in-memory
- Modular structure for incremental growth
- Docker-based development environment
- PostgreSQL as primary datastore
- Redis for background jobs and caching

---

## Main modules

### Authentication & Authorization
- Login / logout
- Refresh tokens
- Password hashing and verification
- JWT-based authentication
- Role-based access control (RBAC)

### Users
- User creation and management
- Enable / disable accounts
- Admin-level operations
- Profile updates

### Inventory
- Product and category management
- Stock tracking and adjustments
- Stock movement history (audit)
- Warehouse / location support
- RBAC-controlled operations

### Planned modules
- Orders & logistics
- Human resources
- Reporting & exports

---

## Tech stack

- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic
- Pydantic v2
- python-jose (JWT)
- Passlib (argon2)
- Pytest
- Docker & Docker Compose

---

## Installation & setup (recommended: Docker)

### Prerequisites
- Docker
- Docker Compose

### Clone the repository
```bash
git clone https://github.com/your-username/Management.git
cd Management
```
### Environment variables
#### env example: 
```bash
# application
APP_NAME=Management
ENV=local
DEBUG=true

# database
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/management_db

# Connection pool 
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_ECHO=false

# security and authentication
SECRET_KEY=your-secret-key-here-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_HASH_SCHEME=argon2

# server
UVICORN_WORKERS=1
GUNICORN_WORKERS=2

```
### Run the application
```bash
docker compose up --build
```

### Run bootstrap (to initialize system data such as 'permissions' and 'roles')
```bash
docker compose exec api python -m app.bootstraps.seed_all
```
#### The API will be available at:
```bash
http://localhost:8000
```
#### Swagger UI:
```bash
http://localhost:8000/docs
```

### Local development (optional, without Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```
- Note: when running locally, you must provide your own PostgreSQL and Redis instances.
