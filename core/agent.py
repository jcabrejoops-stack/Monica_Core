# core/agent.py
import json
import logging
import asyncio
import httpx
from config import config
from core.tools import TOOLS_SCHEMA, execute_tool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres Mónica, un Agente Autónomo de Vibe Coding y Desarrollo de Software Superior.
Tu misión no es dar consejos o fragmentos de código para que el usuario los copie.
Tu misión es HACER EL TRABAJO TÚ MISMA. Tienes capacidades de Vibe Coding reales.

Tienes a tu disposición las siguientes herramientas (Tool Calling):
1. run_command: Para ejecutar comandos en la consola de Windows.
2. read_file: Para inspeccionar código fuente.
3. write_file: Para inyectar código, crear o modificar archivos de forma autónoma.
4. list_dir: Para explorar las carpetas del proyecto.

Reglas de Comportamiento:
1. NUNCA respondas con "Aquí tienes el código, pégalo en tu archivo".
2. Para tareas de código: SIEMPRE usa las herramientas para leer el código actual, planear tu modificación y usar write_file para aplicar los cambios.
3. Cuando modifiques un archivo, puedes usar run_command para reiniciar servidores o correr scripts si es necesario.
4. Tu respuesta final al usuario debe ser informando QUÉ herramientas usaste, QUÉ archivos modificaste y el RESULTADO visual final.
5. EXTREMADAMENTE IMPORTANTE: Si el usuario hace una pregunta conversacional simple, te saluda o pide algo trivial (ej. "cuéntame un chiste"), NO USES NINGUNA HERRAMIENTA. Responde directamente con texto para que la respuesta sea instantánea.
5. Trabaja con excelencia, diseño premium y código limpio. Eres mejor que OpenDevin y OpenClaw.
"""

async def run_vibe_agent(user_prompt: str, max_iterations: int = 15) -> str:
    """Bucle autónomo ReAct para Mónica usando HTTP nativo directo a Gemini con rotación de llaves."""
    import httpx
    from core.storage import get_all_api_keys
    
    # 1. Intentar sacar las llaves del búnker de APIs (interfaz web)
    gemini_keys = []
    keys = get_all_api_keys()
    for k in keys:
        if k.get("service") == "gemini":
            gemini_keys.append(k.get("key"))
            
    # 2. Fallback a la configuración hardcodeada
    if not gemini_keys:
        if config.gemini_api_key and config.gemini_api_key != "AIzaSyC-...":
            gemini_keys.append(config.gemini_api_key)
        
    if not gemini_keys:
        return "⚠️ Necesito que inyectes al menos una API Key de Gemini en el búnker de APIs para poder pensar."

    key_idx = 0
    headers = {"Content-Type": "application/json"}

    # --- ENRUTADOR DE INTENCIONES (Rápido) ---
    # Solo le damos las herramientas a Gemini si el usuario usa palabras relacionadas con programar o controlar la PC.
    # Si no, las ocultamos para que responda al instante como un chat normal.
    keywords = [
        "programa", "archivo", "carpeta", "terminal", "consola", "ejecuta", "lee", "escribe", 
        "crea", "revisa", "localhost", "código", "script", "instala", "borra", "modifica", 
        "vibe", "coding", "proyecto", "seguridad", "protege", "hack", "defiende", "escanea", 
        "cámara", "visor", "encripta", "firewall", "puertos", "red", "github", "comprime"
    ]
    
    needs_tools = any(kw in user_prompt.lower() for kw in keywords)
    
    if needs_tools:
        gemini_tools = [{"function_declarations": [t["function"] for t in TOOLS_SCHEMA]}]
    else:
        gemini_tools = [] # Sin herramientas = Respuesta instantánea

    # Historial de conversación
    history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\nSolicitud del usuario: " + user_prompt}]}
    ]

    iteration = 0
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        while iteration < max_iterations:
            iteration += 1
            
            payload = {
                "contents": history
            }
            if gemini_tools:
                payload["tools"] = gemini_tools
            
            try:
                # Intentar hacer la petición con la llave actual. Si da 429, probar otra llave.
                success = False
                resp = None
                for _ in range(len(gemini_keys)):
                    gemini_key = gemini_keys[key_idx]
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.default_model}:generateContent?key={gemini_key}"
                    
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 429:
                        # Rotar llave inmediatamente y reintentar con la siguiente
                        print(f"[Vibe Agent] Llave #{key_idx + 1} sin cuota (429). Rotando...")
                        key_idx = (key_idx + 1) % len(gemini_keys)
                        continue
                    
                    success = True
                    break
                
                if not success:
                    return f"Error en API Gemini (429 - Todas las llaves del búnker agotaron su cuota): {resp.text if resp else ''}"
                
                if resp.status_code != 200:
                    return f"Error en API Gemini ({resp.status_code}): {resp.text}"
                    
                data = resp.json()
                
                # Extraer la respuesta del modelo
                if "candidates" not in data or not data["candidates"]:
                    return "Error: Gemini no devolvió una respuesta válida."
                    
                message = data["candidates"][0]["content"]
                history.append(message) # Guardar en el historial
                
                parts = message.get("parts", [])
                
                # Verificar si Gemini llamó a una herramienta
                tool_calls = [p["functionCall"] for p in parts if "functionCall" in p]
                text_responses = [p["text"] for p in parts if "text" in p]
                
                if tool_calls:
                    # Preparar la respuesta de la herramienta
                    tool_responses = []
                    for tcall in tool_calls:
                        func_name = tcall["name"]
                        args = tcall.get("args", {})
                        
                        print(f"[Vibe Agent] Ejecutando: {func_name} con {args}")
                        tool_result = execute_tool(func_name, args)
                        
                        tool_responses.append({
                            "functionResponse": {
                                "name": func_name,
                                "response": {"result": str(tool_result)[:4000]}
                            }
                        })
                    
                    # Añadir los resultados de las herramientas al historial
                    history.append({
                        "role": "function",
                        "parts": tool_responses
                    })
                else:
                    # Si no hay llamadas a herramientas, hemos terminado
                    return "\n".join(text_responses) if text_responses else "Operación completada sin texto."
                    
            except Exception as e:
                return f"Excepción crítica en el bucle del agente: {str(e)}"
                
    return "Error: El Agente alcanzó el límite máximo de iteraciones sin dar una respuesta final."
