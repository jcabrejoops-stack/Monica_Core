"""
Módulo de Productividad.
Permite enviar/leer correos y gestionar el calendario.
"""
import smtplib
from email.mime.text import MIMEText
import datetime
import logging

logger = logging.getLogger(__name__)

def draft_email(to_email: str, subject: str, body: str) -> dict:
    """
    Redacta y prepara un correo electrónico. En una configuración real,
    podría enviarlo vía SMTP. Por seguridad, aquí lo devuelve como borrador listo.
    """
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = to_email
        msg['From'] = "monica@tu-agente-local.com"
        
        return {
            "status": "success",
            "message": "Borrador generado",
            "email_raw": msg.as_string()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_today_schedule() -> dict:
    """
    Simula la lectura de un calendario local.
    """
    now = datetime.datetime.now()
    return {
        "status": "success",
        "date": now.strftime("%Y-%m-%d"),
        "events": [
            {"time": "10:00 AM", "title": "Revisión de código con Mónica"},
            {"time": "02:30 PM", "title": "Reunión de planificación"}
        ]
    }
