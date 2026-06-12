"""
the stock file test evaluates the following:

- Happy path      - normal expected behavior
- Validation      - bad input, missing fields
- Auth/Permission - unauthorized, forbidden
- Edge cases      - duplicates, not found, etc.

Initializing stock needs both a product and a location, so these tests lean on
the shared entity builders from integration/conftest.py instead of redefining
helpers here:
- `make_product`  : create a product (auto-creates its category) -> product id
- `make_location` : create a location -> location id

Other fixtures from integration/conftest.py:
- `admin_user`    : user with the admin role (all permissions)
- `employee_user` : user with the employee role (no `stock:create`)
- `client_user`   : user with the client role (no permissions)
- `auth_headers`  : builds the Authorization header for a user

Note: the create-stock endpoint lives at POST /inventory/new.
"""

# POST /inventory/new  (initialize stock)


async def test_create_stock(client, admin_user, auth_headers, make_product, make_location):
    product_id = await make_product(admin_user)
    location_id = await make_location(admin_user)

    response = await client.post(
        "/inventory/new",
        headers=auth_headers(admin_user),
        json={
            "location_id": location_id,
            "product_id": product_id,
            "quantity": 10,
            "reorder_point": 2,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["location_id"] == location_id
    assert body["product_id"] == product_id
    assert body["quantity"] == 10
    assert body["reorder_point"] == 2


async def test_create_stock_reorder_point_capped(
    client, admin_user, auth_headers, make_product, make_location
):
    # service caps reorder_point at the initial quantity
    product_id = await make_product(admin_user)
    location_id = await make_location(admin_user)

    response = await client.post(
        "/inventory/new",
        headers=auth_headers(admin_user),
        json={
            "location_id": location_id,
            "product_id": product_id,
            "quantity": 5,
            "reorder_point": 99,
        },
    )
    assert response.status_code == 201
    assert response.json()["reorder_point"] == 5


async def test_create_stock_forbidden_client(client, client_user, auth_headers):
    response = await client.post(
        "/inventory/new",
        headers=auth_headers(client_user),
        json={"location_id": 1, "product_id": 1, "quantity": 10, "reorder_point": 2},
    )
    assert response.status_code == 403


async def test_create_stock_forbidden_employee(client, employee_user, auth_headers):
    # employees can move stock (in/out/adjust) but cannot initialize it
    response = await client.post(
        "/inventory/new",
        headers=auth_headers(employee_user),
        json={"location_id": 1, "product_id": 1, "quantity": 10, "reorder_point": 2},
    )
    assert response.status_code == 403


async def test_create_stock_missing_field(client, admin_user, auth_headers):
    # quantity omitted -> schema validation (422)
    response = await client.post(
        "/inventory/new",
        headers=auth_headers(admin_user),
        json={"location_id": 1, "product_id": 1, "reorder_point": 2},
    )
    assert response.status_code == 422


async def test_create_stock_invalid_location(
    client, admin_user, auth_headers, make_product
):
    product_id = await make_product(admin_user)

    response = await client.post(
        "/inventory/new",
        headers=auth_headers(admin_user),
        json={
            "location_id": 999999,
            "product_id": product_id,
            "quantity": 10,
            "reorder_point": 2,
        },
    )
    assert response.status_code == 400


async def test_create_stock_zero_quantity(
    client, admin_user, auth_headers, make_product, make_location
):
    product_id = await make_product(admin_user)
    location_id = await make_location(admin_user)

    response = await client.post(
        "/inventory/new",
        headers=auth_headers(admin_user),
        json={
            "location_id": location_id,
            "product_id": product_id,
            "quantity": 0,
            "reorder_point": 0,
        },
    )
    assert response.status_code == 400
