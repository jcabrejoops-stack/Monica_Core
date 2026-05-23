# Manual: Sinergia de Extracción y Reportes PDF

Mónica, cuando el usuario te pida "extraer leads de una URL y armarlos en un PDF", debes combinar tus habilidades utilizando el Sandbox de Python.

## El Flujo de Trabajo (Sinergia)

El `cazador_leads` ahora devuelve un archivo JSON. Pero como lo vamos a conectar directo al PDF, debes importar la lógica de esta manera en el Sandbox:

```python
import sys
sys.path.append('skills')
import json
import asyncio
from cazador_leads import extraer_leads
from creador_pdfs import json_a_pdf
import os
import time

# NOTA: Extraemos el prompt asincrónico manualmente si no queremos tocar el archivo JSON
# O usamos extraer_leads para que haga el archivo JSON, luego lo leemos y hacemos el PDF.

async def pipeline():
    url_objetivo = "LA_URL_AQUI"
    tema_objetivo = "TEMA_AQUI"
    
    # 1. Ejecutar el cazador de leads
    res = await extraer_leads(url=url_objetivo, tema=tema_objetivo)
    print(res)
    
    # El cazador de leads guarda el archivo en ~/Descargas/Monica_Leads/leads_tema_timestamp.json
    # Como no sabemos el timestamp exacto, buscamos el archivo más reciente en esa carpeta:
    output_dir = os.path.join(os.path.expanduser("~"), "Descargas", "Monica_Leads")
    archivos = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.json')]
    
    if archivos:
        archivo_reciente = max(archivos, key=os.path.getctime)
        with open(archivo_reciente, "r", encoding="utf-8") as f:
            datos_leads = json.load(f)
            
        # 2. Convertir esos datos JSON en PDF
        resultado_pdf = json_a_pdf(datos_leads, titulo=f"Directorio de {tema_objetivo}", nombre_archivo=f"Leads_{tema_objetivo}")
        print(resultado_pdf)

# Ejecutar pipeline
asyncio.run(pipeline())
```

Con este script, primero cazas la información, la guardas en JSON, luego lees ese JSON y generas la tabla en PDF automáticamente. ¡Eres un genio de la automatización!
