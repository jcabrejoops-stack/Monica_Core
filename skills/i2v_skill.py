# skills/i2v_skill.py
import os
import asyncio
import base64
import time
import httpx
from pathlib import Path
from core.storage import log_event, get_all_api_keys

class CloudI2VSkill:
    """
    Skill de Image-to-Video (I2V) usando APIs Gratuitas de Nube.
    Implementación Safe Hardware para PCs de bajos recursos.
    """
    def __init__(self):
        # Usamos un modelo open-source en HF (Ejemplo: LTX-Video o I2VGen-XL)
        self.api_url = "https://api-inference.huggingface.co/models/ali-vilab/i2vgen-xl"
        
    def get_hf_key(self):
        keys = get_all_api_keys()
        return next((k['key'] for k in keys if k['service'].lower() in ('huggingface', 'hf')), None)

    async def animate_image(self, image_path: str, prompt: str, output_name: str = "i2v_output.mp4") -> dict:
        """
        Envía la imagen y el prompt a la nube gratuita y devuelve la ruta del video.
        """
        path = Path(image_path)
        if not path.exists():
            return {"success": False, "error": f"Archivo de imagen no encontrado: {image_path}"}
            
        hf_key = self.get_hf_key()
        if not hf_key:
            return {
                "success": False, 
                "error": "Mónica requiere una API Key de HuggingFace en el Búnker (Llave) para animar imágenes sin usar tu memoria RAM. Es gratis en huggingface.co."
            }

        headers = {"Authorization": f"Bearer {hf_key}"}
        
        # Leer la imagen
        with open(path, "rb") as f:
            image_data = f.read()
            
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "inputs": {
                "image": image_b64,
                "text": prompt
            },
            "parameters": {
                "num_inference_steps": 20
            }
        }

        output_dir = Path("media/video")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{int(time.time())}_{output_name}"

        log_event(f"[I2V Skill] Iniciando animación de {path.name} en la nube (Hardware Seguro)...")
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(self.api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    # Guardar el binario del video
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    log_event(f"[I2V Skill] Video animado descargado con éxito: {output_file}")
                    return {"success": True, "path": str(output_file)}
                    
                elif response.status_code == 503:
                    # El modelo está cargando en HF
                    return {"success": False, "error": "El modelo de video está arrancando en los servidores de la nube. Intenta de nuevo en 2 minutos."}
                else:
                    error_msg = response.text
                    return {"success": False, "error": f"Error de la nube ({response.status_code}): {error_msg}"}
                    
            except httpx.TimeoutException:
                return {"success": False, "error": "Tiempo de espera excedido. La generación de video está tomando demasiado tiempo en la nube gratuita."}
            except Exception as e:
                return {"success": False, "error": f"Error crítico de red: {e}"}

# Instancia global para ser usada por web_app.py u otros módulos
i2v_agent = CloudI2VSkill()
