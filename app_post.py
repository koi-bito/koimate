@app.post("/api/register")
def register():
    data = request.json
    username, email, password = data["username"], data["email"], data["password"]
    hash_ = generate_password_hash(password)
    user_id = execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)",
        (username, email, hash_),
    )
    return jsonify({"id": user_id, "username": username, "email": email})

@app.post("/api/login")
def login():
    data = request.json
    email, password = data["email"], data["password"]
    user = query_one("SELECT * FROM users WHERE email=%s", (email,))
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401
    # set cookie or return token (omitted)
    return jsonify({"id": user["id"], "username": user["username"], "email": user["email"]})
