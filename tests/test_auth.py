import pytest
from app.users.service import UserService
from app.users.schemas.command import CreateUserCommand
from app.auth.service import AuthService
from app.users.repository import UserRepository
from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.auth.repositories.password_reset import PasswordResetTokenRepository
from app.mail.mailer import Mailer


@pytest.mark.anyio
async def test_login_success(db_session):
    user_repo = UserRepository(db_session)
    refresh_repo = RefreshTokenRepository(db_session)
    reset_repo = PasswordResetTokenRepository(db_session)

    mailer = Mailer()

    auth_service = AuthService(
        user_repo=user_repo,
        refresh_repo=refresh_repo,
        reset_repo=reset_repo,
        mailer=mailer,
    )

    user_service = UserService(db_session)

    create_data = CreateUserCommand(
        email="test@example.com",
        username="testuser",
        password="123456",
    )

    await user_service.register_user(create_data)

    result = await auth_service.login(
        email="test@example.com",
        password="123456",
    )

    assert result["access_token"] is not None
    assert result["refresh_token"] is not None
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_rotation(client, db_session):

    await client.post(
        "/users/register",
        json={
            "email": "test@test.com",
            "username": "testuser",
            "password": "fj8f835jfefue9df"
        }
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "test@test.com",
            "password": "fj8f835jfefue9df"
        }
    )

    assert login_response.status_code == 200
    tokens = login_response.json()

    refresh_token_1 = tokens["refresh_token"]

    refresh_response = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token_1}
    )

    assert refresh_response.status_code == 200, refresh_response.json()

    new_tokens = refresh_response.json()
    refresh_token_2 = new_tokens["refresh_token"]

    assert refresh_token_1 != refresh_token_2



