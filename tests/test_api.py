def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code in (200, 503)


def test_admin_login_and_me(client, admin_token):
    response = client.get("/api/v1/auth/me", headers=auth(admin_token))
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_create_list_and_analytics(client, admin_token):
    created = client.post("/api/v1/records", headers=auth(admin_token), json={
        "title": "API migration",
        "description": "Migrate reporting service",
        "status": "open",
        "priority": "high",
        "owner": "Platform"
    })
    assert created.status_code == 201, created.text
    record_id = created.json()["id"]

    listed = client.get("/api/v1/records?status=open&page=1&page_size=10",
                        headers=auth(admin_token))
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == record_id

    overview = client.get("/api/v1/analytics/overview", headers=auth(admin_token))
    assert overview.status_code == 200
    assert overview.json()["total_records"] == 1
    assert overview.json()["open_records"] == 1


def test_unauthenticated_records_are_rejected(client):
    response = client.get("/api/v1/records")
    assert response.status_code == 401


def test_admin_can_create_user(client, admin_token):
    response = client.post("/api/v1/users", headers=auth(admin_token), json={
        "email": "analyst@example.com",
        "full_name": "Test Analyst",
        "password": "VerySecure123!",
        "role": "analyst"
    })
    assert response.status_code == 201, response.text
    assert response.json()["role"] == "analyst"
