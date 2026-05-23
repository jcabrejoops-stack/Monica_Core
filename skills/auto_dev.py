# skills/auto_dev.py
import os
import subprocess
import time
from core.llm import call_llm

async def crear_app_web(descripcion: str, nombre_proyecto: str = "mi_app"):
    """
    Toma una descripción de una aplicación web, genera todo el código (HTML, CSS, JS) 
    usando Inteligencia Artificial, crea la estructura de carpetas y levanta un servidor web local.
    """
    print(f"[Auto-Dev] Diseñando la arquitectura para: '{descripcion}'...")
    
    prompt = (
        f"Eres un Desarrollador Web Senior. Escribe el código completo para una aplicación web basada en esta descripción: '{descripcion}'.\n"
        f"Usa HTML, CSS moderno y Vanilla JavaScript. Todo en un solo archivo index.html para fácil despliegue.\n"
        f"No pongas formato markdown (```html), devuelve SOLO el código en bruto, listo para guardar."
    )
    
    try:
        # Usamos el motor híbrido para tener máxima inteligencia
        codigo_app = await call_llm(prompt, engine="hybrid")
        codigo_app = codigo_app.replace("```html", "").replace("```", "").strip()
        
        # Crear la carpeta del proyecto en el Escritorio
        base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Monica_Proyectos", nombre_proyecto)
        os.makedirs(base_dir, exist_ok=True)
        
        archivo_index = os.path.join(base_dir, "index.html")
        with open(archivo_index, "w", encoding="utf-8") as f:
            f.write(codigo_app)
            
        print(f"[Auto-Dev] Código generado y guardado en {archivo_index}")
        
        # Levantar el servidor web local
        puerto = 8080 + int(time.time() % 1000) # Puerto aleatorio
        comando = f"start cmd.exe /k \"cd {base_dir} && python -m http.server {puerto}\""
        subprocess.Popen(comando, shell=True)
        
        # Abrir el navegador automáticamente
        import webbrowser
        webbrowser.open(f"http://localhost:{puerto}")
        
        return f"¡Aplicación '{nombre_proyecto}' creada! Servidor levantado en http://localhost:{puerto} y archivo guardado en el Escritorio."
        
    except Exception as e:
        return f"Error en el Auto-Desarrollador: {e}"
