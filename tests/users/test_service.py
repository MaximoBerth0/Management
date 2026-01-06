import pytest
from app.shared.exceptions import UserAlreadyExists
from app.users.repository import UserRepository
from app.users.schemas import UserCreate
from app.users.service import UserService


def test_create_user(db_session):
    repo = UserRepository(db_session)    
    service = UserService(user_repo=repo)

    data = UserCreate( 
        email="newuser34@gmail.com",
        username="usernew38483",
        password="password12345"
    )

    user = service.create_user(data)

    assert user is not None
    assert user.id is not None
    assert user.email == data.email
    assert user.username == data.username


def test_user_is_persisted_db(db_session):
    repo = UserRepository(db_session)    
    service = UserService(user_repo=repo)

    data = UserCreate( 
        email="userpersist@gmail.com",
        username="userpersisted",
        password="password3948c"
    )

    service.create_user(data)

    db_user = repo.get_by_email(data.email)
    assert db_user is not None

def test_user_default(db_session): 
    repo = UserRepository(db_session)    
    service = UserService(user_repo=repo)

    data = UserCreate( 
        email="userdefault@gmail.com",
        username="userdefault",
        password="password35k4"
    )

    user = service.create_user(data)

    assert user.is_active is True
    assert user.is_superuser is False

def test_not_duplicate_email(db_session):
    repo = UserRepository(db_session)    
    service = UserService(user_repo=repo)

    data = UserCreate( 
        email="userdefault@gmail.com",
        username="userdefault",
        password="password35k4"
    )

    service.create_user(data)

    with pytest.raises(UserAlreadyExists):
        service.create_user(data)



def test_hash_password(db_session):
    repo = UserRepository(db_session)    
    service = UserService(user_repo=repo)

    data = UserCreate( 
        email="hashpassword@gmail.com",
        username="passwordhashed",
        password="password2847hd"
    )

    user = service.create_user(data)

    assert user.hashed_password != data.password
    assert user.hashed_password.startswith("$2")