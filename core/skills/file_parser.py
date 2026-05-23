# core/skills/file_parser.py
"""Módulo para parsear y extraer información de archivos adjuntos (texto, PDFs, imágenes).
"""
import mimetypes
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def parse_file(file_path: Path) -> dict:
    """Extrae el contenido de texto o metadatos de un archivo específico.
    
    Parameters
    ----------
    file_path : Path
        Ruta absoluta al archivo en el disco.
        
    Returns
    -------
    dict
        Diccionario con el resultado del análisis.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return {
            "success": False,
            "error": "El archivo no existe en el servidor."
        }
    
    file_name = file_path.name
    file_size = file_path.stat().st_size
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    res = {
        "success": True,
        "file_name": file_name,
        "file_size": file_size,
        "mime_type": mime_type or "application/octet-stream",
        "file_type": "unknown",
        "text_content": None,
        "metadata": {
            "size_bytes": file_size,
            "mime_type": mime_type or "application/octet-stream"
        }
    }
    
    ext = file_path.suffix.lower()
    
    # 1. IMÁGENES
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]:
        res["file_type"] = "image"
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                res["metadata"]["width"] = img.width
                res["metadata"]["height"] = img.height
                res["metadata"]["format"] = img.format
                res["metadata"]["mode"] = img.mode
        except Exception as e:
            res["error"] = f"Error leyendo metadatos de imagen: {e}"
            logger.error(f"Error parsing image {file_name}: {e}")
            
    # 2. PDFs
    elif ext == ".pdf":
        res["file_type"] = "pdf"
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            text_runs = []
            # Extraer hasta un límite razonable (ej: primeras 10 páginas para evitar desborde de contexto)
            max_pages = 10
            num_pages = len(reader.pages)
            res["metadata"]["pages"] = num_pages
            
            for i in range(min(num_pages, max_pages)):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text_runs.append(f"--- [PÁGINA {i+1}] ---\n{page_text}")
            
            content = "\n\n".join(text_runs)
            if num_pages > max_pages:
                content += f"\n\n... [Contenido truncado. El PDF original tiene {num_pages} páginas, se extrajeron las primeras {max_pages}]"
            
            res["text_content"] = content
        except ImportError:
            res["error"] = "La librería 'pypdf' no está disponible."
            res["text_content"] = "Error: La librería 'pypdf' no está disponible para extraer el texto de este PDF en el servidor."
        except Exception as e:
            res["error"] = f"Error al leer PDF: {e}"
            res["text_content"] = f"Error al extraer texto del PDF: {e}"
            
    # 3. VIDEOS (moviepy)
    elif ext in [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".3gp"] or (mime_type and mime_type.startswith("video/")):
        res["file_type"] = "video"
        try:
            from moviepy.editor import VideoFileClip
            from config import config
            
            # Cargar el clip de video
            with VideoFileClip(str(file_path)) as clip:
                duration = clip.duration
                width, height = clip.size
                fps = clip.fps
                
                res["metadata"]["duration_seconds"] = duration
                res["metadata"]["width"] = width
                res["metadata"]["height"] = height
                res["metadata"]["fps"] = fps
                res["metadata"]["has_audio"] = (clip.audio is not None)
                
                # Extraer fotogramas clave para que Mónica los vea
                from PIL import Image
                
                keyframes = []
                times_to_extract = [duration * 0.1, duration * 0.5, duration * 0.9] if duration > 2 else [duration * 0.5]
                
                for idx, t in enumerate(times_to_extract):
                    # Extraer frame en formato numpy (RGB)
                    frame_array = clip.get_frame(t)
                    # Convertir a imagen PIL
                    img = Image.fromarray(frame_array)
                    
                    # Guardar como jpg directamente en el mismo directorio de uploads
                    kf_filename = f"kf_{file_path.stem}_{idx+1}.jpg"
                    kf_path = file_path.parent / kf_filename
                    img.save(kf_path, quality=80)
                    
                    # Sincronizar en OneDrive si está configurado
                    if config.onedrive_path:
                        od_dir = config.onedrive_path / "media" / "uploads"
                        od_dir.mkdir(parents=True, exist_ok=True)
                        img.save(str(od_dir / kf_filename), quality=80)
                    
                    keyframes.append({
                        "time_seconds": round(t, 2),
                        "url": f"/media/uploads/{kf_filename}",
                        "filename": kf_filename
                    })
                
                res["metadata"]["keyframes"] = keyframes
                res["text_content"] = (
                    f"Video cargado con éxito.\n"
                    f"- Duración: {duration:.2f} segundos\n"
                    f"- Resolución: {width}x{height}\n"
                    f"- FPS: {fps:.2f}\n"
                    f"- Contiene audio: {'Sí' if clip.audio is not None else 'No'}\n"
                    f"- Fotogramas clave extraídos: {len(keyframes)} (guardados en el servidor para análisis visual)."
                )
        except Exception as e:
            res["error"] = f"Error al leer video con moviepy: {e}"
            res["text_content"] = f"Error analizando archivo de video: {e}"
            
    # 4. ARCHIVOS DE TEXTO / CÓDIGO
    elif ext in [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv", ".xml", ".ini", ".yaml", ".yml", ".bat", ".sh", ".ps1"]:
        res["file_type"] = "text"
        try:
            # Leer el archivo detectando codificación de forma segura
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                # Leer hasta 15,000 caracteres para no desbordar el contexto
                content = f.read(15000)
                if file_size > 15000:
                    content += "\n\n... [Contenido truncado debido al tamaño del archivo]"
                res["text_content"] = content
        except Exception as e:
            res["error"] = f"Error leyendo archivo de texto: {e}"
            res["text_content"] = f"Error leyendo archivo de texto: {e}"
            
    return res
