from sqlalchemy.orm import declarative_base

Base = declarative_base()



"""
- Configure connection pooling (pool_size, pool_pre_ping, etc.)
- Fix exception handler to use exc.status_code
- Add Alembic for migrations
- Add health check endpoint
- Add graceful shutdown (engine.dispose())
- Validate environment variables
- Configure logging (no echo=True in prod)
"""