from flask import Flask, jsonify, request, render_template
import sqlite3
import requests
from datetime import datetime
from database import init_db
import os

app = Flask(__name__)

# Cesta k databázi (opraveno pro flexibilitu lokálně/server)
DB_PATH = os.environ.get("DB_PATH", "slovnicek.db")

# Inicializace DB při startu
init_db()

def get_db():
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
            "ai_model": "gpt-3.5-turbo"
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

    # Načtení klíčů z Environment Variables
    api_key = os.environ.get("OPENAI_API_KEY", "sk-0MlocXvcIJNS9usp-OlaAg")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")

    if not api_key:
        return jsonify({"response": "Chyba: Na serveru není nastaven OPENAI_API_KEY v Environment Variables."}), 500

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo", # Bezpečnější volba pro začátek
            "messages": [
                {"role": "user", "content": f"Vysvětli jednou krátkou větou v češtině, co je: {pojem}"}
            ],
            "temperature": 0.7
        }

        # Inteligentní spojení URL adresy
        base_url_cleaned = base_url.rstrip("/")
        if not base_url_cleaned.endswith("/chat/completions"):
            url = f"{base_url_cleaned}/chat/completions"
        else:
            url = base_url_cleaned

        response = requests.post(url, headers=headers, json=payload, timeout=45)
        
        # Pokud server vrátí chybu, vypíšeme ji do odpovědi pro snazší ladění
        if response.status_code != 200:
            return jsonify({"response": f"Server vrátil chybu {response.status_code}: {response.text}"})

        vysledek = response.json()
        odpoved = vysledek["choices"][0]["message"]["content"]

    except Exception as e:
        odpoved = f"Chyba při komunikaci s AI: {str(e)}"

    return jsonify({"response": odpoved})

if __name__ == "__main__":
    # Načtení portu, který přidělí server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
