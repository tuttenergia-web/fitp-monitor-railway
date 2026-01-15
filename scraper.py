import asyncio
import re
from playwright.async_api import async_playwright

URL = "https://www.fitp.it/Tornei/Ricerca-tornei"
SEEN_CODES = set()

def extract_lomb_number(nome):
    m = re.search(r"LOMB\.\s*(\d+)", nome.upper())
    return int(m.group(1)) if m else None

def format_torneo(t):
    return f"{t['nome_torneo']} — {t['citta']} ({t['sigla_provincia']}) dal {t['data_inizio']} al {t['data_fine']}"

async def fetch_tournaments():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-setuid-sandbox"
        ])
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")

        # Rimuovi banner cookie
        await page.evaluate("""
            const banner = document.querySelector('#iubenda-cs-banner');
            if (banner) banner.remove();
        """)

        # Imposta filtri
        await page.select_option("#select-competitionType", value="1")
        await page.evaluate("document.querySelector('#select-competitionType').dispatchEvent(new Event('change'))")
        await asyncio.sleep(0.5)

        await page.select_option("#select_status", value="4")
        await page.evaluate("document.querySelector('#select_status').dispatchEvent(new Event('change'))")
        await asyncio.sleep(0.5)

        await page.select_option("#id_regioneSearch", label="Lombardia")
        await page.evaluate("document.querySelector('#id_regioneSearch').dispatchEvent(new Event('change'))")

        for _ in range(40):
            options = await page.locator("#id_provinciaSearch option").all_inner_texts()
            if any("Milano" in o for o in options):
                break
            await asyncio.sleep(0.25)

        await page.select_option("#id_provinciaSearch", label="Milano")
        await page.evaluate("document.querySelector('#id_provinciaSearch').dispatchEvent(new Event('change'))")
        await asyncio.sleep(2)

        # Estrai tornei dal DOM visibile
        tornei = await page.evaluate("window.app?.tornei || []")

        await browser.close()

    tornei_milano = [t for t in tornei if t.get("sigla_provincia") == "MI"]
    seen = set()
    unici = []
    for t in tornei_milano:
        guid = t.get("guid")
        if guid and guid not in seen:
            seen.add(guid)
            unici.append(t)
    return unici

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

async def run_scraper():
    print("Avvio scraper FITP…")
    tornei = await fetch_tournaments()
    nuovi = detect_new_tournaments(tornei)

    if nuovi:
        print("\n=== NUOVI TORNEI TROVATI ===")
        for t in nuovi:
            print("•", format_torneo(t))
            # Qui va la notifica Telegram
    else:
        print("Nessun nuovo torneo.")

async def main():
    while True:
        try:
            await run_scraper()
        except Exception as e:
            print("Errore:", e)
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())