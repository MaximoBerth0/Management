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


"""
validacion de input
errores de duplicacion

"""


