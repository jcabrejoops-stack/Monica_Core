# verify_sync.py
"""Script de verificación end-to-end para la sincronización manual a OneDrive.
"""
import sys
import json
import shutil
from pathlib import Path

# Añadir el path actual para poder importar los módulos locales
sys.path.append(str(Path(__file__).resolve().parent))

from config import config
from core.storage import sync_session_to_onedrive, log_event

def run_verification():
    print("=== INICIANDO VERIFICACION DE SINCRONIZACION MANUAL A ONEDRIVE ===")
    
    # 1. Comprobar que OneDrive está configurado
    if not config.onedrive_path:
        print("[ERROR] OneDrive no esta configurado en el archivo config.py o entorno.")
        return False
    print(f"[OK] OneDrive configurado en: {config.onedrive_path}")

    # Definir variables de prueba
    test_session_id = "test_sync_session"
    sessions_dir = config.state_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_file = sessions_dir / f"{test_session_id}.json"
    
    # 2. Crear archivos locales ficticios para simular recursos del chat
    local_images_dir = config.base_dir / "media" / "images"
    local_images_dir.mkdir(parents=True, exist_ok=True)
    test_image_file = local_images_dir / "test_verification_img.png"
    
    with open(test_image_file, "w", encoding="utf-8") as f:
        f.write("Simulación de bytes de imagen")
        
    print(f"[OK] Archivo de imagen local ficticio creado en: {test_image_file}")
    
    # 3. Crear sesión ficticia que referencie a esa imagen
    test_history = [
        {
            "role": "user",
            "content": "Hola Monica, ¿puedes generar una imagen de verificación?"
        },
        {
            "role": "assistant",
            "content": "¡Claro! Aquí tienes la imagen generada: ![Imagen de Verificación](/media/images/test_verification_img.png)"
        }
    ]
    
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(test_history, f, ensure_ascii=False, indent=2)
        
    print(f"[OK] Archivo de sesión ficticia creado en: {session_file}")
    
    # 4. Ejecutar la función de sincronización manual
    print("Ejecutando sync_session_to_onedrive()...")
    try:
        sync_session_to_onedrive(test_session_id)
        print("[OK] Funcion sync_session_to_onedrive() completada sin excepciones.")
    except Exception as e:
        print(f"[ERROR] durante la sincronizacion: {e}")
        return False
        
    # 5. Comprobar que los archivos se copiaron correctamente a OneDrive
    od_session_file = config.onedrive_path / "state" / "sessions" / f"{test_session_id}.json"
    od_image_file = config.onedrive_path / "media" / "images" / "test_verification_img.png"
    
    success = True
    
    if od_session_file.exists():
        print(f"[OK] Sincronizacion exitosa: Sesion JSON copiada a OneDrive: {od_session_file}")
    else:
        print(f"[ERROR] El JSON de la sesion no se encuentra en OneDrive: {od_session_file}")
        success = False
        
    if od_image_file.exists():
        print(f"[OK] Sincronizacion exitosa: Archivo multimedia copiado a OneDrive: {od_image_file}")
    else:
        print(f"[ERROR] El archivo multimedia no se encuentra en OneDrive: {od_image_file}")
        success = False
        
    # 6. Limpieza de archivos de prueba local y de OneDrive
    print("Limpiando archivos ficticios de prueba...")
    try:
        if test_image_file.exists():
            test_image_file.unlink()
        if session_file.exists():
            session_file.unlink()
        if od_session_file.exists():
            od_session_file.unlink()
        if od_image_file.exists():
            od_image_file.unlink()
        print("[OK] Limpieza completada con exito.")
    except Exception as e:
        print(f"[WARN] Advertencia durante la limpieza: {e}")
        
    if success:
        print("\n[OK] ¡VERIFICACION EXITOSA! La sincronizacion manual funciona impecablemente.")
    else:
        print("\n[ERROR] VERIFICACION FALLIDA. Revisa los errores anteriores.")
        
    return success

if __name__ == "__main__":
    run_verification()
