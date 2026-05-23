# skills/cazador_leads.py
import json
import os
import time
from playwright.async_api import async_playwright
from core.llm import call_llm

async def extraer_leads(url: str, tema: str = "cafeterías"):
    """
    Raspa una página web y usa Inteligencia Artificial para extraer únicamente
    los contactos (Leads) relacionados con el tema dado, guardándolos en un CSV/JSON.
    """
    print(f"[Cazador de Leads] Navegando a {url} para buscar leads de '{tema}'...")
    
    try:
        async with async_playwright() as p:
            # Lanzar Chromium en modo sin cabeza (invisible)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Extraer todo el texto visible
            texto_bruto = await page.evaluate("document.body.innerText")
            await browser.close()
            
            # Limpiar texto para no sobrecargar el LLM
            texto_bruto = " ".join(texto_bruto.split())
            if len(texto_bruto) > 8000:
                texto_bruto = texto_bruto[:8000] # Truncar a ~8k caracteres para el modelo
                
            print(f"[Cazador de Leads] Texto extraído. Usando LLM Híbrido para estructurar datos...")
            
            # Prompt de extracción estructurada
            prompt_extraccion = (
                f"Eres un experto extractor de datos. Analiza el siguiente texto extraído de una web y busca "
                f"información de contacto (Leads) relacionada con '{tema}'.\n"
                f"Extrae: Nombres de negocios, Correos electrónicos, Teléfonos y Direcciones.\n"
                f"Devuelve ÚNICAMENTE un array en formato JSON puro (sin formato markdown ```json) con esta estructura:\n"
                f"[{{\"nombre\": \"...\", \"email\": \"...\", \"telefono\": \"...\", \"direccion\": \"...\"}}]\n\n"
                f"TEXTO A ANALIZAR:\n{texto_bruto}"
            )
            
            # Llamar al cerebro de Mónica (usamos el motor 'hybrid' para intentar extraer rápido en la nube)
            respuesta_llm = await call_llm(prompt_extraccion, engine="hybrid")
            
            # Intentar limpiar la respuesta del LLM por si puso comillas raras o markdown
            respuesta_llm = respuesta_llm.replace("```json", "").replace("```", "").strip()
            
            # Parsear JSON
            leads_encontrados = json.loads(respuesta_llm)
            
            if not leads_encontrados:
                return f"No se encontraron leads válidos en la URL: {url}"
                
            # Guardar en disco duro de Mónica
            output_dir = os.path.join(os.path.expanduser("~"), "Descargas", "Monica_Leads")
            os.makedirs(output_dir, exist_ok=True)
            
            filepath = os.path.join(output_dir, f"leads_{tema.replace(' ', '_')}_{int(time.time())}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(leads_encontrados, f, ensure_ascii=False, indent=4)
                
            return f"¡Éxito! Se extrajeron {len(leads_encontrados)} leads de {url}. Guardados en: {filepath}"
            
    except Exception as e:
        return f"Error en el Cazador de Leads: {e}"
