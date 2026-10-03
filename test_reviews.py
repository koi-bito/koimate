"""Tests for /api/reviews blueprint (routes/reviews.py)."""


class TestSubmitReview:
    def test_submit_review(self, client, auth_headers, seeded_products):
        """POST /api/reviews/ with valid data → 201."""
        res = client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 4,
            "review_text": "Good product!",
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.get_json()
        assert "msg" in data

    def test_review_upsert(self, client, auth_headers, seeded_products):
        """Submit review for same product twice → second returns 200 (update)."""
        payload = {"product_id": 1, "rating": 5, "review_text": "Great!"}
        res1 = client.post("/api/reviews/", json=payload, headers=auth_headers)
        assert res1.status_code == 201

        updated = {"product_id": 1, "rating": 3, "review_text": "Updated review"}
        res2 = client.post("/api/reviews/", json=updated, headers=auth_headers)
        assert res2.status_code == 200

    def test_rating_too_high(self, client, auth_headers, seeded_products):
        """Rating 6 → 400."""
        res = client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 6,
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_rating_too_low(self, client, auth_headers, seeded_products):
        """Rating 0 → 400."""
        res = client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 0,
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_review_nonexistent_product(self, client, auth_headers, db_session):
        """Review for product_id=9999 (doesn't exist) → 404."""
        res = client.post("/api/reviews/", json={
            "product_id": 9999,
            "rating": 4,
        }, headers=auth_headers)
        assert res.status_code == 404

    def test_review_without_auth(self, client, seeded_products, db_session):
        """POST /api/reviews/ without JWT → 401."""
        res = client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 4,
        })
        assert res.status_code == 401


class TestGetReviews:
    def test_get_product_reviews(self, client, auth_headers, seeded_products):
        """GET /api/reviews/<product_id> (no auth needed) → 200, list."""
        # First submit a review
        client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 5,
            "review_text": "Excellent!",
        }, headers=auth_headers)

        res = client.get("/api/reviews/1")
        assert res.status_code == 200
        data = res.get_json()
        assert "reviews" in data
        assert isinstance(data["reviews"], list)
        assert len(data["reviews"]) > 0

    def test_product_review_fields(self, client, auth_headers, seeded_products):
        """Each review has expected fields."""
        client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 4,
            "review_text": "Nice product",
        }, headers=auth_headers)

        res = client.get("/api/reviews/1")
        review = res.get_json()["reviews"][0]
        for key in ("id", "user_id", "product_id", "rating", "review_text", "created_at"):
            assert key in review

    def test_get_my_reviews(self, client, auth_headers, seeded_products):
        """GET /api/reviews/my + auth → 200, only current user's reviews."""
        client.post("/api/reviews/", json={
            "product_id": 1,
            "rating": 5,
            "review_text": "My review",
        }, headers=auth_headers)

        res = client.get("/api/reviews/my", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert "reviews" in data
        assert len(data["reviews"]) > 0
        # my reviews include product_name
        assert "product_name" in data["reviews"][0]

    def test_get_my_reviews_without_auth(self, client, db_session):
        """GET /api/reviews/my without JWT → 401."""
        res = client.get("/api/reviews/my")
        assert res.status_code == 401

    def test_get_reviews_empty_product(self, client, seeded_products):
        """GET /api/reviews/<id> for product with no reviews → 200, empty list."""
        res = client.get("/api/reviews/2")
        assert res.status_code == 200
        data = res.get_json()
        assert data["reviews"] == []
