# skills/creador_pdfs.py
import os
import time
from fpdf import FPDF

def json_a_pdf(datos: list, titulo: str = "Reporte de Datos", nombre_archivo: str = "Reporte") -> str:
    """
    Convierte una lista de diccionarios (Ej: Leads extraídos) en un documento PDF
    profesional con una tabla formateada.
    """
    if not datos or not isinstance(datos, list) or len(datos) == 0:
        return "Error: No hay datos válidos para generar el PDF."
        
    try:
        pdf = FPDF(orientation="L", unit="mm", format="A4") # Paisaje para tablas
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        
        # Título
        pdf.cell(0, 10, titulo, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        # Extraer cabeceras (claves del primer diccionario)
        cabeceras = list(datos[0].keys())
        
        # Calcular ancho de columnas dinámicamente
        ancho_pagina = pdf.epw
        ancho_columna = ancho_pagina / len(cabeceras)
        
        # Estilo de cabecera
        pdf.set_font("helvetica", "B", 10)
        pdf.set_fill_color(200, 220, 255)
        
        # Imprimir fila de cabeceras
        for cabecera in cabeceras:
            pdf.cell(ancho_columna, 10, cabecera.upper(), border=1, fill=True, align="C")
        pdf.ln()
        
        # Estilo de datos
        pdf.set_font("helvetica", "", 9)
        
        # Imprimir filas
        for fila in datos:
            for cabecera in cabeceras:
                # Limpiar texto para evitar errores de encoding
                valor_texto = str(fila.get(cabecera, ""))
                valor_limpio = valor_texto.encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(ancho_columna, 8, valor_limpio[:40], border=1) # Truncado a 40 chars por celda
            pdf.ln()
            
        # Guardar archivo en la carpeta pública de Mónica (media/uploads) para que aparezca en la Galería
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "media", "uploads")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, f"{nombre_archivo}_{int(time.time())}.pdf")
        pdf.output(filepath)
        
        # Devolver una url relativa que Mónica pueda mostrar en su chat
        filename = os.path.basename(filepath)
        return f"✅ PDF generado exitosamente.\n\n[Puedes descargar/ver el PDF aquí](/media/uploads/{filename})"
    except Exception as e:
        return f"Error crítico al generar el PDF: {e}"

# Ejemplo de uso en Sandbox:
# from creador_pdfs import json_a_pdf
# leads = [{"nombre": "Juan", "email": "juan@test.com"}]
# print(json_a_pdf(leads, "Leads Extraídos", "Leads_Cafeterias"))
