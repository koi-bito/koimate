@app.get("/api/analytics/top")
def top_analytics():
    rows = query_all("""
      SELECT p.id, p.name,
             SUM(pc.quantity) AS total_qty,
             AVG(rv.rating) AS avg_rating
      FROM products p
      LEFT JOIN purchases pc ON pc.product_id=p.id
      LEFT JOIN reviews rv ON rv.product_id=p.id
      GROUP BY p.id, p.name
      ORDER BY total_qty DESC
      LIMIT 10
    """)
    return jsonify(rows)
