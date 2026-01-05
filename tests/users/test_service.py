from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate
from app.users.service import UserService


def test_create_user(db_session):
    repo = UserRepository(db_session)    
    service = UserService(user_repo=repo)

    data = UserCreate( 
        email="maximo1@gmail.com",
        username="maximobth01",
        password="password12345"
    )

    user = service.create_user(data)

    assert user is not None
    assert isinstance(user, User)

