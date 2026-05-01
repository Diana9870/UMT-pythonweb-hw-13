def test_register(client):
    res = client.post(
        "/auth/register",
        params={"email": "test@test.com", "password": "123456"}
    )
    assert res.status_code in [200, 201]


def test_login(client):
    client.post(
        "/auth/register",
        params={"email": "test@test.com", "password": "123456"}
    )

    res = client.post(
        "/auth/login",
        params={"email": "test@test.com", "password": "123456"}
    )

    assert res.status_code == 200
    assert "access_token" in res.json()