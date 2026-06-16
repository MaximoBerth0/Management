# PATCH orders/{order.id}/confirm

async def test_confirm_order(
    client, auth_headers, admin_user, employee_user, make_stock, make_order
):
    # admin seeds infra (employee lacks location:create / stock:create):
    stock = await make_stock(admin_user, quantity=10)
    product_id = stock["product_id"]
    location_id = stock["location_id"]

    order_id = await make_order(employee_user)
    await client.post(
        f"/orders/{order_id}/items",
        headers=auth_headers(employee_user),
        json={"product_id": product_id, "quantity": 3},
    )

    response = await client.patch(
        f"/orders/{order_id}/confirm",
        headers=auth_headers(employee_user, location_id=location_id),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


async def test_confirm_order_forbidden(
    client, auth_headers, admin_user, employee_user, client_user, make_stock, make_order
):
    stock = await make_stock(admin_user, quantity=10)
    product_id = stock["product_id"]
    location_id = stock["location_id"]

    order_id = await make_order(employee_user)
    await client.post(
        f"/orders/{order_id}/items",
        headers=auth_headers(employee_user),
        json={"product_id": product_id, "quantity": 3},
    )

    response = await client.patch(
        f"/orders/{order_id}/confirm",
        headers=auth_headers(client_user, location_id=location_id),
    )

    assert response.status_code == 403


async def test_confirm_order_insufficient_stock(
    client, auth_headers, admin_user, employee_user, make_stock, make_order
):
    # only 2 in stock, but the order asks for 5 > reserve raises InsufficientStock
    stock = await make_stock(admin_user, quantity=2)
    product_id = stock["product_id"]
    location_id = stock["location_id"]

    order_id = await make_order(employee_user)
    await client.post(
        f"/orders/{order_id}/items",
        headers=auth_headers(employee_user),
        json={"product_id": product_id, "quantity": 5},
    )

    response = await client.patch(
        f"/orders/{order_id}/confirm",
        headers=auth_headers(employee_user, location_id=location_id),
    )

    assert response.status_code == 409


async def test_confirm_order_no_stock_at_location(
    client, auth_headers, admin_user, employee_user, make_stock, make_location, make_order
):
    # stock exists at one location, but we confirm against another that has none
    stock = await make_stock(admin_user, quantity=10)
    product_id = stock["product_id"]
    other_location_id = await make_location(admin_user, name="depot", city="gotham")

    order_id = await make_order(employee_user)
    await client.post(
        f"/orders/{order_id}/items",
        headers=auth_headers(employee_user),
        json={"product_id": product_id, "quantity": 3},
    )

    response = await client.patch(
        f"/orders/{order_id}/confirm",
        headers=auth_headers(employee_user, location_id=other_location_id),
    )

    assert response.status_code == 404