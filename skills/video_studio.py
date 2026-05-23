# skills/video_studio.py
import urllib.request
import urllib.parse
import json
import time
import os

def generar_video(prompt: str, api_key: str, output_name: str = "generado") -> str:
    """
    Se conecta a la API de Fal.ai (Kling o Minimax) para generar video desde texto.
    Descarga el video resultante en la carpeta 'Videos' del usuario.
    """
    print(f"Iniciando renderizado en la Nube (Fal.ai). Prompt: '{prompt}'")
    
    # Usaremos Minimax Text-to-Video como ejemplo por su alta calidad y velocidad en Fal.ai
    # (El usuario debe tener saldo en fal.ai)
    url = "https://queue.fal.run/fal-ai/minimax-video"
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = json.dumps({
        "prompt": prompt,
        "aspect_ratio": "16:9"
    }).encode('utf-8')
    
    try:
        # Enviar petición a la cola
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            queue_data = json.loads(response.read().decode('utf-8'))
            request_id = queue_data.get('request_id')
            
        if not request_id:
            return "Error: No se recibió ID de tarea de Fal.ai"
            
        # Hacer polling (vigilar el estado en la cola)
        status_url = f"https://queue.fal.run/fal-ai/minimax-video/requests/{request_id}"
        req_status = urllib.request.Request(status_url, headers=headers)
        
        while True:
            with urllib.request.urlopen(req_status) as res:
                status_data = json.loads(res.read().decode('utf-8'))
                status = status_data.get("status")
                
                if status == "COMPLETED":
                    video_url = status_data['response_url'] if 'response_url' in status_data else status_data.get('video_url', '')
                    # A veces la url final viene anidada, intentamos extraerla
                    if 'video' in status_data:
                        video_url = status_data['video']['url']
                    elif 'video_url' not in status_data and 'response_url' not in status_data:
                        # Fetch the final response URL
                        final_res = urllib.request.urlopen(urllib.request.Request(status_url, headers=headers))
                        final_data = json.loads(final_res.read().decode('utf-8'))
                        # Asumiendo estructura estándar de Fal.ai
                        pass # simplification
                        
                    # Descargar el video
                    download_url = status_data.get('video', {}).get('url') or status_data.get('url')
                    if download_url:
                        output_dir = os.path.join(os.path.expanduser("~"), "Videos", "Monica_Studio")
                        os.makedirs(output_dir, exist_ok=True)
                        filepath = os.path.join(output_dir, f"{output_name}_{int(time.time())}.mp4")
                        
                        print(f"Descargando video desde {download_url}...")
                        urllib.request.urlretrieve(download_url, filepath)
                        return f"¡Video generado con éxito! Guardado en: {filepath}"
                    else:
                        return f"Proceso completado, pero no se encontró la URL de descarga. Data: {status_data}"
                        
                elif status == "FAILED":
                    return f"Error en la generación del video: {status_data.get('error')}"
                else:
                    # IN_QUEUE o IN_PROGRESS
                    time.sleep(3)
                    
    except Exception as e:
        return f"Error crítico al conectar con el estudio de video: {e}"
