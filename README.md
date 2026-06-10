# Management API

Inventory management system for orders, reservations, authentication, and role-permission for administrators, employees, and customers. Focused on back-office systems for businesses and companies.

---

### [future images]

--- 

## Overview

Managing inventory, orders, and reservations across disconnected tools leads to stock inconsistencies, fulfillment errors, and poor visibility. As operations scale, these problems compound fast.

**Management API** provides a centralized back-office backend that handles the full lifecycle of inventory and orders in a single system, keeping stock levels, reservations, and order states consistent at all times. Access is governed by a role-based model with three distinct roles — administrators, employees, and customers — ensuring each actor can only do what their role allows.

Built on FastAPI with a fully async stack (asyncpg + SQLAlchemy), it's designed for reliability and performance as your business grows.

---

## Tech stack

- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic
- Pydantic v2
- PyJWT
- Argon2-CFFI
- Pytest
- Docker & Docker Compose

---

## Technical Features

- Async-first architecture
- SQLAlchemy 2.0 (typed, async ORM)
- JWT authentication with token rotation
- Email-based password reset flow
- Role-based access control with configurable roles and permissions via constants
- Integration testing (pytest) with SQLite in-memory
- Modular structure for incremental growth
- Docker-based development environment
- PostgreSQL as primary datastore

### Deployment on Amazon Web Services


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
