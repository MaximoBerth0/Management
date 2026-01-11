def test_create_user_ok(db_session, client):
    payload = {
        "email": "testuser@gmail.com",
        "username": "testuser",
        "password": "password39r4f3"
    }

    response = client.post("/users/create", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "id" in data

def test_create_user_invalid_email(client):
    payload = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/users/create", json=payload)

    assert response.status_code == 422

def test_create_user_short_password(client):
    payload = {
        "email": "emailshort@gmail.com",
        "username": "testuser",
        "password": "123"
    }

    response = client.post("/users/create", json=payload)

    assert response.status_code == 422

def test_create_user_duplicate_email(client):
    payload = {
        "email": "dup@gmail.com",
        "username": "dup12",
        "password": "password123"
    }

    r1 = client.post("/users/create", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/users/create", json=payload)
    assert r2.status_code in (400, 409)

    data = r2.json()
    assert "email" in data["detail"].lower()

def test_create_user_password_not_returned(client):
    payload = {
        "email": "nopass@gmail.com",
        "username": "nopass",
        "password": "password123"
    }

    response = client.post("/users/create", json=payload)
    data = response.json()

    assert "password" not in data
    assert "hashed_password" not in data


