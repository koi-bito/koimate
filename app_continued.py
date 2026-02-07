# app.py (continued)
from services.recommender import content_recommend_for_user, build_collab_model, collab_recommend_for_user
import heapq

collab_model = None

@app.before_first_request
def warm_models():
    global collab_model
    conn = get_db()
    collab_model = build_collab_model(conn)

@app.get("/api/recommendations")
def recommend():
    user_id = int(request.args["user_id"])
    conn = get_db()
    content_ids = content_recommend_for_user(conn, user_id, topk=30)  # content scores implicit ordering
    collab_ids = collab_recommend_for_user(conn, collab_model, user_id, topk=30)

    # Merge via priority queue (higher rank gets higher priority)
    priorities = {}
    for rank, pid in enumerate(content_ids):
        priorities[pid] = priorities.get(pid, 0) + max(0, 100 - rank)
    for rank, pid in enumerate(collab_ids):
        priorities[pid] = priorities.get(pid, 0) + max(0, 100 - rank)

    top = heapq.nlargest(12, priorities.items(), key=lambda kv: kv[1])
    ids = [pid for pid, _ in top]
    if not ids:
        return jsonify([])
    # preserve order with FIELD
    placeholders = ",".join(["%s"] * len(ids))
    rows = query_all(f"SELECT * FROM products WHERE id IN ({placeholders})", ids)
    # order rows by final ranking
    order = {pid: i for i, pid in enumerate(ids)}
    rows.sort(key=lambda r: order[r["id"]])
    return jsonify(rows)
