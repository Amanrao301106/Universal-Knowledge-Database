from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# Set FRONTEND_ORIGINS to a comma-separated list of trusted frontend origins
# in the Render environment settings, for example:
# https://your-project.vercel.app
origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": origins}})

def get_db():
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "universal_knowledge_db"),
        "connection_timeout": 10,
    }

    # Optional CA certificate path for verified TLS connections.
    # Aiven provides a CA certificate in its service connection settings.
    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca:
        config["ssl_ca"] = ssl_ca
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True

    return mysql.connector.connect(**config)

def serialize(row):
    if not row:
        return None
    if row.get("created_at"):
        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M")
    return row

@app.get("/")
def index():
    return jsonify({
        "service": "Universal Knowledge Database API",
        "status": "running",
        "health": "/api/health"
    })

@app.get("/api/stats")
def stats():
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM knowledge")
        total = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(DISTINCT category) AS categories FROM knowledge")
        categories = cur.fetchone()["categories"]
        cur.execute("SELECT COUNT(DISTINCT source) AS sources FROM knowledge")
        sources = cur.fetchone()["sources"]
        cur.close()
        conn.close()
        return jsonify({"total": total, "categories": categories, "sources": sources})
    except Error:
        app.logger.exception("Database error while loading stats")
        return jsonify({"error": "Database is unavailable.", "total": 0, "categories": 0, "sources": 0}), 503

@app.get("/api/knowledge")
def list_knowledge():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        sql = """SELECT k.id, k.title, k.content, k.category, k.source, k.created_at
                 FROM knowledge k WHERE (%s = '' OR k.category = %s)
                 AND (%s = '' OR k.title LIKE %s OR k.content LIKE %s OR k.tags LIKE %s)
                 ORDER BY k.created_at DESC"""
        like = f"%{q}%"
        cur.execute(sql, (category, category, q, like, like, like))
        rows = [serialize(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(rows)
    except Error:
        app.logger.exception("Database error while listing knowledge")
        return jsonify({"error": "Database is unavailable."}), 503

@app.post("/api/knowledge")
def add_knowledge():
    data = request.get_json(silent=True) or {}
    required = ["title", "content", "category"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": "Title, content and category are required."}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO knowledge (title, content, category, source, tags) VALUES (%s,%s,%s,%s,%s)",
            (
                data["title"].strip(),
                data["content"].strip(),
                data["category"].strip(),
                (data.get("source") or "User contribution").strip(),
                (data.get("tags") or "").strip()
            )
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({"message": "Knowledge record saved.", "id": new_id}), 201
    except Error:
        app.logger.exception("Database error while inserting knowledge")
        return jsonify({"error": "Could not save the record. Check database configuration."}), 503

@app.delete("/api/knowledge/<int:record_id>")
def delete_knowledge(record_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM knowledge WHERE id = %s", (record_id,))
        conn.commit()
        deleted = cur.rowcount
        cur.close()
        conn.close()
        if not deleted:
            return jsonify({"error": "Record not found."}), 404
        return jsonify({"message": "Record deleted."})
    except Error:
        app.logger.exception("Database error while deleting knowledge")
        return jsonify({"error": "Could not delete the record."}), 503

@app.get("/api/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify({"api": "running", "database": "connected"})
    except Error:
        app.logger.exception("Database health check failed")
        return jsonify({"api": "running", "database": "disconnected"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
