"""Tests for /api/track blueprint (routes/tracking.py).

Key detail: tracking uses jwt_required(optional=True), so unauthenticated
requests return 200 (behavior not tracked), NOT 401.
"""


class TestTracking:
    def test_track_view(self, client, auth_headers, seeded_products):
        """POST /api/track/ with action_type='view' + auth → 201."""
        res = client.post("/api/track/", json={
            "product_id": 1,
            "action_type": "view",
        }, headers=auth_headers)
        assert res.status_code == 201

    def test_track_cart(self, client, auth_headers, seeded_products):
        """POST /api/track/ with action_type='add_to_cart' + auth → 201."""
        res = client.post("/api/track/", json={
            "product_id": 1,
            "action_type": "add_to_cart",
        }, headers=auth_headers)
        assert res.status_code == 201

    def test_track_purchase(self, client, auth_headers, seeded_products):
        """POST /api/track/ with action_type='purchase' + auth → 201."""
        res = client.post("/api/track/", json={
            "product_id": 1,
            "action_type": "purchase",
        }, headers=auth_headers)
        assert res.status_code == 201

    def test_track_without_auth(self, client, seeded_products, db_session):
        """No JWT → 200 (behavior not tracked, since jwt_required is optional)."""
        res = client.post("/api/track/", json={
            "product_id": 1,
            "action_type": "view",
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "not authenticated" in data["msg"].lower()

    def test_track_missing_product_id(self, client, auth_headers, db_session):
        """Missing product_id → 400."""
        res = client.post("/api/track/", json={
            "action_type": "view",
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_track_missing_action_type(self, client, auth_headers, db_session):
        """Missing action_type → 400."""
        res = client.post("/api/track/", json={
            "product_id": 1,
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_track_missing_json_body(self, client, auth_headers, db_session):
        """Empty/non-JSON request body → 400 or 415."""
        res = client.post("/api/track/",
                          data="not json",
                          content_type="text/plain",
                          headers=auth_headers)
        assert res.status_code in (400, 415)
