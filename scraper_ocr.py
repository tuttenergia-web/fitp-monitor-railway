import os
import re
import time
from screenshot import get_screenshot
from ocr_utils import extract_text
filter_tournament
is_duplicate
save_seen_tournament

# URL FITP con filtro "Milano"
FITP_URL = "https://www.federtennis.it/FITP_Tornei?provincia=Milano"
SCREENSHOT_PATH = "/tmp/fitp_milano.png"


def parse_tournaments_from_text(text: str):
    """
    Estrae i tornei dal testo OCR.
    Ritorna una lista di dizionari con i campi minimi richiesti.
    """
    tournaments = []
    lines = text.split("\n")

    current = {}

    for line in lines:
        line = line.strip()

        # Nome torneo (pattern generico)
        if re.search(r"Open|TPRA|Torneo|Campionato|Circuito", line, re.IGNORECASE):
            if current:
                tournaments.append(current)
                current = {}
            current["name"] = line

        # Date (pattern semplice)
        if re.search(r"\d{1,2}/\d{1,2}/\d{4}", line):
            current["dates"] = line

        # Circolo
        if "Tennis" in line or "Sport" in line or "Club" in line:
            current["club"] = line

    if current:
        tournaments.append(current)

    return tournaments


def process_tournaments(tournaments):
    """
    Applica filtri, LOMB, dedup e invia notifiche Telegram.
    """
    for t in tournaments:
        name = t.get("name", "")
        dates = t.get("dates", "")
        club = t.get("club", "")

        # Ricostruzione testo torneo
        text = f"{name}\n{dates}\n{club}"

        # Duplicati
        if is_duplicate(text):
            continue

        # Salva come visto
        save_seen_tournament(text)

        # Notifica Telegram
        send_telegram_message(f"🏆 Nuovo torneo trovato:\n\n{text}")


def run_ocr_scraper():
    """
    Flusso completo:
    1. Screenshot pagina FITP (Milano)
    2. OCR
    3. Parsing
    4. Filtri + LOMB + dedup
    5. Telegram
    """
    try:
        # 1) Screenshot
        get_screenshot(FITP_URL, SCREENSHOT_PATH)

        # 2) OCR
        text = extract_text(SCREENSHOT_PATH)

        # 3) Parsing
        tournaments = parse_tournaments_from_text(text)

        # 4) Filtri + LOMB + dedup + Telegram
        process_tournaments(tournaments)

    except Exception as e:
        send_telegram_message(f"❌ Errore scraper OCR: {e}")


if __name__ == "__main__":
    while True:
        run_ocr_scraper()
        time.sleep(300)  # ogni 5 minuti