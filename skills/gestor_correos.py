# skills/gestor_correos.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario: str, asunto: str, cuerpo: str, remitente_email: str, remitente_password: str) -> str:
    """
    Envía un correo electrónico automatizado a través de SMTP (ej. Gmail).
    Requiere Email y Contraseña de Aplicación en el Búnker.
    """
    if not remitente_email or not remitente_password:
        return "Error: Credenciales de correo no configuradas."
        
    try:
        # Configuración por defecto para Gmail (se puede adaptar a Outlook/SMTP genérico)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        msg = MIMEMultipart()
        msg['From'] = remitente_email
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        print(f"[Gestor Correos] Conectando al servidor SMTP para enviar a {destinatario}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(remitente_email, remitente_password)
        server.send_message(msg)
        server.quit()
        
        return f"✅ Correo enviado con éxito a {destinatario}."
    except Exception as e:
        return f"Error al enviar correo: {str(e)}"
