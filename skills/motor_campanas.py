# skills/motor_campanas.py
import time
import random
import json
from core.database import get_connection
from skills.whatsapp_agent import enviar_mensaje_evolution

def ruido_tiempo(minutos_base: float) -> float:
    """Añade un factor de aleatoriedad del +/- 20% al tiempo base en minutos, para evitar bloqueos por SPAM."""
    ruido = minutos_base * random.uniform(0.8, 1.2)
    return ruido * 60 # Convertir a segundos

def procesar_prospeccion(instancia: str, apikey: str, url_api: str, minutos_lapso: float):
    """
    Busca leads en estado 'Nuevos' y les envía el primer mensaje, pasándolos a 'Prospectado'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener el mensaje base desde las configuraciones (esto vendrá del UI en el futuro)
    cursor.execute("SELECT * FROM leads WHERE estado = 'Nuevos' LIMIT 5")
    nuevos_leads = cursor.fetchall()
    
    for lead in nuevos_leads:
        telefono = lead['telefono']
        nombre = lead['nombre']
        
        # Simulación: Si tuviéramos un JSON de variantes en la DB, lo escogeríamos aquí
        mensajes_posibles = [
            f"Hola {nombre}, un gusto saludarte. ¿Cómo va todo en tu negocio?",
            f"¡Hola {nombre}! Quería contactarte brevemente. ¿Tienes unos minutos?",
            f"Buenas {nombre}. Encontré tu perfil y me pareció muy interesante."
        ]
        texto = random.choice(mensajes_posibles)
        
        print(f"[Motor Anti-Ban] Prospectando a {nombre} ({telefono})...")
        res = enviar_mensaje_evolution(instancia, apikey, telefono, texto, url_api)
        
        if res.get("success"):
            cursor.execute("UPDATE leads SET estado = 'Prospectado', ultima_interaccion = CURRENT_TIMESTAMP WHERE id = ?", (lead['id'],))
            conn.commit()
            print(f"✅ Éxito. Esperando lapso seguro...")
            time.sleep(ruido_tiempo(minutos_lapso))
        else:
            print(f"❌ Error al enviar: {res.get('error')}")
            
    conn.close()

# Esta función podrá ser llamada en un Hilo (Threading) por el web_app.py cuando el usuario pulse '▶'
