# This will be modified





import pytest
from app.core.security.passwords import hash_password
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.rbac.models import Permission, Role, RolePermission, UserRole
from app.users.models import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()

@pytest.fixture
def user_factory(db_session):
    def create_user(*, password="password123", permissions=None):
        user = User(
            email="test@example.com",
            username="testuser1",
            hashed_password=hash_password(password),
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

        if permissions:
            role = Role(name="test-role")
            db_session.add(role)
            db_session.flush()

            for perm in permissions:
                p = Permission(name=perm)
                db_session.add(p)
                db_session.flush()
                db_session.add(RolePermission(role_id=role.id, permission_id=p.id))

            db_session.add(UserRole(user_id=user.id, role_id=role.id))

        db_session.commit()
        db_session.refresh(user)

        user._plain_password = password
        return user

    return create_user

