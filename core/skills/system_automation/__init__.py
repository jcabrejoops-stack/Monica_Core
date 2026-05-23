"""
Módulo de Automatización de Sistema.
Permite chequear el hardware y ejecutar comandos de forma segura.
"""
import subprocess
import logging

logger = logging.getLogger(__name__)

def check_system_health() -> dict:
    """
    Chequea el estado de CPU, RAM y disco duro de la computadora actual.
    """
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "success",
            "cpu_percent": cpu,
            "ram_percent": mem.percent,
            "ram_used_gb": round(mem.used / (1024**3), 2),
            "disk_percent": disk.percent
        }
    except ImportError:
        return {"status": "error", "message": "psutil no está instalado."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_terminal_command(command: str) -> dict:
    """
    Ejecuta un comando en la terminal local y devuelve su salida.
    (Atención: Requiere control estricto de seguridad).
    """
    try:
        # Timeout de 15 segundos para no colgar a Mónica
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        return {
            "status": "success",
            "command": command,
            "stdout": result.stdout[:1000], # Limitar longitud de respuesta
            "stderr": result.stderr[:1000],
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "El comando tardó demasiado y fue cancelado."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
