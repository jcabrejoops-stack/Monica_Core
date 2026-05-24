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
    """Llama al modelo LLM exclusivamente usando Google Gemini con rotación automática de claves."""
    from core.storage import get_all_api_keys
    
    # 1. Obtener todas las llaves de Gemini del búnker
    gemini_keys = []
    keys = get_all_api_keys()
    for k in keys:
        if k.get("service") == "gemini":
            gemini_keys.append(k.get("key"))
            
    # Si no hay llaves en el búnker, usamos la por defecto del archivo de configuración
    if not gemini_keys:
        if config.gemini_api_key and config.gemini_api_key != "AIzaSyC-...":
            gemini_keys.append(config.gemini_api_key)
        
    if not gemini_keys:
        return "⚠️ Mónica no puede hablar. Necesitas configurar al menos una API Key de Gemini en el búnker."

    chosen_model = model or config.default_model
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }

    # Intentar con cada una de las llaves en el búnker
    last_error_msg = ""
    for key_idx, gemini_key in enumerate(gemini_keys):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={gemini_key}"
        attempt = 0
        backoff = 1
        
        logger.info(f"Intentando llamada a Gemini con llave #{key_idx + 1} ({gemini_key[:8]}...)")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            while attempt <= max_retries:
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                    
                    if resp.status_code == 429:
                        # Cuota excedida para esta llave, pasar a la siguiente llave inmediatamente
                        logger.warning(f"Llave #{key_idx + 1} sin cuota (429). Probando siguiente llave...")
                        last_error_msg = f"Llave #{key_idx + 1} (429): {resp.text}"
                        break # Rompe el bucle de intentos de esta llave y pasa a la siguiente llave
                        
                    resp.raise_for_status()
                    data = resp.json()
                    
                    # Extraer texto de la respuesta de Gemini
                    try:
                        text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                        return text_response
                    except (KeyError, IndexError):
                        return f"⚠️ Error parseando la respuesta de Gemini: {data}"
                        
                except httpx.HTTPStatusError as http_err:
                    logger.warning(f"Error HTTP de Gemini con llave #{key_idx + 1} ({http_err.response.status_code}): {http_err.response.text}")
                    last_error_msg = f"Error HTTP ({http_err.response.status_code}): {http_err.response.text}"
                    if http_err.response.status_code == 429:
                        break # Pasar a la siguiente llave
                except Exception as exc:
                    logger.error(f"Error inesperado en llamada a Gemini con llave #{key_idx + 1}: {exc}")
                    last_error_msg = f"Error inesperado: {exc}"
                    
                await asyncio.sleep(backoff)
                attempt += 1
                backoff *= 2
                
    return f"⚠️ Error: No se pudo conectar a Gemini tras probar todas las llaves en el búnker. Último error: {last_error_msg}"

async def close_client() -> None:
    """Cierre del cliente al terminar la aplicación."""
    pass
