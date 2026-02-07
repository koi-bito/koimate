# app.py
import os
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import mysql.connector.pooling
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, supports_credentials=True)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "database": os.getenv("DB_NAME", "ecommerce"),
    "user": os.getenv("DB_USER", "ecom_user"),
    "password": os.getenv("DB_PASS", "change_me"),
    "pool_name": "ecom_pool",
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    "pool_reset_session": True,
}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name=DB_CONFIG["pool_name"],
    pool_size=DB_CONFIG["pool_size"],
    pool_reset_session=DB_CONFIG["pool_reset_session"],
    host=DB_CONFIG["host"],
    database=DB_CONFIG["database"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
)

def get_db():
    if "db" not in g:
        g.db = connection_pool.get_connection()
    return g.db

@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()
