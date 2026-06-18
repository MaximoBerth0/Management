# The app/containers use host `db` (see .env) from the host using localhost.
LOCAL_DATABASE_URL := postgresql+asyncpg://postgres:postgres@localhost:5432/management

# Run alembic with the local URL injected.
ALEMBIC := DATABASE_URL=$(LOCAL_DATABASE_URL) alembic

.PHONY: db-up db-stop db-down db-reset migrate revision current heads

db-up:        ## Start the database in the background
	docker compose up -d db

db-stop:      ## Stop the database (keeps data)
	docker compose stop db

db-down:      ## Remove containers (keeps data volume)
	docker compose down

db-reset:     ## Remove containers AND wipe the data volume
	docker compose down -v

## Migrations (require the db to be running)
migrate:      ## Apply all pending migrations
	$(ALEMBIC) upgrade head

revision:     ## Autogenerate a migration: make revision m="your message"
	$(ALEMBIC) revision --autogenerate -m "$(m)"

current:      ## Show the DB's current revision
	$(ALEMBIC) current

heads:        ## Show the latest migration file revision
	$(ALEMBIC) heads
