async def _create_category(client, admin_user, auth_headers, name, description="cat"):
    """helper: create a category and return its id"""
    response = await client.post(
        "/inventory/categories",
        headers=auth_headers(admin_user),
        json={"name": name, "description": description},
    )
    assert response.status_code == 200
    return response.json()["id"]

async def _create_product(client, admin_user, auth_headers, name, sku, category_id):
    """helper: create a product and return its id"""
    response = await client.post(
        "/inventory/products",
        headers=auth_headers(admin_user),
        json={"name": name, "sku": sku, "category_id": category_id},
    )
    assert response.status_code == 201
    return response.json()["id"]

# GET inventory/products/{id}


async def test_get_product(client, admin_user, auth_headers):
    category_id = await _create_category(client, admin_user, auth_headers, "tools")
    product_id = await _create_product(
        client, admin_user, auth_headers, "widget", "SKU-1", category_id
    )

    response = await client.get(
        f"/inventory/products/{product_id}",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200
    assert response.json()["id"] == product_id
