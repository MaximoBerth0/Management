from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.users.models import User 
# Add all model imports

""" Alembic commands

# Create new migration (auto-detect changes)
alembic revision --autogenerate -m "Add posts table"

# Create empty migration (manual)
alembic revision -m "Add index"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
"""