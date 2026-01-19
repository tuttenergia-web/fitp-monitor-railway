import os
from paddleocr import PaddleOCR

# Inizializzazione OCR (una sola volta)
ocr = PaddleOCR(use_angle_cls=True, lang='it')

def extract_text(image_path: str) -> str:
    """
    Esegue OCR sull'immagine e ritorna il testo estratto.
    """
    result = ocr.ocr(image_path, cls=True)
    lines = []

    for block in result:
        for line in block:
            text = line[1][0]
            lines.append(text)

    return "\n".join(lines)