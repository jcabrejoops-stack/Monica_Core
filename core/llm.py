"""Cliente asincrónico para Gemini.

Provee la función ``call_llm`` que utiliza la API de Google Gemini para la interfaz gráfica principal.
"""
import json
import logging
import asyncio
from typing import Any, Dict
import httpx
from config import config

logger = logging.getLogger(__name__)

async def call_llm(
    prompt: str,
    model: str | None = None,
    max_retries: int = 2,
    engine: str = "speed"
) -> str:
    """Llama al modelo LLM exclusivamente usando Google Gemini."""
    from core.storage import get_all_api_keys
    
    # 1. Obtener la llave del búnker
    gemini_key = None
    keys = get_all_api_keys()
    for k in keys:
        if k.get("service") == "gemini":
            gemini_key = k.get("key")
            break
            
    if not gemini_key:
        gemini_key = config.gemini_api_key
        
    if not gemini_key or gemini_key == "AIzaSyC-...":
        return "⚠️ Mónica no puede hablar. Necesitas configurar la API Key de Gemini en el búnker."

    chosen_model = model or config.default_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    
    attempt = 0
    backoff = 1
    async with httpx.AsyncClient(timeout=120.0) as client:
        while attempt <= max_retries:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                
                # Extraer texto de la respuesta de Gemini
                try:
                    text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    return text_response
                except (KeyError, IndexError):
                    return f"⚠️ Error parseando la respuesta de Gemini: {data}"
                    
            except httpx.HTTPStatusError as http_err:
                logger.warning(f"Error HTTP de Gemini ({http_err.response.status_code}): {http_err.response.text}")
            except Exception as exc:
                logger.error(f"Error inesperado en llamada a Gemini: {exc}")
                
            await asyncio.sleep(backoff)
            attempt += 1
            backoff *= 2
            
    return "⚠️ Error: No se pudo conectar a Gemini tras múltiples intentos."

async def close_client() -> None:
    """Cierre del cliente al terminar la aplicación."""
    pass
