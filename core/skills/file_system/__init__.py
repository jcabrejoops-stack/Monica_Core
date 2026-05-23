"""
Módulo de Sistema de Archivos.
Permite organizar, buscar y manipular archivos localmente.
"""
import os
import shutil
import logging

logger = logging.getLogger(__name__)

def search_files(directory: str, keyword: str) -> dict:
    """
    Busca archivos por nombre dentro de un directorio y sus subdirectorios.
    """
    if not os.path.exists(directory):
        return {"status": "error", "message": f"El directorio {directory} no existe."}
        
    matches = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if keyword.lower() in file.lower():
                    matches.append(os.path.join(root, file))
        return {"status": "success", "keyword": keyword, "matches": matches[:100]} # Limitamos a 100
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_directory(directory: str) -> dict:
    """
    Crea un nuevo directorio.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return {"status": "success", "message": f"Directorio creado o ya existe: {directory}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def organize_by_extension(source_dir: str, target_dir: str) -> dict:
    """
    Organiza todos los archivos de un directorio en subcarpetas según su extensión.
    """
    if not os.path.exists(source_dir):
        return {"status": "error", "message": "Directorio de origen no existe."}
        
    try:
        os.makedirs(target_dir, exist_ok=True)
        files_moved = 0
        
        for file in os.listdir(source_dir):
            file_path = os.path.join(source_dir, file)
            if os.path.isfile(file_path):
                ext = file.split('.')[-1].lower() if '.' in file else 'misc'
                ext_dir = os.path.join(target_dir, ext)
                os.makedirs(ext_dir, exist_ok=True)
                
                shutil.move(file_path, os.path.join(ext_dir, file))
                files_moved += 1
                
        return {"status": "success", "files_moved": files_moved, "target": target_dir}
    except Exception as e:
        return {"status": "error", "message": str(e)}
