# skills/agente_vigilante.py
import threading
import time
import inspect

# Registro de misiones activas
misiones_activas = {}

def _bucle_vigilante(nombre_mision: str, intervalo_segundos: int, funcion_tarea, kwargs_tarea: dict):
    print(f"[Vigilante] Agente '{nombre_mision}' desplegado. Trabajando de fondo cada {intervalo_segundos}s.")
    while misiones_activas.get(nombre_mision, False):
        try:
            print(f"[Vigilante] '{nombre_mision}' ejecutando tarea...")
            if inspect.iscoroutinefunction(funcion_tarea):
                import asyncio
                asyncio.run(funcion_tarea(**kwargs_tarea))
            else:
                funcion_tarea(**kwargs_tarea)
        except Exception as e:
            print(f"[Vigilante] Error en '{nombre_mision}': {e}")
        
        # Dormir en pequeños intervalos para permitir cancelación rápida
        for _ in range(intervalo_segundos):
            if not misiones_activas.get(nombre_mision, False):
                break
            time.sleep(1)
            
    print(f"[Vigilante] Agente '{nombre_mision}' desactivado y retirado.")

def delegar_agente(nombre_mision: str, intervalo_segundos: int, funcion_tarea, kwargs_tarea: dict):
    """
    Inicia un sub-agente en segundo plano (hilo) que ejecutará la 'funcion_tarea' repetidamente.
    """
    if nombre_mision in misiones_activas and misiones_activas[nombre_mision]:
        return f"El agente '{nombre_mision}' ya está patrullando."
        
    misiones_activas[nombre_mision] = True
    hilo = threading.Thread(target=_bucle_vigilante, args=(nombre_mision, intervalo_segundos, funcion_tarea, kwargs_tarea), daemon=True)
    hilo.start()
    return f"Agente '{nombre_mision}' activado exitosamente en segundo plano."

def detener_agente(nombre_mision: str):
    """
    Cancela la patrulla de un sub-agente en segundo plano.
    """
    if nombre_mision in misiones_activas:
        misiones_activas[nombre_mision] = False
        return f"Orden de retirada enviada al agente '{nombre_mision}'."
    return f"No se encontró al agente '{nombre_mision}'."

def listar_agentes():
    activos = [nombre for nombre, estado in misiones_activas.items() if estado]
    return f"Agentes activos: {', '.join(activos) if activos else 'Ninguno'}"
