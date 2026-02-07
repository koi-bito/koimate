@app.post("/api/reviews")
def add_review():
    d = request.json
    execute(
        "INSERT INTO reviews (user_id, product_id, rating, comment) VALUES (%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE rating=VALUES(rating), comment=VALUES(comment)",
        (d["user_id"], d["product_id"], d["rating"], d.get("comment")),
    )
    return jsonify({"ok": True})

@app.post("/api/purchases")
def add_purchase():
    d = request.json
    # price_at_purchase recorded for analysis
    execute(
        "INSERT INTO purchases (user_id, product_id, quantity, price_at_purchase) VALUES (%s,%s,%s,%s)",
        (d["user_id"], d["product_id"], d.get("quantity", 1), d["price_at_purchase"]),
    )
    return jsonify({"ok": True})

@app.post("/api/browse")
def add_browse():
    d = request.json
    execute(
        "INSERT INTO browsing_history (user_id, product_id, action) VALUES (%s,%s,%s)",
        (d["user_id"], d["product_id"], d.get("action", "view")),
    )
    return jsonify({"ok": True})
