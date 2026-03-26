from flask import Flask, jsonify, request, render_template
import sqlite3
import requests
from datetime import datetime
from database import init_db
import os

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
            "ai_model": "gpt-4o-mini" # Změněno na standardní OpenAI model pro cloud
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

    # Načtení klíčů ze serveru (podle zadání z obrázku 1)
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1") # Fallback na orig OpenAI

    if not api_key:
        return jsonify({"response": "Chyba: Na serveru není nastaven OPENAI_API_KEY."}), 500

    try:
        # Přepsáno na standardní OpenAI API formát, který ten tvůj server vyžaduje
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini", # Případně "gpt-3.5-turbo", záleží co ten proxy server v Kuřimi podporuje
            "messages": [
                {"role": "user", "content": f"Vysvětli jednou krátkou větou v češtině, co je: {pojem}"}
            ],
            "temperature": 0.7
        }

        # URL poskládáme tak, aby to šlo na endpoint /chat/completions
        url = f"{base_url.rstrip('/')}/chat/completions"

        response = requests.post(url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        
        # Vytáhnutí odpovědi z OpenAI formátu
        vysledek = response.json()
        odpoved = vysledek["choices"][0]["message"]["content"]

    except Exception as e:
        odpoved = f"Chyba při komunikaci s AI: {str(e)}"

    return jsonify({"response": odpoved})

if __name__ == "__main__":
    # 🌟 OPRAVA PORTU PRO SERVER 🌟
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
