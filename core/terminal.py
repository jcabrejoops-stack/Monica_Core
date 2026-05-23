# core/terminal.py
"""Módulo de ejecución de comandos en terminal para Mónica.

Permite a Mónica:
- Ejecutar cualquier comando en PowerShell o CMD.
- Instalar programas (pip, npm, winget, choco, etc.).
- Crear archivos y directorios.
- Compilar y ejecutar código.
- Gestionar procesos del sistema.

Todos los comandos se registran en el sistema de logs para trazabilidad.
"""
import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime

from config import config

logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

# Directorio de trabajo por defecto para los comandos.
DEFAULT_CWD = str(config.base_dir)

# Directorio donde Mónica guarda el software que crea.
PROJECTS_DIR = config.onedrive_path / "proyectos"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


async def execute_command(command: str, cwd: str | None = None, timeout: int = 120) -> dict:
    """Ejecuta un comando en PowerShell y devuelve el resultado.

    Parameters
    ----------
    command : str
        Comando a ejecutar (se ejecuta en PowerShell).
    cwd : str | None
        Directorio de trabajo. Si es None, usa DEFAULT_CWD.
    timeout : int
        Tiempo máximo de ejecución en segundos.

    Returns
    -------
    dict
        Diccionario con: 'success', 'stdout', 'stderr', 'exit_code', 'command', 'cwd'.
    """
    work_dir = cwd or DEFAULT_CWD
    logger.info(f"Ejecutando comando: {command}")
    logger.info(f"Directorio: {work_dir}")

    try:
        process = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-NonInteractive", "-Command", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        stderr_text = stderr.decode("utf-8", errors="replace").strip()
        exit_code = process.returncode

        result = {
            "success": exit_code == 0,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "exit_code": exit_code,
            "command": command,
            "cwd": work_dir,
        }

        if exit_code == 0:
            logger.info(f"Comando exitoso (código {exit_code})")
        else:
            logger.warning(f"Comando falló (código {exit_code}): {stderr_text[:200]}")

        return result

    except asyncio.TimeoutError:
        logger.error(f"Timeout ({timeout}s) al ejecutar: {command}")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Timeout: el comando excedió los {timeout} segundos.",
            "exit_code": -1,
            "command": command,
            "cwd": work_dir,
        }
    except Exception as exc:
        logger.error(f"Error ejecutando comando: {exc}")
        return {
            "success": False,
            "stdout": "",
            "stderr": str(exc),
            "exit_code": -1,
            "command": command,
            "cwd": work_dir,
        }


async def install_package(package_manager: str, package_name: str) -> dict:
    """Instala un paquete usando el gestor indicado.

    Gestores soportados:
    - pip: paquetes de Python.
    - npm: paquetes de Node.js.
    - winget: aplicaciones de Windows.
    - choco: paquetes de Chocolatey.

    Returns
    -------
    dict
        Resultado de la instalación.
    """
    commands = {
        "pip": f"pip install {package_name}",
        "npm": f"npm install -g {package_name}",
        "winget": f"winget install -e --accept-package-agreements --accept-source-agreements {package_name}",
        "choco": f"choco install {package_name} -y",
    }

    cmd = commands.get(package_manager.lower())
    if not cmd:
        return {
            "success": False,
            "stderr": f"Gestor de paquetes '{package_manager}' no soportado. Usa: pip, npm, winget, choco.",
            "exit_code": -1,
        }

    logger.info(f"Instalando {package_name} con {package_manager}...")
    return await execute_command(cmd)


async def create_file(filepath: str, content: str) -> dict:
    """Crea un archivo con el contenido especificado.

    Parameters
    ----------
    filepath : str
        Ruta del archivo a crear (relativa a PROJECTS_DIR o absoluta).
    content : str
        Contenido del archivo.

    Returns
    -------
    dict
        Resultado con 'success', 'filepath', 'message'.
    """
    try:
        path = Path(filepath)
        if not path.is_absolute():
            path = PROJECTS_DIR / path

        # Crear directorios padre si no existen.
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Archivo creado: {path}")
        return {
            "success": True,
            "filepath": str(path),
            "message": f"Archivo creado exitosamente: {path}",
        }
    except Exception as exc:
        logger.error(f"Error creando archivo {filepath}: {exc}")
        return {
            "success": False,
            "filepath": filepath,
            "message": f"Error: {exc}",
        }


async def create_project(project_name: str, project_type: str = "python") -> dict:
    """Crea la estructura base de un proyecto nuevo.

    Tipos soportados:
    - python: crea main.py, requirements.txt, README.md
    - web: crea index.html, style.css, script.js
    - node: ejecuta npm init -y

    Returns
    -------
    dict
        Resultado con 'success', 'project_dir', 'files_created'.
    """
    project_dir = PROJECTS_DIR / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    files_created = []

    if project_type == "python":
        templates = {
            "main.py": f'# {project_name}\n# Creado por Mónica\n\ndef main():\n    print("¡Hola desde {project_name}!")\n\nif __name__ == "__main__":\n    main()\n',
            "requirements.txt": "# Dependencias del proyecto\n",
            "README.md": f"# {project_name}\n\nProyecto creado por Mónica – Agente IA.\n",
        }
        for fname, content in templates.items():
            fpath = project_dir / fname
            fpath.write_text(content, encoding="utf-8")
            files_created.append(str(fpath))

    elif project_type == "web":
        templates = {
            "index.html": f'<!DOCTYPE html>\n<html lang="es">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{project_name}</title>\n    <link rel="stylesheet" href="style.css">\n</head>\n<body>\n    <h1>{project_name}</h1>\n    <p>Creado por Mónica</p>\n    <script src="script.js"></script>\n</body>\n</html>\n',
            "style.css": f"/* {project_name} - Estilos */\n* {{ margin: 0; padding: 0; box-sizing: border-box; }}\nbody {{ font-family: 'Inter', sans-serif; background: #0f172a; color: #e2e8f0; display: flex; align-items: center; justify-content: center; min-height: 100vh; }}\nh1 {{ font-size: 2rem; background: linear-gradient(135deg, #6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}\n",
            "script.js": f'// {project_name} - JavaScript\nconsole.log("¡{project_name} cargado!");\n',
        }
        for fname, content in templates.items():
            fpath = project_dir / fname
            fpath.write_text(content, encoding="utf-8")
            files_created.append(str(fpath))

    elif project_type == "node":
        result = await execute_command("npm init -y", cwd=str(project_dir))
        files_created.append(str(project_dir / "package.json"))

    logger.info(f"Proyecto '{project_name}' creado en {project_dir}")
    return {
        "success": True,
        "project_dir": str(project_dir),
        "project_type": project_type,
        "files_created": files_created,
    }


async def list_projects() -> list[dict]:
    """Lista todos los proyectos creados por Mónica."""
    projects = []
    if PROJECTS_DIR.exists():
        for item in PROJECTS_DIR.iterdir():
            if item.is_dir():
                files = list(item.rglob("*"))
                projects.append({
                    "name": item.name,
                    "path": str(item),
                    "files_count": len([f for f in files if f.is_file()]),
                })
    return projects
