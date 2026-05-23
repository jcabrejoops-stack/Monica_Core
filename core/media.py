# core/media.py
"""Módulo de generación multimedia para Mónica.

Capacidades:
- Generación de imágenes a partir de texto (usando Pollinations.ai, gratuito y sin API key).
- Generación de audio/voz (usando edge-tts, el TTS gratuito de Microsoft).
- Generación de video básico (usando moviepy para combinar imágenes).
- Scraping web (delegado a core.browser).

Todos los archivos generados se guardan en OneDrive/Monica_Core/media/.
"""
import asyncio
import logging
import httpx
import urllib.parse
from pathlib import Path
from datetime import datetime

from config import config

logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

# Directorio donde se guardan los archivos multimedia generados.
MEDIA_DIR = config.media_dir
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Sub‑directorios por tipo de medio.
IMAGES_DIR = MEDIA_DIR / "images"
AUDIO_DIR = MEDIA_DIR / "audio"
VIDEO_DIR = MEDIA_DIR / "video"
for d in (IMAGES_DIR, AUDIO_DIR, VIDEO_DIR):
    d.mkdir(parents=True, exist_ok=True)


# =====================================================================
# 🖼️  GENERACIÓN DE IMÁGENES
# =====================================================================
async def generate_image(prompt: str, width: int = 1024, height: int = 1024) -> str:
    """Genera una imagen a partir de un prompt de texto.

    Usa la API gratuita de Pollinations.ai (no requiere API key).
    Devuelve la ruta absoluta del archivo guardado.
    """
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = IMAGES_DIR / f"imagen_{timestamp}.png"

        async with httpx.AsyncClient(timeout=120) as client:
            logger.info(f"Generando imagen: '{prompt}'...")
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            with open(filename, "wb") as f:
                f.write(response.content)

        logger.info(f"Imagen guardada en: {filename}")
        return str(filename)
    except Exception as exc:
        logger.error(f"Error al generar imagen: {exc}")
        raise


# =====================================================================
# 🔊  GENERACIÓN DE AUDIO (Text-to-Speech)
# =====================================================================
async def generate_audio(text: str, voice: str = "es-MX-DaliaNeural") -> str:
    """Genera audio a partir de texto usando edge-tts (Microsoft TTS gratuito).

    Voces disponibles en español:
    - es-MX-DaliaNeural (femenina, México)
    - es-MX-JorgeNeural (masculino, México)
    - es-CO-GonzaloNeural (masculino, Colombia)
    - es-CO-SalomeNeural (femenina, Colombia)
    - es-ES-ElviraNeural (femenina, España)

    Devuelve la ruta absoluta del archivo .mp3 generado.
    """
    try:
        import edge_tts

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = AUDIO_DIR / f"audio_{timestamp}.mp3"

        logger.info(f"Generando audio con voz '{voice}'...")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(filename))

        logger.info(f"Audio guardado en: {filename}")
        return str(filename)
    except Exception as exc:
        logger.error(f"Error al generar audio: {exc}")
        raise


# =====================================================================
# 🎬  GENERACIÓN DE VIDEO (a partir de imágenes + audio)
# =====================================================================
async def generate_video(image_paths: list[str], audio_path: str | None = None, duration_per_image: float = 3.0) -> str:
    """Genera un video MP4 a partir de una lista de imágenes.

    Opcionalmente añade una pista de audio (mp3).
    Devuelve la ruta absoluta del archivo .mp4 generado.
    """
    try:
        from moviepy.editor import ImageSequenceClip, AudioFileClip

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = VIDEO_DIR / f"video_{timestamp}.mp4"

        logger.info(f"Generando video con {len(image_paths)} imágenes...")

        # Crear clip de imágenes.
        clip = ImageSequenceClip(image_paths, durations=[duration_per_image] * len(image_paths))

        # Añadir audio si se proporcionó.
        if audio_path:
            audio = AudioFileClip(audio_path)
            clip = clip.set_audio(audio)

        # Renderizar video.
        await asyncio.to_thread(
            clip.write_videofile,
            str(filename),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )

        logger.info(f"Video guardado en: {filename}")
        return str(filename)
    except Exception as exc:
        logger.error(f"Error al generar video: {exc}")
        raise


# =====================================================================
# 🌐  SCRAPING WEB (helper rápido sin necesidad del agente completo)
# =====================================================================
async def scrape_url(url: str) -> dict:
    """Extrae el título, texto principal y enlaces de una URL.

    Devuelve un diccionario con las claves: 'title', 'text', 'links'.
    """
    try:
        from playwright.async_api import async_playwright

        logger.info(f"Scraping: {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")

            title = await page.title()
            text = await page.inner_text("body")
            links = await page.eval_on_selector_all("a[href]", "els => els.map(e => ({text: e.innerText, href: e.href}))")

            await browser.close()

        result = {
            "title": title,
            "text": text[:5000],  # Limitar para no saturar.
            "links": links[:50],
        }
        logger.info(f"Scraping completado: {title}")
        return result
    except Exception as exc:
        logger.error(f"Error al hacer scraping de {url}: {exc}")
        raise


# =====================================================================
# 📡  LLAMADAS A APIs EXTERNAS (helper genérico)
# =====================================================================
async def call_api(url: str, method: str = "GET", headers: dict | None = None, body: dict | None = None) -> dict:
    """Realiza una llamada HTTP genérica a cualquier API.

    Devuelve un diccionario con 'status_code' y 'data' (JSON parseado si es posible).
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            logger.info(f"API {method} → {url}")
            if method.upper() == "GET":
                resp = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                resp = await client.post(url, headers=headers, json=body)
            else:
                resp = await client.request(method.upper(), url, headers=headers, json=body)

            resp.raise_for_status()
            try:
                data = resp.json()
            except Exception:
                data = resp.text

            return {"status_code": resp.status_code, "data": data}
    except Exception as exc:
        logger.error(f"Error al llamar API {url}: {exc}")
        raise
