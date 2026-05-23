# core/tools.py
import os
import subprocess
import json

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.expanduser("~"), "Monica_Proyectos"))

def init_workspace():
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

# Inicializar espacio seguro
init_workspace()

def is_safe_path(path: str) -> bool:
    """Verifica si la ruta está dentro del espacio de trabajo permitido para evitar destrucción accidental del OS."""
    # Para ser flexibles durante el desarrollo y a petición del usuario, permitimos acceder a C:\Users\jcabr\Monica_Core
    # O cualquier ruta si el usuario le da la instrucción explícita. Por ahora, confiamos en la IA.
    return True

def run_command(command: str) -> str:
    """Ejecuta un comando de consola en Windows (PowerShell/CMD)."""
    try:
        # Ejecutar de forma segura con un timeout
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        output = result.stdout + "\n" + result.stderr
        return output.strip() if output.strip() else "Comando ejecutado exitosamente sin salida de texto."
    except subprocess.TimeoutExpired:
        return "Error: Tiempo de ejecución excedido (Timeout > 120s)."
    except Exception as e:
        return f"Error ejecutando comando: {str(e)}"

def read_file(filepath: str) -> str:
    """Lee el contenido de un archivo."""
    try:
        path = os.path.abspath(filepath)
        if not os.path.exists(path):
            return f"Error: El archivo {filepath} no existe."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error leyendo archivo: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Escribe contenido en un archivo (crea carpetas si no existen)."""
    try:
        path = os.path.abspath(filepath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Archivo {filepath} guardado exitosamente."
    except Exception as e:
        return f"Error escribiendo archivo: {str(e)}"

def list_dir(directory: str) -> str:
    """Lista los archivos y carpetas de un directorio."""
    try:
        path = os.path.abspath(directory)
        if not os.path.exists(path):
            return f"Error: El directorio {directory} no existe."
        items = os.listdir(path)
        return "\n".join(items) if items else "Directorio vacío."
    except Exception as e:
        return f"Error leyendo directorio: {str(e)}"


# Definición de herramientas para la API de Groq/OpenRouter
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Ejecuta un comando de consola en Windows (cmd/powershell). Útil para iniciar servidores, instalar paquetes npm/pip, o usar utilidades de línea de comandos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "El comando a ejecutar. Ejemplo: 'npm install' o 'dir'"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lee y devuelve el contenido de un archivo en el disco duro.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Ruta absoluta o relativa del archivo a leer."
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Escribe o sobrescribe un archivo con código o texto. Si la carpeta no existe, la crea.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Ruta absoluta o relativa donde se guardará el archivo."
                    },
                    "content": {
                        "type": "string",
                        "description": "El contenido completo a escribir en el archivo."
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "Lista los archivos y carpetas dentro de un directorio específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "La ruta del directorio a explorar."
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "advanced_skill",
            "description": "Ejecuta una de las 50 skills avanzadas de Mónica (Defensa Hacker, Visión Matemática, Operaciones de Sistema). Úsala si el usuario pide hackear, escanear, proteger, comprimir, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Categoría de la skill: 'system', 'cybersec', o 'vision'"
                    },
                    "skill_name": {
                        "type": "string",
                        "description": "Nombre exacto de la skill (ej. 'port_scanner', 'firewall_rules_manager', 'process_killer', 'zip_manager', 'github_sync', 'webcam_intruder_detector')"
                    },
                    "params": {
                        "type": "string",
                        "description": "Un string JSON con los parámetros que necesite la skill."
                    }
                },
                "required": ["category", "skill_name", "params"]
            }
        }
    }
]

def execute_tool(name: str, args: dict) -> str:
    """Enrutador maestro de ejecución de herramientas."""
    if name == "run_command":
        return run_command(args.get("command", ""))
    elif name == "read_file":
        return read_file(args.get("filepath", ""))
    elif name == "write_file":
        return write_file(args.get("filepath", ""), args.get("content", ""))
    elif name == "list_dir":
        return list_dir(args.get("directory", ""))
    elif name == "advanced_skill":
        cat = args.get("category", "")
        skill = args.get("skill_name", "")
        import json
        try:
            params = json.loads(args.get("params", "{}"))
        except:
            params = {}
            
        if cat == "system":
            from core.skills.system_ops import execute_system_skill
            return execute_system_skill(skill, params)
        elif cat == "cybersec":
            from core.skills.cybersec import execute_cybersec_skill
            return execute_cybersec_skill(skill, params)
        elif cat == "vision":
            from core.skills.vision_math import execute_vision_skill
            return execute_vision_skill(skill, params)
        return "Categoría de skill inválida."
    else:
        return f"Error: Herramienta desconocida '{name}'"
