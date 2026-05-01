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


def test_me(client):
    token = get_token(client)

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200