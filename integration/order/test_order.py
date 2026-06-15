# POST /orders

async def test_create_order(client, auth_headers, employee_user): 
    response = await client.post(
        "orders/",
        headers=auth_headers(employee_user)
    )
    
    assert response.status_code == 201 


async def test_create_order_forbidden(client, auth_headers, client_user): 
    response = await client.post(
        "orders/",
        headers=auth_headers(client_user)
    )
    
    assert response.status_code == 403


async def test_add_item_to_order(
    client, employee_user, auth_headers, make_order, make_product
):
    order_id = await make_order(employee_user)
    product_id = await make_product(employee_user)

    response = await client.post(
        f"/orders/{order_id}/items",
        headers=auth_headers(employee_user),
        json={"product_id": product_id, "quantity": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == order_id
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["product_id"] == product_id
    assert item["quantity"] == 3


async def test_add_item_to_order_forbidden(
    client, client_user, employee_user, auth_headers, make_order, make_product
):
    order_id = await make_order(employee_user)
    product_id = await make_product(employee_user)

    response = await client.post(
        f"/orders/{order_id}/items",
        headers=auth_headers(client_user),
        json={"product_id": product_id, "quantity": 3},
    )

    assert response.status_code == 403


async def test_add_item_to_order_product_not_found(
    client, employee_user, auth_headers, make_order
):
    order_id = await make_order(employee_user)

    response = await client.post(
        f"/orders/{order_id}/items",
        headers=auth_headers(employee_user),
        json={"product_id": 999999, "quantity": 3},
    )

    assert response.status_code == 404