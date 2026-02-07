@app.get("/api/products")
def list_products():
    q = request.args.get("q", "").strip()
    brand = request.args.get("brand", "").strip()
    category = request.args.get("category", "").strip()
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if q:
        sql += " AND MATCH(name,brand,category,description) AGAINST(? IN NATURAL LANGUAGE MODE)"
        params.append(q)
    if brand:
        sql += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    if category:
        sql += " AND category LIKE ?"
        params.append(f"%{category}%")
    if min_price:
        sql += " AND price >= ?"
        params.append(float(min_price))
    if max_price:
        sql += " AND price <= ?"
        params.append(float(max_price))

    # mysql-connector uses %s, not ?, so normalize:
    sql = sql.replace("?", "%s")
    rows = query_all(sql, params)
    return jsonify(rows)

@app.get("/api/products/<int:pid>")
def product_detail(pid):
    product = query_one("SELECT * FROM products WHERE id=%s", (pid,))
    if not product:
        return jsonify({"error": "Not found"}), 404
    avg = query_one("SELECT AVG(rating) AS avg_rating, COUNT(*) AS cnt FROM reviews WHERE product_id=%s", (pid,))
    product["avg_rating"] = float(avg["avg_rating"] or 0)
    product["rating_count"] = int(avg["cnt"] or 0)
    return jsonify(product)

@app.post("/api/products")  # admin
def create_product():
    data = request.json
    pid = execute(
        "INSERT INTO products (name, brand, category, description, price, image_url) VALUES (%s,%s,%s,%s,%s,%s)",
        (data["name"], data.get("brand"), data.get("category"), data.get("description"), data["price"], data.get("image_url")),
    )
    return jsonify({"id": pid}), 201

@app.put("/api/products/<int:pid>")  # admin
def update_product(pid):
    data = request.json
    execute(
        "UPDATE products SET name=%s, brand=%s, category=%s, description=%s, price=%s, image_url=%s WHERE id=%s",
        (data["name"], data.get("brand"), data.get("category"), data.get("description"), data["price"], data.get("image_url"), pid),
    )
    return jsonify({"ok": True})

@app.delete("/api/products/<int:pid>")  # admin
def delete_product(pid):
    execute("DELETE FROM products WHERE id=%s", (pid,))
    return jsonify({"ok": True})

@app.get("/api/products/popular")
def popular_products():
    rows = query_all(
        """
        SELECT p.*, COALESCE(sales.total_qty,0) AS total_qty, COALESCE(rv.avg_rating,0) AS avg_rating
        FROM products p
        LEFT JOIN (
          SELECT product_id, SUM(quantity) AS total_qty
          FROM purchases GROUP BY product_id
        ) sales ON p.id = sales.product_id
        LEFT JOIN (
          SELECT product_id, AVG(rating) AS avg_rating
          FROM reviews GROUP BY product_id
        ) rv ON p.id = rv.product_id
        ORDER BY total_qty DESC, avg_rating DESC
        LIMIT 20
        """
    )
    return jsonify(rows)
