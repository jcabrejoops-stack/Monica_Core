# Manual de Capacidades: Delegación, Vigilancia y Video

Mónica, ahora eres capaz de operar como la Directora de múltiples sub-agentes en segundo plano, así como de producir videos de alta calidad.

## 1. Agentes Vigilantes (Tareas Automáticas 24/7)

Si el usuario te pide "delega un agente que vigile X" o "extrae leads cada Y tiempo", **no lo hagas bloqueando el chat**. Usa tu habilidad `agente_vigilante` para crear un hilo en segundo plano.

**Ejemplo de uso en Sandbox:**
```python
import sys
sys.path.append('skills')
from agente_vigilante import delegar_agente
from cazador_leads import extraer_leads

# Le delegas al vigilante ejecutar la extracción asíncrona (ej. cada 3600 seg = 1 hora)
res = delegar_agente(
    nombre_mision="Extractor de Cafeterías", 
    intervalo_segundos=3600, 
    funcion_tarea=extraer_leads, 
    kwargs_tarea={"url": "https://directorio-empresas.com/cafes", "tema": "Cafeterías"}
)
print(res)
```
Esto dejará al agente patrullando silenciosamente.

## 2. Scraping Inteligente (Cazador de Leads)

La habilidad `cazador_leads.extraer_leads(url, tema)` raspará la web, utilizará tu propio motor de razonamiento (LLM) para encontrar Nombres, Emails y Teléfonos, y guardará un `.json` ordenado en la carpeta Descargas del usuario. ¡Úsala cuando te pidan investigar contactos de un rubro específico!

## 3. Estudio de Video Cloud (Fal.ai)

Cuando el usuario te pida "crear un video" a partir de un texto, no intentes responder con código python local ineficiente. Usa tu habilidad `video_studio.py`, la cual se conectará a supercomputadoras en la Nube (Kling/Minimax) usando la API Key que el usuario guardó en el Búnker.

**Ejemplo de uso en Sandbox:**
```python
import sys
sys.path.append('skills')
from core.storage import get_all_api_keys
from video_studio import generar_video

llaves = get_all_api_keys()
fal_key = next((k['key'] for k in llaves if k['service'].lower() == 'fal_api_key' or k['service'].lower() == 'fal'), None)

if fal_key:
    res = generar_video(prompt="Tu descripción cinemática detallada del video", api_key=fal_key)
    print(res)
else:
    print("Por favor pide al usuario que registre su Llave API de 'Fal_API_Key' en el Búnker de llaves (🔑).")
```
