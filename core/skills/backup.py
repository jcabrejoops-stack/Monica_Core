import os
import zipfile
import shutil
from datetime import datetime
from config import config

async def backup_to_onedrive() -> str:
    """
    Comprime todo el proyecto actual (config.base_dir) y lo guarda en la bóveda
    de OneDrive (config.onedrive_path) con la fecha y hora actual.
    Ignora la carpeta 'venv' para ahorrar espacio y tiempo.
    """
    try:
        source_dir = config.base_dir
        dest_dir = config.onedrive_path
        
        # Crear la carpeta de respaldo si no existe
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = dest_dir / f"monica_backup_{timestamp}.zip"
        
        # Ignorar directorios pesados
        ignored_dirs = {"venv", "__pycache__", ".git"}
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                # Modificar dirs in-place para que os.walk ignore esas carpetas
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    # La ruta en el zip relativa a la carpeta base
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
                    
        return f"Copia de seguridad exitosa. Guardado en: {zip_filename}"
    except Exception as e:
        raise Exception(f"Error al realizar copia de seguridad: {e}")
