# skills/calendario.py
import os
import time
from datetime import datetime, timedelta
try:
    from icalendar import Calendar, Event, vText
except ImportError:
    pass

def agendar_reunion(titulo: str, descripcion: str, fecha_hora_inicio: str, duracion_minutos: int = 60) -> str:
    """
    Genera un archivo de evento de calendario (.ics) compatible con Google Calendar, 
    Outlook y Apple Calendar.
    Formato fecha_hora_inicio esperado: 'YYYY-MM-DD HH:MM' (ej: '2026-05-24 15:30')
    """
    try:
        from icalendar import Calendar, Event, vText
    except ImportError:
        return "Error: la librería 'icalendar' no está instalada."

    try:
        inicio = datetime.strptime(fecha_hora_inicio, "%Y-%m-%d %H:%M")
        fin = inicio + timedelta(minutes=duracion_minutos)
        
        cal = Calendar()
        cal.add('prodid', '-//Monica AI Calendar Agent//mxm.dk//')
        cal.add('version', '2.0')
        
        evento = Event()
        evento.add('summary', titulo)
        evento.add('description', descripcion)
        evento.add('dtstart', inicio)
        evento.add('dtend', fin)
        evento.add('dtstamp', datetime.now())
        
        cal.add_component(evento)
        
        # Guardar archivo
        output_dir = os.path.join(os.path.expanduser("~"), "Documentos", "Monica_Calendario")
        os.makedirs(output_dir, exist_ok=True)
        
        nombre_seguro = titulo.replace(" ", "_").replace("/", "-")
        filepath = os.path.join(output_dir, f"Evento_{nombre_seguro}_{int(time.time())}.ics")
        
        with open(filepath, 'wb') as f:
            f.write(cal.to_ical())
            
        # Intentar abrir el archivo para que se añada automáticamente al calendario por defecto del sistema
        import subprocess
        try:
            os.startfile(filepath) # Exclusivo de Windows
        except AttributeError:
            subprocess.call(['open', filepath]) # Mac/Linux
            
        return f"✅ Evento '{titulo}' agendado. El archivo de calendario se guardó en: {filepath} y se intentó abrir automáticamente."
        
    except ValueError:
        return "Error: El formato de fecha debe ser 'YYYY-MM-DD HH:MM'."
    except Exception as e:
        return f"Error crítico al crear evento: {e}"
