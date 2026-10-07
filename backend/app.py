import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "notesdb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        port=os.environ.get("DB_PORT", "5432")
    )


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
@app.route("/health/", methods=["GET"])
@app.route("/api/health/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/notes", methods=["GET"])
def get_notes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    notes = [
        {"id": r[0], "title": r[1], "content": r[2], "created_at": str(r[3])}
        for r in rows
    ]
    return jsonify(notes)


@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json() or {}
    if "title" not in data or not data.get("title"):
        return jsonify({"error": "El título es requerido"}), 400

    title = data["title"]
    content = data.get("content", "")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING id",
        (title, content)
    )
    note_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": note_id, "title": title, "content": content}), 201


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"result": "deleted"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
