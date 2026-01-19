import asyncio
import re
import json
import os
import requests

URL = "https://www.fitp.it/Tornei/Ricerca-tornei"
SEEN_CODES = set()

# ---------------------------------------------------------
#   TELEGRAM
# ---------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token o chat_id Telegram non configurati.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("Notifica Telegram inviata.")
    except Exception as e:
        print("Errore invio Telegram:", e)


# ---------------------------------------------------------
#   UTILS
# ---------------------------------------------------------

def extract_lomb_number(nome):
    m = re.search(r"LOMB\.\s*(\d+)", nome.upper())
    return int(m.group(1)) if m else None

def format_torneo(t):
    return (
        f"<b>{t['nome_torneo']}</b>\n"
        f"{t['citta']} ({t['sigla_provincia']})\n"
        f"Dal {t['data_inizio']} al {t['data_fine']}"
    )


# ---------------------------------------------------------
#   SCRAPER SENZA BROWSER
# ---------------------------------------------------------

def fetch_html():
    print("STEP 1: scarico HTML frontend FITP", flush=True)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_tournaments_from_html(html):
    print("STEP 2: estraggo tornei dal JS incorporato", flush=True)

    # Caso 1: array diretto
    pattern_array = re.compile(
        r"window\.app\.tornei\s*=\s*(\[[^\]]*\])",
        re.DOTALL
    )

    # Caso 2: oggetto __INITIAL_STATE__
    pattern_obj = re.compile(
        r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;",
        re.DOTALL
    )

    match = pattern_array.search(html)
    if match:
        raw = match.group(1)
        try:
            tornei = json.loads(raw)
            print(f"Trovati {len(tornei)} tornei (array diretto).", flush=True)
            return tornei
        except Exception as e:
            print("Errore parsing array diretto:", e, flush=True)

    match = pattern_obj.search(html)
    if match:
        raw = match.group(1)
        try:
            state = json.loads(raw)
            tornei = state.get("tornei", [])
            print(f"Trovati {len(tornei)} tornei (__INITIAL_STATE__).", flush=True)
            return tornei
        except Exception as e:
            print("Errore parsing __INITIAL_STATE__:", e, flush=True)

    print("Nessun blocco JS trovato.", flush=True)
    return []


async def fetch_tournaments():
    print("STEP 1: avvio scraper senza browser", flush=True)

    html = fetch_html()
    tornei = extract_tournaments_from_html(html)

    print("STEP 3: filtro Milano", flush=True)
    tornei_milano = [t for t in tornei if t.get("sigla_provincia") == "MI"]

    print("STEP 4: rimuovo duplicati", flush=True)
    seen = set()
    unici = []
    for t in tornei_milano:
        guid = t.get("guid")
        if guid and guid not in seen:
            seen.add(guid)
            unici.append(t)

    print("STEP 5: ritorno tornei", flush=True)
    return unici


# ---------------------------------------------------------
#   RILEVAMENTO NUOVI TORNEI
# ---------------------------------------------------------

def detect_new_tournaments(tornei):
    nuovi = []
    nuovi_codici = []
    for t in tornei:
        num = extract_lomb_number(t["nome_torneo"])
        if num and num not in SEEN_CODES:
            nuovi.append(t)
            nuovi_codici.append(num)
    SEEN_CODES.update(nuovi_codici)
    return nuovi


# ---------------------------------------------------------
#   CICLO SCRAPER
# ---------------------------------------------------------

async def run_scraper():
    print("Scraper FITP: inizio ciclo", flush=True)
    tornei = await fetch_tournaments()
    nuovi = detect_new_tournaments(tornei)

    if nuovi:
        print("\n=== NUOVI TORNEI TROVATI ===", flush=True)
        for t in nuovi:
            msg = format_torneo(t)
            print("•", msg, flush=True)
            send_telegram_message(msg)
    else:
        print("Nessun nuovo torneo.", flush=True)


async def main():
    while True:
        print("Worker FITP: ciclo attivo", flush=True)
        try:
            await run_scraper()
        except Exception as e:
            print("Errore:", e, flush=True)
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())