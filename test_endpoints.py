"""
End-to-end integration test for all new endpoints.
Requires the Flask server to be running on http://127.0.0.1:5000
"""
import requests
import sys

BASE = "http://127.0.0.1:5000"
PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  →  {detail}")

def auth_header(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# ── Get JWT token ──
print("\n🔑 Auth")
r = requests.post(f"{BASE}/api/auth/login", json={"username": "alice", "password": "password123"})
test("POST /api/auth/login → 200", r.status_code == 200, f"status={r.status_code}")
token = r.json().get("access_token", "")
test("Token received", bool(token), "empty token")

headers = auth_header(token)

# ── Reviews: POST new ──
print("\n📝 Reviews — POST")
r = requests.post(f"{BASE}/api/reviews/", json={
    "product_id": 1, "rating": 5, "review_text": "Test review from integration test"
}, headers=headers)
test("POST /api/reviews/ → 200 or 201", r.status_code in (200, 201), f"status={r.status_code} body={r.text}")

# ── Reviews: POST update (same user+product → should upsert) ──
r = requests.post(f"{BASE}/api/reviews/", json={
    "product_id": 1, "rating": 3, "review_text": "Updated review"
}, headers=headers)
test("POST /api/reviews/ upsert → 200", r.status_code == 200, f"status={r.status_code} body={r.text}")

# ── Reviews: POST validation (rating=0) ──
r = requests.post(f"{BASE}/api/reviews/", json={
    "product_id": 1, "rating": 0
}, headers=headers)
test("POST /api/reviews/ rating=0 → 400", r.status_code == 400, f"status={r.status_code}")

# ── Reviews: POST validation (rating=6) ──
r = requests.post(f"{BASE}/api/reviews/", json={
    "product_id": 1, "rating": 6
}, headers=headers)
test("POST /api/reviews/ rating=6 → 400", r.status_code == 400, f"status={r.status_code}")

# ── Reviews: POST missing product ──
r = requests.post(f"{BASE}/api/reviews/", json={
    "product_id": 9999, "rating": 4
}, headers=headers)
test("POST /api/reviews/ bad product → 404", r.status_code == 404, f"status={r.status_code}")

# ── Reviews: POST without auth ──
r = requests.post(f"{BASE}/api/reviews/", json={
    "product_id": 1, "rating": 4
})
test("POST /api/reviews/ no auth → 401", r.status_code == 401, f"status={r.status_code}")

# ── Reviews: GET by product (public) ──
print("\n📖 Reviews — GET by product")
r = requests.get(f"{BASE}/api/reviews/1")
test("GET /api/reviews/1 → 200", r.status_code == 200, f"status={r.status_code}")
data = r.json()
test("Response has 'reviews' key", "reviews" in data, f"keys={list(data.keys())}")
if "reviews" in data:
    test("Reviews list is non-empty", len(data["reviews"]) > 0, "empty list")
    if data["reviews"]:
        rev = data["reviews"][0]
        test("Review has expected fields", all(k in rev for k in ("id", "user_id", "product_id", "rating", "review_text", "created_at")),
             f"keys={list(rev.keys())}")

# ── Reviews: GET /my ──
print("\n👤 Reviews — GET /my")
r = requests.get(f"{BASE}/api/reviews/my", headers=headers)
test("GET /api/reviews/my → 200", r.status_code == 200, f"status={r.status_code}")
data = r.json()
test("Response has 'reviews' key", "reviews" in data, f"keys={list(data.keys())}")
if "reviews" in data and data["reviews"]:
    rev = data["reviews"][0]
    test("My review has product_name", "product_name" in rev, f"keys={list(rev.keys())}")

# ── Reviews: GET /my without auth ──
r = requests.get(f"{BASE}/api/reviews/my")
test("GET /api/reviews/my no auth → 401", r.status_code == 401, f"status={r.status_code}")

# ── Recommendations (still work after re-ranking change) ──
print("\n🤖 Recommendations")
r = requests.post(f"{BASE}/api/recommend/", json={
    "purchases": "laptop keyboard",
    "needs": "electronics",
    "shortages": ""
}, headers=headers)
test("POST /api/recommend/ → 200", r.status_code == 200, f"status={r.status_code}")
data = r.json()
test("Has 'recommendations' key", "recommendations" in data, f"keys={list(data.keys())}")
if "recommendations" in data:
    test("Recommendations list is non-empty", len(data["recommendations"]) > 0, "empty list")
    if data["recommendations"]:
        rec = data["recommendations"][0]
        test("Recommendation has expected fields", all(k in rec for k in ("id", "name", "category", "price")),
             f"keys={list(rec.keys())}")

# ── Analytics: existing /data endpoint ──
print("\n📊 Analytics — /data")
r = requests.get(f"{BASE}/api/analytics/data")
test("GET /api/analytics/data → 200", r.status_code == 200, f"status={r.status_code}")
data = r.json()
test("Has categories/timeline/actions", all(k in data for k in ("categories", "timeline", "actions")),
     f"keys={list(data.keys())}")

# ── Analytics: new /dashboard endpoint ──
print("\n📊 Analytics — /dashboard")
r = requests.get(f"{BASE}/api/analytics/dashboard", headers=headers)
test("GET /api/analytics/dashboard → 200", r.status_code == 200, f"status={r.status_code} body={r.text[:200]}")
data = r.json()
test("Has top_products key", "top_products" in data, f"keys={list(data.keys())}")
test("Has avg_ratings key", "avg_ratings" in data, f"keys={list(data.keys())}")
test("Has interaction_trend key", "interaction_trend" in data, f"keys={list(data.keys())}")

if "top_products" in data:
    test("top_products is non-empty", len(data["top_products"]) > 0, "empty list")
    if data["top_products"]:
        tp = data["top_products"][0]
        test("top_product has expected fields",
             all(k in tp for k in ("product_id", "name", "view_count", "cart_count", "purchase_count")),
             f"keys={list(tp.keys())}")

if "avg_ratings" in data:
    test("avg_ratings is non-empty", len(data["avg_ratings"]) > 0, "empty list")
    if data["avg_ratings"]:
        ar = data["avg_ratings"][0]
        test("avg_rating has expected fields",
             all(k in ar for k in ("product_id", "name", "avg_rating", "review_count")),
             f"keys={list(ar.keys())}")

if "interaction_trend" in data:
    test("interaction_trend is non-empty", len(data["interaction_trend"]) > 0, "empty list")
    if data["interaction_trend"]:
        it = data["interaction_trend"][0]
        test("trend entry has expected fields",
             all(k in it for k in ("date", "views", "purchases")),
             f"keys={list(it.keys())}")

# ── Analytics: /dashboard without auth ──
r = requests.get(f"{BASE}/api/analytics/dashboard")
test("GET /api/analytics/dashboard no auth → 401", r.status_code == 401, f"status={r.status_code}")

# ── Page routes ──
print("\n🌐 Page Routes")
r = requests.get(f"{BASE}/")
test("GET / → 200", r.status_code == 200, f"status={r.status_code}")

r = requests.get(f"{BASE}/dashboard")
test("GET /dashboard → 200", r.status_code == 200, f"status={r.status_code}")
test("/dashboard contains Chart.js canvases", "topProductsChart" in r.text and "avgRatingsChart" in r.text and "trendChart" in r.text,
     "missing chart canvases")

r = requests.get(f"{BASE}/login")
test("GET /login → 200", r.status_code == 200, f"status={r.status_code}")

# ── Summary ──
print(f"\n{'='*50}")
print(f"  Results: {PASS} passed, {FAIL} failed")
print(f"{'='*50}")
sys.exit(1 if FAIL else 0)
