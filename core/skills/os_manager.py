import os
import shutil
import hashlib
from pathlib import Path

async def os_list_dir(path: str) -> dict:
    """
    Lista los contenidos de un directorio.
    """
    try:
        p = Path(path)
        if not p.exists() or not p.is_dir():
            return {"error": f"La ruta {path} no existe o no es un directorio."}
        
        items = []
        for item in p.iterdir():
            items.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size_bytes": item.stat().st_size if item.is_file() else 0
            })
        return {"path": path, "items": items}
    except Exception as e:
        return {"error": str(e)}

async def os_manage_files(action: str, target: str, destination: str = None) -> dict:
    """
    Acciones soportadas: 'delete', 'move', 'copy', 'hash'
    """
    try:
        p = Path(target)
        if not p.exists():
            return {"error": f"El objetivo {target} no existe."}
            
        if action == "delete":
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            return {"success": True, "message": f"Eliminado: {target}"}
            
        elif action == "move":
            if not destination: return {"error": "Se requiere destino para mover."}
            shutil.move(str(p), destination)
            return {"success": True, "message": f"Movido a {destination}"}
            
        elif action == "copy":
            if not destination: return {"error": "Se requiere destino para copiar."}
            if p.is_dir():
                shutil.copytree(str(p), destination)
            else:
                shutil.copy2(str(p), destination)
            return {"success": True, "message": f"Copiado a {destination}"}
            
        elif action == "hash":
            if p.is_dir(): return {"error": "No se puede calcular hash de directorio."}
            h = hashlib.md5()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    h.update(chunk)
            return {"success": True, "hash": h.hexdigest(), "file": target}
            
        else:
            return {"error": f"Acción '{action}' no soportada."}
            
    except Exception as e:
        return {"error": str(e)}
