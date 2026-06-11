# POST inventory/categories 


async def test_create_category(client, admin_user, auth_headers):
    response = await client.post(
        "/inventory/categories",
        headers=auth_headers(admin_user),
        json={"name": "category", "description": "cateogry_description"}
    )

    assert response.status_code == 201
    body = response.json() 
    assert body["name"] == "category"
    assert body["description"] == "cateogry_description"


# create category forbidden 403 

async def test_create_category_forbidden(client, client_user, auth_headers): 
    response = await client.post(
        "/inventory/categories",
        headers=auth_headers(client_user),
        json={"name": "category", "description": "cateogry_description"}
    )

    assert response.status_code == 403

# create category duplicate name 409 conflict 
    
async def test_create_category_duplicate_name(client, admin_user, auth_headers):
    # create the category once
    response = await client.post(
        "/inventory/categories",
        headers=auth_headers(admin_user),
        json={"name": "category", "description": "cateogry_description"},
    )
    assert response.status_code == 201

    # creating another category with the same name conflicts
    response = await client.post(
        "/inventory/categories",
        headers=auth_headers(admin_user),
        json={"name": "category", "description": "another_description"},
    )
    assert response.status_code == 409


# DELETE inventory/categories/{id}


async def test_delete_category(client, admin_user, auth_headers):
    response = await client.post(
        "/inventory/categories",
        headers=auth_headers(admin_user),
        json={"name": "category", "description": "cateogry_description"},
    )
    assert response.status_code == 201
    category_id = response.json()["id"]

    response = await client.delete(
        f"/inventory/categories/{category_id}",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 204

# test delete category forbidden 403

async def test_delete_category_forbidden(client, admin_user, client_user, auth_headers):
    response = await client.post(
        "/inventory/categories",
        headers=auth_headers(admin_user),
        json={"name": "category", "description": "cateogry_description"},
    )
    assert response.status_code == 201
    category_id = response.json()["id"]

    response = await client.delete(
        f"/inventory/categories/{category_id}",
        headers=auth_headers(client_user),
    )
    assert response.status_code == 403

# test delete category not found 404

async def test_delete_category_not_found(client, admin_user, auth_headers):
    response = await client.delete(
        "/inventory/categories/999999",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 404
