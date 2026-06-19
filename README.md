# Management API

Inventory management system for orders, reservations, authentication, and role-permission for administrators, employees, and customers. Focused on back-office systems for businesses and companies.

---

[future image]

--- 

## Overview

Managing inventory, orders, and reservations across disconnected tools leads to stock inconsistencies, fulfillment errors, and poor visibility. As operations scale, these problems compound fast.

**Management API** provides a centralized back-office backend that handles the full lifecycle of inventory and orders in a single system, keeping stock levels, reservations, and order states consistent at all times. Access is governed by a role-based model with three distinct roles — administrators, employees, and customers — ensuring each actor can only do what their role allows.

Built on FastAPI with a fully async stack (asyncpg + SQLAlchemy), it's designed for **reliability and performance** as your business grows.

It also keeps users informed through **email notifications**, including low-stock **alerts** so inventory is replenished before it runs out, and password reset links for secure account recovery.

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

The API runs as a container on **Amazon ECS** (Fargate), behind an Application Load Balancer. A few additional AWS services support it:

- **AWS Secrets Manager** — stores sensitive configuration (database URL, secret key, AWS credentials) and injects it into the ECS tasks at runtime, so no secrets live in the image or repository.
- **ECS Service Auto Scaling** — scales the number of running tasks up or down based on CPU/memory usage to handle changing load.
- **Amazon SES** — sends transactional email (low-stock alerts and password reset links).

---

## Architecture

The codebase is organized into self-contained feature modules under `app/`, each
following the same layered layout (router → service → repository → model). Shared
concerns (config, security, constants) live in `core/`, and the SQLAlchemy `Base`
plus session wiring live in `database/`.

```text
app/
├── main.py             # FastAPI application entry point
├── core/               # Shared application components
│   ├── config.py       # Application settings (Pydantic Settings)
│   ├── constants/      # Roles, permissions, and shared constants
│   └── security/       # Password hashing, JWT handling, security utilities
├── database/           # Database engine, session, Base, and ORM configuration
├── auth/               # Authentication and account security
│   └── repositories/
├── users/              # User management
├── rbac/               # Role-Based Access Control (roles and permissions)
│   ├── models/
│   └── repositories/
├── inventory/          # Inventory management (products, stock, locations, reservations)
│   ├── models/
│   ├── repositories/
│   ├── router.py
│   ├── service.py
│   └── schemas.py
├── orders/             # Order management and lifecycle
│   ├── models/
│   ├── repository.py
│   ├── router.py
│   ├── service.py
│   └── schemas.py
├── mail/               # Email delivery (AWS SES)
├── observability/      # Logging, monitoring, and application metrics
└── bootstraps/         # Database seed scripts (roles, permissions, initial data)
```

Supporting top-level directories:

```text
alembic/        # database migrations
docs/           # per-module documentation and screenshots
integration/    # pytest integration suite (conftest fixtures + tests)
```

---

## Installation & setup (recommended: Docker)

### Prerequisites
- Docker
- Docker Compose

### Clone the repository
```bash
git clone https://github.com/MaximoBerth0/Management.git
cd Management
```
### Environment variables
#### env example: 
```bash
# application
APP_NAME=Management
ENV=local
DEBUG=true
APP_BASE_URL=http://localhost:8000

# AWS (Secrets Manager / SES)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
SENDER_EMAIL=no-reply@yourdomain.com

# database
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/management_db

# Connection pool 
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_ECHO=false

# Connection timeouts
DB_CONNECT_TIMEOUT=10
DB_COMMAND_TIMEOUT=60
DB_STATEMENT_TIMEOUT=30000

# security and authentication
SECRET_KEY=your-secret-key-here-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# server
UVICORN_WORKERS=1
GUNICORN_WORKERS=2

# CORS
CORS_ALLOW_ORIGINS=["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true

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
- Note: when running locally, you must provide your own PostgreSQL instance and AWS services (or any other cloud provider)
