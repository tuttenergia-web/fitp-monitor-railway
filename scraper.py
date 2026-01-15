import asyncio
from playwright.async_api import async_playwright
import time

# Funzione principale dello scraper
async def run_scraper():
    print("Avvio scraper FITP...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-setuid-sandbox"
            ]
        )

        page = await browser.new_page()

        url = "https://www.fitp.it/"
        print(f"Apro la pagina: {url}")

        await page.goto(url, timeout=60000)

        # Esempio: cattura un elemento visibile
        titolo = await page.text_content("h1")
        print("Titolo pagina:", titolo)

        await browser.close()
        print("Browser chiuso.")

# Entry point per esecuzione locale o come worker
def main():
    while True:
        try:
            asyncio.run(run_scraper())
        except Exception as e:
            print("Errore nello scraper:", e)

        # Attendi 60 secondi prima del prossimo ciclo
        time.sleep(60)