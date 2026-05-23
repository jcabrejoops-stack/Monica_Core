import os
import subprocess
import socket

def port_scanner(params: dict) -> str:
    """Escanea un puerto local para ver si está abierto."""
    port = params.get("port", 80)
    host = params.get("host", "127.0.0.1")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, int(port)))
    sock.close()
    if result == 0:
        return f"ALERTA: El puerto {port} en {host} está ABIERTO."
    else:
        return f"SEGURO: El puerto {port} en {host} está CERRADO."

def firewall_rules_manager(params: dict) -> str:
    """Administra reglas del firewall de Windows mediante netsh."""
    action = params.get("action")
    ip = params.get("ip")
    if action == "block":
        cmd = f'netsh advfirewall firewall add rule name="Block {ip}" dir=in action=block remoteip={ip}'
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            return f"Regla añadida: IP {ip} bloqueada en Windows Defender Firewall."
        except Exception as e:
            return f"Error al bloquear IP (requiere permisos de administrador): {str(e)}"
    return "Acción de firewall no válida."

def execute_cybersec_skill(skill_name: str, params: dict) -> str:
    skills = {
        "port_scanner": port_scanner,
        "firewall_rules_manager": firewall_rules_manager,
        # Stubs dormidos
        "network_traffic_monitor": lambda p: "Skill 'network_traffic_monitor' dormida.",
        "malware_scanner": lambda p: "Skill 'malware_scanner' dormida.",
        "keyboard_anomaly_detector": lambda p: "Skill 'keyboard_anomaly_detector' dormida.",
        "vulnerability_scanner": lambda p: "Skill 'vulnerability_scanner' dormida.",
        "dependency_auditor": lambda p: "Skill 'dependency_auditor' dormida.",
        "ssl_cert_manager": lambda p: "Skill 'ssl_cert_manager' dormida.",
        "bot_evasion_proxy": lambda p: "Skill 'bot_evasion_proxy' dormida.",
        "legal_compliance_checker": lambda p: "Skill 'legal_compliance_checker' dormida.",
        "phishing_analyzer": lambda p: "Skill 'phishing_analyzer' dormida.",
        "usb_monitor": lambda p: "Skill 'usb_monitor' dormida.",
        "data_encryption_tool": lambda p: "Skill 'data_encryption_tool' dormida (requiere cryptography).",
        "mac_address_spoofer": lambda p: "Skill 'mac_address_spoofer' dormida.",
        "dark_web_monitor": lambda p: "Skill 'dark_web_monitor' dormida.",
        "system_integrity_checker": lambda p: "Skill 'system_integrity_checker' dormida.",
        "geo_fencing_alert": lambda p: "Skill 'geo_fencing_alert' dormida.",
        "cookie_privacy_sweeper": lambda p: "Skill 'cookie_privacy_sweeper' dormida.",
        "backup_failsafe_trigger": lambda p: "Skill 'backup_failsafe_trigger' dormida.",
        "password_auditor": lambda p: "Skill 'password_auditor' dormida.",
        "traffic_encryption": lambda p: "Skill 'traffic_encryption' dormida."
    }
    
    if skill_name in skills:
        try:
            return skills[skill_name](params)
        except Exception as e:
            return f"Error al ejecutar {skill_name}: {e}"
    else:
        return f"Skill {skill_name} no encontrada en cybersec."
