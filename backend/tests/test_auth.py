import pytest
from app.services.auth_service import hash_password
from app.models.user import User


async def _create_test_user(db_session, email="test@test.com", password="test123"):
    user = User(
        email=email,
        username=email.split("@")[0],
        full_name="Test User",
        password_hash=hash_password(password),
        role="investigator",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    await _create_test_user(db_session)

    response = await client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "test123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@test.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session):
    await _create_test_user(db_session)

    response = await client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "test123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/api/auth/register", json={
        "email": "newuser@test.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "securepass123",
        "role": "investigator",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"
    assert data["role"] == "investigator"
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_get_me_authenticated(client, db_session):
    await _create_test_user(db_session)

    login_resp = await client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "test123",
    })
    token = login_resp.json()["access_token"]

    response = await client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client):
    response = await client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid.token.here",
    })
    assert response.status_code == 401
