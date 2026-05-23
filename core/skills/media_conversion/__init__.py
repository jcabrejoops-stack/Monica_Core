"""
Módulo de Conversión Multimedia.
Permite convertir archivos entre formatos.
"""
import os
import logging

logger = logging.getLogger(__name__)

def convert_video_to_audio(video_path: str, output_path: str) -> dict:
    """
    Extrae el audio de un archivo de video y lo guarda en formato MP3 o WAV.
    """
    if not os.path.exists(video_path):
        return {"status": "error", "message": "El archivo de video no existe."}
        
    try:
        from moviepy.editor import VideoFileClip
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(output_path, logger=None)
        
        return {"status": "success", "file": output_path}
    except ImportError:
        return {"status": "error", "message": "Moviepy no está instalado."}
    except Exception as e:
        logger.error(f"Error convirtiendo video a audio: {e}")
        return {"status": "error", "message": str(e)}

def resize_image(image_path: str, output_path: str, width: int, height: int) -> dict:
    """
    Redimensiona una imagen a las dimensiones dadas.
    """
    if not os.path.exists(image_path):
        return {"status": "error", "message": "La imagen no existe."}
        
    try:
        from PIL import Image
        img = Image.open(image_path)
        img = img.resize((width, height))
        img.save(output_path)
        
        return {"status": "success", "file": output_path, "dimensions": f"{width}x{height}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
