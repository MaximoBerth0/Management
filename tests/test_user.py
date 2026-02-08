import pytest
from app.users.service import UserService


@pytest.mark.anyio
async def test_create_user_success(db_session):
    service = UserService(db_session)

    data = UserCreateCommand(
        email="test@example.com",
        username="testuser",
        password="123456",
    )

    user = await service.register_user(data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_active is True
