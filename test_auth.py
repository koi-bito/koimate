"""Tests for /api/auth blueprint (routes/auth.py)."""


class TestRegister:
    def test_register_success(self, client, db_session):
        """POST /api/auth/register with valid data → 201."""
        res = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "securepass123",
        })
        assert res.status_code == 201
        data = res.get_json()
        assert "msg" in data

    def test_register_duplicate_username(self, client, db_session):
        """Register same username twice → 400."""
        payload = {"username": "dupeuser", "password": "pass123"}
        client.post("/api/auth/register", json=payload)
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 400

    def test_register_missing_username(self, client, db_session):
        """Register without username → 400."""
        res = client.post("/api/auth/register", json={
            "password": "pass123",
        })
        assert res.status_code == 400

    def test_register_missing_password(self, client, db_session):
        """Register without password → 400."""
        res = client.post("/api/auth/register", json={
            "username": "nopassuser",
        })
        assert res.status_code == 400


class TestLogin:
    def test_login_success(self, client, db_session):
        """POST /api/auth/login with correct creds → 200 + access_token."""
        client.post("/api/auth/register", json={
            "username": "loginuser",
            "password": "mypassword",
        })
        res = client.post("/api/auth/login", json={
            "username": "loginuser",
            "password": "mypassword",
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "access_token" in data
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client, db_session):
        """Wrong password → 401."""
        client.post("/api/auth/register", json={
            "username": "wrongpwuser",
            "password": "correctpassword",
        })
        res = client.post("/api/auth/login", json={
            "username": "wrongpwuser",
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client, db_session):
        """Unknown username → 401."""
        res = client.post("/api/auth/login", json={
            "username": "ghost",
            "password": "doesntmatter",
        })
        assert res.status_code == 401


class TestProtectedRoutes:
    def test_protected_route_without_token(self, client, db_session):
        """Hit /api/auth/me without JWT header → 401."""
        res = client.get("/api/auth/me")
        assert res.status_code == 401

    def test_me_with_valid_token(self, client, auth_headers, db_session):
        """GET /api/auth/me with valid JWT → 200 and user info."""
        res = client.get("/api/auth/me", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["username"] == "testuser"
