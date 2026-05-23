import os
import psutil
import zipfile
import subprocess
import shutil

def system_stats(params: dict) -> str:
    """Retorna estadisticas del sistema (RAM, CPU, Disco)."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    return f"CPU: {cpu}% | RAM Usada: {ram.percent}% ({ram.used / (1024**3):.2f} GB) | RAM Libre: {ram.available / (1024**3):.2f} GB"

def process_killer(params: dict) -> str:
    """Mata un proceso por su nombre."""
    target = params.get("process_name", "")
    killed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        if target.lower() in proc.info['name'].lower():
            try:
                psutil.Process(proc.info['pid']).terminate()
                killed += 1
            except:
                pass
    return f"Se mataron {killed} procesos que coinciden con '{target}'."

def zip_manager(params: dict) -> str:
    """Comprime un directorio o extrae un zip."""
    action = params.get("action")
    source = params.get("source")
    dest = params.get("destination")
    
    if action == "compress":
        shutil.make_archive(dest.replace('.zip', ''), 'zip', source)
        return f"Directorio {source} comprimido en {dest}."
    elif action == "extract":
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(dest)
        return f"Archivo {source} extraído en {dest}."
    return "Acción no válida."

def github_sync(params: dict) -> str:
    """Sube cambios a GitHub automáticamente."""
    commit_msg = params.get("message", "Auto-sync de Mónica")
    repo_path = params.get("repo_path", ".")
    try:
        subprocess.run("git add .", shell=True, cwd=repo_path, check=True)
        subprocess.run(f'git commit -m "{commit_msg}"', shell=True, cwd=repo_path, check=True)
        subprocess.run("git push", shell=True, cwd=repo_path, check=True)
        return "Sincronización con GitHub completada exitosamente."
    except Exception as e:
        return f"Error en sincronización GitHub: {str(e)}"

# Aquí dormirán 26 skills adicionales de productividad...
def execute_system_skill(skill_name: str, params: dict) -> str:
    skills = {
        "system_stats": system_stats,
        "process_killer": process_killer,
        "zip_manager": zip_manager,
        "github_sync": github_sync,
        # Stubs para el resto de la lista (dormidas hasta implementación futura)
        "clipboard_reader": lambda p: "Skill 'clipboard_reader' dormida/no implementada aún.",
        "app_launcher": lambda p: "Skill 'app_launcher' dormida.",
        "file_downloader": lambda p: "Skill 'file_downloader' dormida.",
        "api_fetcher": lambda p: "Skill 'api_fetcher' dormida.",
        "google_search": lambda p: "Skill 'google_search' dormida.",
        "pdf_analyzer": lambda p: "Skill 'pdf_analyzer' dormida.",
        "excel_parser": lambda p: "Skill 'excel_parser' dormida.",
        "email_scanner": lambda p: "Skill 'email_scanner' dormida.",
        "calendar_sync": lambda p: "Skill 'calendar_sync' dormida.",
        "notion_writer": lambda p: "Skill 'notion_writer' dormida.",
        "markdown_generator": lambda p: "Skill 'markdown_generator' dormida.",
        "notification_sender": lambda p: "Skill 'notification_sender' dormida.",
        "self_updater": lambda p: "Skill 'self_updater' dormida."
    }
    
    if skill_name in skills:
        try:
            return skills[skill_name](params)
        except Exception as e:
            return f"Error al ejecutar {skill_name}: {e}"
    else:
        return f"Skill {skill_name} no encontrada en system_ops."
