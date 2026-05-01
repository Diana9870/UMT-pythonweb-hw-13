def test_register(client):
    response = client.post("/auth/register", json={
        "username": "test",
        "email": "test@test.com",
        "password": "123456"
    })

    assert response.status_code == 200


def test_login(client):
    client.post("/auth/register", json={
        "username": "test",
        "email": "test@test.com",
        "password": "123456"
    })

    response = client.post("/auth/login", json={
        "email": "test@test.com",
        "password": "123456"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()