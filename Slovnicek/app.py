from flask import Flask, jsonify, request, render_template
import sqlite3
import requests
from datetime import datetime
from database import init_db
import os

# ✅ TOTO TI CHYBĚLO
app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "/app/data/slovnicek.db")

# Inicializace DB při startu
init_db()

def get_db():
    """Vytvoří připojení k SQLite databázi."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return "pong"

@app.route("/status")
def status():
    try:
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM pojmy").fetchone()[0]
        conn.close()
        return jsonify({
            "status": "ok",
            "autor": "dmytroshevaha",
            "cas": datetime.now().isoformat(),
            "pocet_pojmu": count,
            "ai_model": "gemma3:4b"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/pojmy")
def pojmy():
    try:
        conn = get_db()
        rows = conn.execute("SELECT * FROM pojmy").fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ai", methods=["POST"])
def ai():
    data = request.json
    pojem = data.get("prompt", "")

    if not pojem:
        return jsonify({"response": "Nebyl zadán žádný dotaz."}), 400

    try:
        response = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": "gemma3:4b",
                "prompt": f"Vysvětli jednou krátkou větou v češtině, co je: {pojem}",
                "stream": False
            },
            timeout=45
        )
        response.raise_for_status()
        odpoved = response.json().get("response", "Nepodařilo se získat odpověď.")
    except requests.exceptions.ConnectionError:
        odpoved = "Chyba: Nelze se spojit s Ollamou."
    except Exception as e:
        odpoved = f"Chyba při komunikaci s AI: {str(e)}"

    return jsonify({"response": odpoved})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)