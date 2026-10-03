"""Tests for /api/analytics blueprint (routes/analytics.py)."""


class TestAnalyticsData:
    def test_analytics_data_endpoint(self, client, db_session):
        """GET /api/analytics/data → 200 (public, no auth required)."""
        res = client.get("/api/analytics/data")
        assert res.status_code == 200

    def test_analytics_data_response_shape(self, client, db_session):
        """Response contains categories, timeline, actions keys."""
        res = client.get("/api/analytics/data")
        data = res.get_json()
        assert "categories" in data
        assert "timeline" in data
        assert "actions" in data


class TestDashboard:
    def test_dashboard_endpoint(self, client, auth_headers, db_session):
        """GET /api/analytics/dashboard + auth → 200."""
        res = client.get("/api/analytics/dashboard", headers=auth_headers)
        assert res.status_code == 200

    def test_dashboard_response_shape(self, client, auth_headers, db_session):
        """Response contains top_products, avg_ratings, interaction_trend."""
        res = client.get("/api/analytics/dashboard", headers=auth_headers)
        data = res.get_json()
        assert "top_products" in data
        assert "avg_ratings" in data
        assert "interaction_trend" in data

    def test_dashboard_without_auth(self, client, db_session):
        """GET /api/analytics/dashboard without JWT → 401."""
        res = client.get("/api/analytics/dashboard")
        assert res.status_code == 401

    def test_top_products_structure(self, client, auth_headers, seeded_products):
        """When data exists, top_products items have correct fields."""
        # Seed some behavior so top_products has data
        client.post("/api/track/", json={
            "product_id": 1,
            "action_type": "view",
        }, headers=auth_headers)
        client.post("/api/track/", json={
            "product_id": 1,
            "action_type": "purchase",
        }, headers=auth_headers)

        res = client.get("/api/analytics/dashboard", headers=auth_headers)
        data = res.get_json()
        assert len(data["top_products"]) > 0
        tp = data["top_products"][0]
        for key in ("product_id", "name", "view_count", "cart_count", "purchase_count"):
            assert key in tp

    def test_avg_ratings_structure(self, client, auth_headers, seeded_products):
        """When reviews exist, avg_ratings items have correct fields."""
        client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 4,
            "review_text": "Good for analytics test",
        }, headers=auth_headers)

        res = client.get("/api/analytics/dashboard", headers=auth_headers)
        data = res.get_json()
        assert len(data["avg_ratings"]) > 0
        ar = data["avg_ratings"][0]
        for key in ("product_id", "name", "avg_rating", "review_count"):
            assert key in ar

    def test_interaction_trend_structure(self, client, auth_headers, seeded_products):
        """When behavior exists, interaction_trend items have correct fields."""
        client.post("/api/track/", json={
            "product_id": 1,
            "action_type": "view",
        }, headers=auth_headers)

        res = client.get("/api/analytics/dashboard", headers=auth_headers)
        data = res.get_json()
        assert len(data["interaction_trend"]) > 0
        it = data["interaction_trend"][0]
        for key in ("date", "views", "purchases"):
            assert key in it
