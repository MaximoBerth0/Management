# Management API

Modular backend built with FastAPI for business management.
Includes authentication, users, roles and permissions, inventory, orders,
logistics, human resources, and reporting.

---

## Architecture

The project follows a modular, layered, and decoupled architecture:

- **Schemas**: data validation and serialization (Pydantic)
- **Models**: ORM models (SQLAlchemy)
- **Repository**: data access layer
- **Service**: business logic
- **Routers**: HTTP endpoints (FastAPI)

Each module is independent and designed to scale.

---

## Main Modules

### Authentication & Authorization
- Login / logout
- Refresh token
- Password change and recovery
- Roles and permissions (RBAC)

### Users
- User CRUD
- User profile
- Enable / disable accounts
- Admin-only endpoints

### Inventory
- Items and categories
- Stock movements
- Audit logs

### Orders & Logistics
- Order management
- Status handling and assignments
- Deliveries and tracking

### Human Resources
- Employees
- Schedules
- Vacations and performance

### Reports
- Sales
- Inventory
- Data export

---

## Technologies

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT (python-jose)
- Passlib (bcrypt)

---

## Installation

```bash
git clone https://github.com/your-username/Management.git
cd Management

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

Create a .env file with:
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=change-this
APP_NAME=change-this
#security:
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

Run the aplicacion:
uvicorn app.main:app --reload

---

This project is under active development.
The core structure for authentication, users, and permissions is in progress.
Additional modules will be implemented incrementally.
