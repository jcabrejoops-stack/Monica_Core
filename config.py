# config.py
"""Configuración global del proyecto Mónica.

Este archivo define constantes y valores por defecto que pueden ser
sobrescritos mediante variables de entorno. Está pensado para ser
importado por los demás módulos.
"""
import os
from dataclasses import dataclass
from pathlib import Path

# ---------- Rutas ----------
USERPROFILE = os.getenv("USERPROFILE", "")
BASE_DIR = Path(__file__).resolve().parent  # raíz del proyecto local (ahora en C:\Users\jcabr\Monica_Core)
DEFAULT_ONEDRIVE = Path(USERPROFILE) / "OneDrive" / "Respaldo_Monica"
ONEDRIVE_PATH = Path(os.getenv("MONICA_ONEDRIVE", DEFAULT_ONEDRIVE))

# Carpetas activas de estado y logs (ahora locales)
STATE_DIR = BASE_DIR / "state"
LOGS_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / "media"

# ---------- Playwright ----------
# Por defecto usamos modo headless (sin ventana visible). Cambiar al
# iniciar la aplicación si se necesita depuración.
PLAYWRIGHT_HEADLESS: bool = os.getenv("MONICA_HEADLESS", "true").lower() == "true"

# ---------- LLM (Gemini Cloud) ----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC-cOSuhE8hRLdMAz6CxI5FGWGSYdIW4HM")
DEFAULT_MODEL = os.getenv("MONICA_DEFAULT_MODEL", "gemini-2.5-flash")
LLM_TIMEOUT_SECONDS = int(os.getenv("MONICA_LLM_TIMEOUT", "120"))

# ---------- Logging ----------
# Nivel DEBUG por defecto para facilitar diagnóstico.
LOG_LEVEL = os.getenv("MONICA_LOG_LEVEL", "DEBUG").upper()

# ---------- Otros ----------
# Tiempo de espera entre teclados simulados (milisegundos)
MIN_TYPING_DELAY = int(os.getenv("MONICA_MIN_TYPING_DELAY", "50"))
MAX_TYPING_DELAY = int(os.getenv("MONICA_MAX_TYPING_DELAY", "250"))

@dataclass
class Config:
    base_dir: Path = BASE_DIR
    onedrive_path: Path = ONEDRIVE_PATH
    state_dir: Path = STATE_DIR
    logs_dir: Path = LOGS_DIR
    media_dir: Path = MEDIA_DIR
    playwright_headless: bool = PLAYWRIGHT_HEADLESS
    gemini_api_key: str = GEMINI_API_KEY
    default_model: str = DEFAULT_MODEL
    llm_timeout: int = LLM_TIMEOUT_SECONDS
    log_level: str = LOG_LEVEL
    min_typing_delay: int = MIN_TYPING_DELAY
    max_typing_delay: int = MAX_TYPING_DELAY

config = Config()
