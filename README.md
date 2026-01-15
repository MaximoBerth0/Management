`# Management API

A modular, async backend built with FastAPI for **business management systems**.
Designed with a layered architecture, clear separation of concerns, and scalability in mind.
The project is under active development, with modules added incrementally.

---

## Architecture

The project follows a modular, layered, and decoupled architecture:

- **Schemas**: data validation and serialization (Pydantic)
- **Models**: ORM models (SQLAlchemy)
- **Repository**: data access layer
- **Service**: business logic
- **Routers**: HTTP endpoints (FastAPI)

Each module is independent and designed to scale.


flowchart TD
    A[Client] --> B[Router]
    B --> C[Service]
    C --> D[Repository]
    D --> E[(Database)]

---

## Key Characteristics
- Async-first architecture
- SQLAlchemy 2.0 ORM (typed models)
- Clear separation: schemas, models, repositories, services, routers
- Modular structure for long-term scalability
- PostgreSQL as primary datastore

---

## Main Modules

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

### Planned modules
- Inventory
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

---

## Installation and setup
### Clone the repository
```bash
git clone https://github.com/your-username/Management.git
cd Management
```

### Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### install dependencies 
```bash
pip install -e .
```

### Environment variables
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

SECRET_KEY=change-this
APP_NAME=change-this

JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Running the application 
```bash
uvicorn app.main:app --reload
```