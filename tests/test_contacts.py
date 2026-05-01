def get_token(client):
    client.post("/auth/register", json={
        "username": "test",
        "email": "test@test.com",
        "password": "123456"
    })

    res = client.post("/auth/login", json={
        "email": "test@test.com",
        "password": "123456"
    })

    return res.json()["access_token"]


def test_create_contact(client):
    token = get_token(client)

    response = client.post(
        "/contacts/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@test.com",
            "phone": "123456789",
            "birthday": "2000-01-01"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_get_contacts(client):
    token = get_token(client)

    response = client.get(
        "/contacts/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200