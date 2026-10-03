"""Tests for /api/recommend blueprint (routes/recommender.py).

The recommender is a POST endpoint with optional JWT.
It requires products in the DB so the TF-IDF/KNN pipeline can fit.
"""


class TestRecommender:
    def test_recommend_returns_list(self, client, auth_headers, seeded_products):
        """POST /api/recommend/ + auth → 200, 'recommendations' is a list."""
        res = client.post("/api/recommend/", json={
            "purchases": "electronics gadget",
            "needs": "device",
            "shortages": "",
        }, headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_recommend_without_auth(self, client, seeded_products, db_session):
        """POST /api/recommend/ without JWT → still works (jwt optional), 200."""
        res = client.post("/api/recommend/", json={
            "purchases": "electronics",
            "needs": "",
            "shortages": "",
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "recommendations" in data

    def test_recommend_with_seeded_data(self, client, auth_headers, seeded_products):
        """With seeded products, recommendation list should be non-empty."""
        res = client.post("/api/recommend/", json={
            "purchases": "product electronics gadget",
            "needs": "device",
            "shortages": "",
        }, headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["recommendations"]) > 0

    def test_recommend_response_shape(self, client, auth_headers, seeded_products):
        """Each recommendation has id, name, category, price fields."""
        res = client.post("/api/recommend/", json={
            "purchases": "electronics gadget",
            "needs": "device",
            "shortages": "",
        }, headers=auth_headers)
        assert res.status_code == 200
        recs = res.get_json()["recommendations"]
        assert len(recs) > 0
        for rec in recs:
            assert "id" in rec
            assert "name" in rec
            assert "category" in rec
            assert "price" in rec

    def test_recommend_empty_query(self, client, auth_headers, db_session):
        """All empty strings → 400 (nothing to recommend from)."""
        res = client.post("/api/recommend/", json={
            "purchases": "",
            "needs": "",
            "shortages": "",
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_recommend_missing_json(self, client, auth_headers, db_session):
        """No JSON body → 400 or 415."""
        res = client.post("/api/recommend/",
                          data="not json",
                          content_type="text/plain",
                          headers=auth_headers)
        assert res.status_code in (400, 415)
