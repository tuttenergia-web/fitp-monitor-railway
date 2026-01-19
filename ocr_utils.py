from PIL import Image
import pytesseract

def extract_text(image_path: str) -> str:
    """
    Esegue OCR su un'immagine usando Tesseract.
    Ritorna il testo estratto come stringa.
    """
    try:
        img = Image.open(image_path)

        # Usa lingua italiana se disponibile, altrimenti fallback automatico
        try:
            text = pytesseract.image_to_string(img, lang="ita")
        except:
            text = pytesseract.image_to_string(img)

        return text

    except Exception as e:
        return f"Errore OCR: {e}"