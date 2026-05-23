# skills/whatsapp_agent.py
import urllib.request
import urllib.parse
import json
import random
import time
from core.database import get_connection

def enviar_mensaje_evolution(instancia: str, apikey: str, numero: str, texto: str, evolution_url: str = "http://localhost:8080"):
    """
    Envía un mensaje de WhatsApp a través de Evolution API.
    """
    url = f"{evolution_url}/message/sendText/{instancia}"
    headers = {
        "apikey": apikey,
        "Content-Type": "application/json"
    }
    data = {
        "number": numero,
        "options": {
            "delay": random.randint(1000, 3000), # Pequeño delay de tipeo interno
            "presence": "composing"
        },
        "textMessage": {
            "text": texto
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return {"success": True, "data": res_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def enviar_multimedia_evolution(instancia: str, apikey: str, numero: str, media_url: str, caption: str, evolution_url: str = "http://localhost:8080"):
    """
    Envía una imagen o video por WhatsApp.
    """
    url = f"{evolution_url}/message/sendMedia/{instancia}"
    headers = {
        "apikey": apikey,
        "Content-Type": "application/json"
    }
    data = {
        "number": numero,
        "options": {
            "delay": random.randint(1500, 4000),
            "presence": "composing"
        },
        "mediaMessage": {
            "mediatype": "image", # Se asume imagen por ahora, pero puede ser 'video'
            "caption": caption,
            "media": media_url # Debe ser una URL pública o base64
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return {"success": True, "data": res_data}
    except Exception as e:
        return {"success": False, "error": str(e)}
