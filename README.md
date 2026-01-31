# Management API

A modular, async backend built with **FastAPI** for business management systems.

Designed with a **clean layered architecture**, strong separation of concerns, and
infrastructure-ready configuration (Docker, PostgreSQL, Redis).

The project is under active development, with modules added incrementally.

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
- Clear separation: schemas, models, repositories, services, routers
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
- Redis
- Alembic
- Pydantic v2
- python-jose (JWT)
- Passlib (argon2)
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
#### .env example: 
```bash
APP_NAME=Management
ENV=local
DEBUG=true

DATABASE_URL=postgresql+asyncpg://management:management@db:5432/management

JWT_PRIVATE_KEY=dev-private
JWT_PUBLIC_KEY=dev-public

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

CORS_ALLOW_ORIGINS=http://localhost:3000
```
### Run the application
```bash
docker compose up --build
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
