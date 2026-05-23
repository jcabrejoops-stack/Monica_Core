# skills/notificador_movil.py
import urllib.request
import urllib.parse
import json

def enviar_telegram(mensaje: str, bot_token: str, chat_id: str) -> str:
    """
    Envía un mensaje instantáneo a tu celular vía Telegram.
    Requiere un Bot Token (creado con BotFather) y tu Chat ID.
    """
    if not bot_token or not chat_id:
        return "Error: Faltan credenciales. Configura Telegram_Bot_Token y Telegram_Chat_ID en el Búnker."
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get('ok'):
                return "✅ Notificación enviada al celular exitosamente."
            else:
                return f"Error de Telegram: {res_data.get('description')}"
    except Exception as e:
        return f"Error crítico al enviar notificación: {str(e)}"
