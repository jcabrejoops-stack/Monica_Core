# skills/buscar_clima.py
import urllib.request
import urllib.parse
import json

def obtener_clima(ciudad: str) -> str:
    """Busca el clima de una ciudad usando wttr.in y devuelve un resumen en texto plano."""
    try:
        url = f"https://wttr.in/{urllib.parse.quote(ciudad)}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            temp_c = data['current_condition'][0]['temp_C']
            desc = data['current_condition'][0]['lang_es'][0]['value'] if 'lang_es' in data['current_condition'][0] else data['current_condition'][0]['weatherDesc'][0]['value']
            return f"El clima actual en {ciudad} es {temp_c}°C con {desc}."
    except Exception as e:
        return f"Error al buscar el clima de {ciudad}: {str(e)}"
