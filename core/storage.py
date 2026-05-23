# core/storage.py
"""Módulo de persistencia y gestión de logs para Mónica.

- Detecta automáticamente la ruta de OneDrive del usuario.
- Crea la estructura de carpetas Monica_Core/logs y Monica_Core/state.
- Proporciona funciones de logging y guardado de estado en tiempo real.
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

_initialized = False

def _ensure_directories() -> None:
    """Crea la carpeta base y los sub‑directorios si no existen."""
    global _initialized
    logs_dir = config.logs_dir
    state_dir = config.state_dir
    sessions_dir = config.state_dir / "sessions"

    for p in (logs_dir, state_dir, sessions_dir):
        p.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directorio asegurado: {p}")

    # Configurar logger para escribir en archivo (solo la primera vez).
    if not _initialized:
        log_file = logs_dir / f"monica_{datetime.now():%Y%m%d_%H%M%S}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        logging.getLogger().addHandler(file_handler)
        logger.info(f"Logger inicializado en {log_file}")
        _initialized = True

async def init_storage() -> None:
    """Inicializa la persistencia. Se llama una sola vez al arrancar el agente."""
    _ensure_directories()
    logger.info("Sistema de almacenamiento inicializado.")

RECENT_EVENTS = []

def log_event(event: str) -> None:
    """Registra un evento en el logger (también irá a archivo) y lo guarda en memoria."""
    logger.info(event)
    timestamp = datetime.now().strftime("%H:%M:%S")
    RECENT_EVENTS.append(f"[{timestamp}] {event}")
    if len(RECENT_EVENTS) > 30:
        RECENT_EVENTS.pop(0)

def save_state(data: dict, filename: str = "session_state.json") -> None:
    """Guarda un diccionario JSON en state/."""
    state_path = config.state_dir / filename
    try:
        with state_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"Estado guardado en {state_path}")
    except Exception as exc:
        logger.error(f"Fallo al guardar estado en {state_path}: {exc}")

def get_chat_history(session_id: str = "default") -> list:
    """Recupera el historial de chat guardado en state/sessions/{session_id}.json."""
    history_file = config.state_dir / "sessions" / f"{session_id}.json"
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_chat_history(history: list, session_id: str = "default") -> None:
    """Guarda el historial de chat en state/sessions/{session_id}.json."""
    history_file = config.state_dir / "sessions" / f"{session_id}.json"
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error al guardar historial de chat: {e}")

def get_all_sessions() -> list:
    """Devuelve la lista de todas las sesiones guardadas."""
    sessions_dir = config.state_dir / "sessions"
    sessions = []
    
    if not sessions_dir.exists():
        return sessions

    for file_path in sessions_dir.glob("*.json"):
        session_id = file_path.stem
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                title = "Nueva Sesión"
                
                # Buscar título personalizado o usar primer mensaje
                for msg in history:
                    if msg.get("role") == "system_title":
                        title = msg.get("content", "")
                        break
                    elif msg.get("role") == "user" and title == "Nueva Sesión":
                        title = msg.get("content", "")[:30] + ("..." if len(msg.get("content", "")) > 30 else "")
                
                # Obtener la fecha de modificación
                mtime = file_path.stat().st_mtime
                
                sessions.append({
                    "id": session_id,
                    "title": title,
                    "updated_at": mtime
                })
        except Exception:
            continue
            
    # Ordenar por fecha descendente
    sessions.sort(key=lambda x: x["updated_at"], reverse=True)
    return sessions

def rename_session(session_id: str, new_title: str) -> None:
    """Cambia el nombre de la sesión añadiendo un mensaje oculto de sistema."""
    history_file = config.state_dir / "sessions" / f"{session_id}.json"
    if not history_file.exists():
        return
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
            
        if len(history) > 0 and history[0].get("role") == "system_title":
            history[0]["content"] = new_title
        else:
            history.insert(0, {"role": "system_title", "content": new_title})
            
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error al renombrar sesión {session_id}: {e}")


def delete_session_files(session_id: str) -> None:
    """Borra físicamente todos los archivos asociados a la sesión (imágenes, audios, videos, subidas)
    del almacenamiento local y de OneDrive, y luego elimina el archivo JSON de la sesión.
    """
    import re
    
    # 1. Obtener la sesión y leer su historial
    sessions_dir = config.state_dir / "sessions"
    session_file = sessions_dir / f"{session_id}.json"
    
    if not session_file.exists():
        log_event(f"Limpieza de disco: No se encontró el archivo de sesión para {session_id}")
        return

    try:
        with open(session_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception as e:
        logger.error(f"Error al leer sesión {session_id} para borrado: {e}")
        history = []

    # 2. Buscar archivos multimedia referenciados
    files_to_delete = set()
    
    # Expresión regular para detectar enlaces a /media/tipo_medio/nombre_archivo
    # Permite caracteres alfanuméricos, guiones, puntos y barras bajas para evitar path traversal
    media_pattern = re.compile(r'/media/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-\.]+)')
    
    for msg in history:
        # Buscar en el contenido de texto del mensaje
        content = msg.get("content", "")
        for match in media_pattern.finditer(content):
            media_type, filename = match.groups()
            files_to_delete.add((media_type, filename))
            
        # Buscar en attachments (adjuntos)
        attachments = msg.get("attachments", [])
        for att in attachments:
            url = att.get("url", "")
            if url:
                for match in media_pattern.finditer(url):
                    media_type, filename = match.groups()
                    files_to_delete.add((media_type, filename))
            
            # Subidas directas por nombre de archivo
            filename = att.get("filename")
            if filename:
                # Los adjuntos subidos van por defecto al subdirectorio "uploads"
                files_to_delete.add(("uploads", filename))

    log_event(f"Limpieza de disco: Detectados {len(files_to_delete)} archivos asociados a la sesión {session_id}")
    
    # 3. Borrar los archivos físicamente
    for media_type, filename in files_to_delete:
        # Sanitizar para evitar path traversal
        filename = os.path.basename(filename)
        media_type = os.path.basename(media_type)
        
        # Ruta local
        local_path = config.base_dir / "media" / media_type / filename
        if local_path.exists():
            try:
                local_path.unlink()
                log_event(f"Limpieza de disco: Archivo local eliminado -> media/{media_type}/{filename}")
            except Exception as e:
                logger.error(f"Error al borrar archivo local {local_path}: {e}")
                log_event(f"Limpieza de disco: ❌ Error al borrar local -> media/{media_type}/{filename}")

        # Ruta OneDrive (si está configurada)
        if config.onedrive_path:
            od_path = config.onedrive_path / "media" / media_type / filename
            if od_path.exists():
                try:
                    od_path.unlink()
                    log_event(f"Limpieza de disco: Archivo OneDrive eliminado -> media/{media_type}/{filename}")
                except Exception as e:
                    logger.error(f"Error al borrar archivo OneDrive {od_path}: {e}")
                    log_event(f"Limpieza de disco: ❌ Error al borrar OneDrive -> media/{media_type}/{filename}")

    # 4. Eliminar el archivo de sesión JSON
    try:
        session_file.unlink()
        log_event(f"Limpieza de disco: Sesión {session_id}.json eliminada permanentemente del servidor.")
    except Exception as e:
        logger.error(f"Error al eliminar sesión JSON {session_file}: {e}")
        log_event(f"Limpieza de disco: ❌ Error al borrar sesión {session_id}.json")

def sync_session_to_onedrive(session_id: str) -> None:
    """Copia manualmente el archivo JSON de la sesión activa y todos sus archivos multimedia
    (imágenes, audios, videos, subidas) asociados a la bóveda de OneDrive.
    """
    import re
    import shutil
    
    if not config.onedrive_path:
        log_event("Sincronización: ❌ No se puede sincronizar. OneDrive no está configurado.")
        raise ValueError("OneDrive no está configurado en las variables de entorno.")

    # 1. Ubicar el archivo de la sesión
    sessions_dir = config.state_dir / "sessions"
    session_file = sessions_dir / f"{session_id}.json"
    
    if not session_file.exists():
        log_event(f"Sincronización: No se encontró el archivo de sesión local para {session_id}")
        return

    # Asegurar el directorio de destino en OneDrive
    od_sessions_dir = config.onedrive_path / "state" / "sessions"
    od_sessions_dir.mkdir(parents=True, exist_ok=True)
    od_session_file = od_sessions_dir / f"{session_id}.json"

    # Copiar archivo de sesión JSON
    try:
        shutil.copy2(str(session_file), str(od_session_file))
        log_event(f"Sincronización: Guardado archivo de sesión en OneDrive -> state/sessions/{session_id}.json")
    except Exception as e:
        logger.error(f"Error al copiar sesión JSON a OneDrive: {e}")
        log_event(f"Sincronización: ❌ Error al copiar archivo de sesión JSON a OneDrive.")
        raise

    # 2. Leer historial para buscar archivos multimedia
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception as e:
        logger.error(f"Error al leer sesión {session_id} para sincronización: {e}")
        history = []

    files_to_sync = set()
    media_pattern = re.compile(r'/media/([a-zA-Z0-9_\-]+)/([a-zA-Z0-9_\-\.]+)')
    
    for msg in history:
        content = msg.get("content", "")
        for match in media_pattern.finditer(content):
            media_type, filename = match.groups()
            files_to_sync.add((media_type, filename))
            
        attachments = msg.get("attachments", [])
        for att in attachments:
            url = att.get("url", "")
            if url:
                for match in media_pattern.finditer(url):
                    media_type, filename = match.groups()
                    files_to_sync.add((media_type, filename))
            
            filename = att.get("filename")
            if filename:
                files_to_sync.add(("uploads", filename))

    log_event(f"Sincronización: Detectados {len(files_to_sync)} archivos multimedia para subir a la nube.")
    
    # 3. Copiar los archivos a OneDrive
    copied_count = 0
    for media_type, filename in files_to_sync:
        filename = os.path.basename(filename)
        media_type = os.path.basename(media_type)
        
        local_path = config.base_dir / "media" / media_type / filename
        if local_path.exists():
            od_media_dir = config.onedrive_path / "media" / media_type
            od_media_dir.mkdir(parents=True, exist_ok=True)
            od_path = od_media_dir / filename
            
            try:
                shutil.copy2(str(local_path), str(od_path))
                log_event(f"Sincronización: Archivo subido a OneDrive -> media/{media_type}/{filename}")
                copied_count += 1
            except Exception as e:
                logger.error(f"Error al sincronizar archivo {local_path} a OneDrive: {e}")
                log_event(f"Sincronización: ❌ Error al copiar -> media/{media_type}/{filename}")

    log_event(f"Sincronización: ¡Proceso completado! {copied_count} archivos multimedia respaldados en la nube con éxito.")

def get_all_api_keys() -> list:
    """Recupera todas las api keys guardadas."""
    keys_file = config.state_dir / "api_keys.json"
    if keys_file.exists():
        try:
            with open(keys_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_api_key(service_name: str, key_value: str) -> None:
    keys_file = config.state_dir / "api_keys.json"
    keys = get_all_api_keys()
    
    found = False
    for k in keys:
        if k['service'] == service_name:
            k['key'] = key_value
            found = True
            break
    if not found:
        keys.append({"service": service_name, "key": key_value})
    
    with open(keys_file, "w", encoding="utf-8") as f:
        json.dump(keys, f, ensure_ascii=False, indent=2)

def delete_api_key(service_name: str) -> None:
    keys_file = config.state_dir / "api_keys.json"
    keys = get_all_api_keys()
    keys = [k for k in keys if k['service'] != service_name]
    with open(keys_file, "w", encoding="utf-8") as f:
        json.dump(keys, f, ensure_ascii=False, indent=2)
