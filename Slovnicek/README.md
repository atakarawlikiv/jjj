## IT Slovníček

Autor: dmytroshevaha
Doména: dmytroshevaha.skola.test
Port: 8081


## Popis aplikace

Jednoduchá webová aplikace „IT Slovníček“, která:

zobrazuje IT pojmy z databáze
umožňuje zjistit stav aplikace
využívá lokální AI model (LLM) pro vysvětlení pojmů

Aplikace běží v Docker kontejneru a komunikuje s lokálním LLM (Ollama).


## Technologie

Python (Flask)
SQLite databáze
Docker + Docker Compose
Ollama (lokální LLM na CPU)


## Spuštění aplikace (na jiném počítači)

1. Požadavky

Na počítači musí být nainstalováno:

Docker Desktop
Docker Compose (součást Docker Desktopu)
(volitelné) Ollama pro AI endpoint

2. Stažení projektu

Rozbal ZIP nebo naklonuj repozitář:

git clone <repo-url>
cd <projekt>
3. Spuštění

V příkazové řádce (CMD / PowerShell):

docker compose up --build

4. Ověření

Otevři v prohlížeči:

http://localhost:8081/ping

Očekávaný výstup:

pong


## Přístup z jiného zařízení (např. mobil)
zjisti IP adresu počítače:

ipconfig


povol firewall:
netsh advfirewall firewall add rule name="MojeAPI" dir=in action=allow protocol=TCP localport=8081


ujisti se, že zařízení jsou na stejné síti
případně použij hotspot (kvůli izolaci WiFi)


## Endpointy
- GET  /ping       → pong
- GET  /status     → JSON se stavem a počtem pojmů
- GET  /pojmy      → seznam všech pojmů
- POST /ai         → vysvětlení pojmu přes LLM

## Ukázkový curl
curl -X POST http://jmenoprijmeni.skola.test:8081/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Co je DNS?"}'

## Síť
- IP serveru: 10.10.10.X
- Maska: 255.255.255.0 (/24)
- DHCP scope: 10.10.10.100–200
- DNS Option 006: 10.10.10.X
