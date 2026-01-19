import time
from scraper_ocr import main as scraper_main

if __name__ == "__main__":
    while True:
        scraper_main()
        time.sleep(300)  # ogni 5 minuti