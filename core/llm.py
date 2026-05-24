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
    """Llama al modelo LLM usando OpenRouter (si está disponible) o directamente Google Gemini con rotación de claves."""
    from core.storage import get_all_api_keys
    
    keys = get_all_api_keys()
    
    # 1. Buscar claves de OpenRouter en el búnker
    openrouter_keys = []
    for k in keys:
        if k.get("service", "").lower() in ["openrouter", "open_router"]:
            openrouter_keys.append(k.get("key"))
            
    # 2. Buscar claves directas de Gemini en el búnker
    gemini_keys = []
    for k in keys:
        if k.get("service") == "gemini":
            gemini_keys.append(k.get("key"))
            
    # Si no hay llaves directas de Gemini, intentar usar la por defecto de config
    if not gemini_keys and not openrouter_keys:
        if config.gemini_api_key and config.gemini_api_key != "AIzaSyC-...":
            gemini_keys.append(config.gemini_api_key)

    # ---- INTENTAR CON OPENROUTER PRIMERO SI HAY CLAVE ----
    if openrouter_keys:
        or_key = openrouter_keys[0]
        # Determinar el modelo gratuito óptimo a usar en OpenRouter
        or_model = "google/gemini-2.5-flash:free"
        if model and "/" in model:
            or_model = model
        elif model == "gemini-2.5-pro":
            or_model = "google/gemini-2.5-pro:free"
            
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {or_key}",
            "HTTP-Referer": "https://localhost:8000",
            "X-Title": "Monica Core Agent",
            "Content-Type": "application/json"
        }
        payload = {
            "model": or_model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        logger.info(f"Intentando llamada a OpenRouter con modelo gratuito '{or_model}'...")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                
                try:
                    text_response = data["choices"][0]["message"]["content"]
                    logger.info("Llamada a OpenRouter completada con éxito.")
                    return text_response
                except (KeyError, IndexError):
                    logger.error(f"Error parseando respuesta de OpenRouter: {data}")
            except Exception as exc:
                logger.warning(f"Fallo llamada a OpenRouter: {exc}. Reintentando con Gemini directo...")

    # ---- FALLBACK A GEMINI DIRECTO SI OPENROUTER NO ESTÁ DISPONIBLE O FALLA ----
    if not gemini_keys:
        return "⚠️ Mónica no puede hablar. Configura una API Key de OpenRouter o Gemini en el búnker de APIs."

    chosen_model = model or config.default_model
    if chosen_model and "/" in chosen_model:
        # Si venía un modelo con formato OpenRouter (ej. google/gemini-2.5-flash), limpiarlo para Gemini Directo
        chosen_model = "gemini-2.5-flash-lite"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }

    last_error_msg = ""
    for key_idx, gemini_key in enumerate(gemini_keys):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={gemini_key}"
        attempt = 0
        backoff = 1
        
        logger.info(f"Intentando llamada directa a Gemini con llave #{key_idx + 1} ({gemini_key[:8]}...)")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            while attempt <= max_retries:
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                    
                    if resp.status_code == 429:
                        logger.warning(f"Llave #{key_idx + 1} sin cuota (429). Probando siguiente llave...")
                        last_error_msg = f"Llave #{key_idx + 1} (429): {resp.text}"
                        break
                        
                    resp.raise_for_status()
                    data = resp.json()
                    
                    try:
                        text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                        return text_response
                    except (KeyError, IndexError):
                        return f"⚠️ Error parseando la respuesta de Gemini: {data}"
                        
                except httpx.HTTPStatusError as http_err:
                    logger.warning(f"Error HTTP de Gemini con llave #{key_idx + 1} ({http_err.response.status_code}): {http_err.response.text}")
                    last_error_msg = f"Error HTTP ({http_err.response.status_code}): {http_err.response.text}"
                    if http_err.response.status_code == 429:
                        break
                except Exception as exc:
                    logger.error(f"Error inesperado en llamada directa a Gemini con llave #{key_idx + 1}: {exc}")
                    last_error_msg = f"Error inesperado: {exc}"
                    
                await asyncio.sleep(backoff)
                attempt += 1
                backoff *= 2
                
    return f"⚠️ Error: No se pudo conectar a OpenRouter ni a Gemini. Último error: {last_error_msg}"

async def close_client() -> None:
    """Cierre del cliente al terminar la aplicación."""
    pass
