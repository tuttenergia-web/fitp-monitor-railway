import os
import re
import time
import asyncio
from screenshot import get_screenshot
from ocr_utils import extract_text
from scraper import send_telegram_message

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


def main():
    print(">>> CICLO OCR AVVIATO")

    # 1. Screenshot
    print(">>> STEP 1: screenshot")
    get_screenshot(FITP_URL, SCREENSHOT_PATH)

    # 2. OCR
    print(">>> STEP 2: OCR")
    text = extract_text(SCREENSHOT_PATH)

    # 3. Parsing
    print(">>> STEP 3: parsing")
    tournaments = parse_tournaments_from_text(text)

    # 4. Notifica Telegram per ogni torneo trovato
    print(">>> STEP 4: invio Telegram")
    for t in tournaments:
        name = t.get("name", "")
        dates = t.get("dates", "")
        club = t.get("club", "")

        msg = f"{name}\n{dates}\n{club}"
        asyncio.run(send_telegram_message(f"🏆 Nuovo torneo trovato:\n\n{msg}"))

    print(">>> PIPELINE OCR COMPLETATA")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # ogni 5 minuti