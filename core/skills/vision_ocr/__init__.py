"""
Módulo de Visión y OCR.
Permite a Mónica extraer texto de imágenes usando Tesseract.
"""
import os
import logging

logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str) -> dict:
    """
    Extrae el texto de una imagen utilizando Tesseract OCR.
    """
    if not os.path.exists(image_path):
        return {"status": "error", "message": f"La imagen {image_path} no existe."}
        
    try:
        from PIL import Image
        import pytesseract
        
        # En Windows, a veces es necesario configurar la ruta del ejecutable de tesseract
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        return {"status": "success", "file": image_path, "text": text.strip()}
    except ImportError:
        return {"status": "error", "message": "Pillow o pytesseract no están instalados."}
    except Exception as e:
        logger.error(f"Error en OCR: {e}")
        return {"status": "error", "message": str(e)}
