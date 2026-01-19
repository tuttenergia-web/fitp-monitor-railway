import os
import requests

API_KEY = os.getenv("SCREENSHOT_API_KEY")  # Impostala su Fly.io
API_URL = "https://shot.screenshotapi.net/screenshot"

def get_screenshot(url: str, output_path: str) -> str:
    """
    Scarica uno screenshot della pagina FITP filtrata per Milano.
    Ritorna il percorso del file salvato.
    """
    params = {
        "token": API_KEY,
        "url": url,
        "full_page": True,
        "fresh": True,
        "output": "image",
        "file_type": "png",
        "wait_for_event": "load"
    }

    response = requests.get(API_URL, params=params, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(f"Screenshot API error: {response.text}")

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path