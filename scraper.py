# Qui va la logica Playwright per il monitor FITP

import asyncio
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # URL da monitorare
        url = "https://www.fitp.it/"

        await page.goto(url)

        # Esempio: cattura un elemento visibile
        titolo = await page.text_content("h1")

        print("Titolo pagina:", titolo)

        await browser.close()

def main():
    asyncio.run(run_scraper())