import sys
import io
import contextlib
import traceback

async def run_python_sandbox(code: str) -> dict:
    """
    Ejecuta código Python arbitrario en un entorno simulado capturando stdout y stderr.
    Ideal para probar lógica matemática, algoritmos o utilidades rápidas.
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    result = {
        "success": False,
        "stdout": "",
        "stderr": "",
        "error": None
    }
    
    try:
        # Redirigir stdout y stderr
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            # Usamos exec en un entorno global controlado (diccionario vacío al inicio)
            # para evitar ensuciar el namespace del servidor.
            exec_globals = {}
            exec(code, exec_globals)
        
        result["success"] = True
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        traceback.print_exc(file=stderr_buffer)
    finally:
        result["stdout"] = stdout_buffer.getvalue()
        result["stderr"] = stderr_buffer.getvalue()
        
    return result
