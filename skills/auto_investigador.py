# skills/auto_investigador.py
import json
from duckduckgo_search import DDGS
from core.llm import call_llm
from core.skills.browser_agent import browser_navigate
import asyncio

async def investigacion_profunda(tema: str) -> str:
    """
    Realiza una búsqueda profunda en internet sobre un tema, lee varias páginas 
    y sintetiza un reporte estructurado y completo utilizando el LLM.
    """
    print(f"[Auto-Investigador] Iniciando investigación sobre: '{tema}'")
    
    try:
        # 1. Buscar en internet
        with DDGS() as ddgs:
            resultados = list(ddgs.text(tema, max_results=3))
            
        if not resultados:
            return f"No se encontró información en internet sobre: {tema}"
            
        textos_recolectados = []
        
        # 2. Navegar y extraer texto de las fuentes
        print(f"[Auto-Investigador] Se encontraron {len(resultados)} fuentes. Extrayendo contenido...")
        for res in resultados:
            url = res.get('href')
            if url:
                print(f"Leyendo: {url}")
                datos_pagina = await browser_navigate(url, extract_text=True)
                if datos_pagina.get('success'):
                    texto_pagina = datos_pagina.get('content', '')[:3000] # Limitar tokens
                    textos_recolectados.append(f"FUENTE: {url}\nCONTENIDO:\n{texto_pagina}\n---")
                    
        if not textos_recolectados:
            return "Las fuentes bloquean el acceso o no tienen texto legible."
            
        # 3. Sintetizar con el LLM
        print("[Auto-Investigador] Sintetizando la investigación...")
        contexto_total = "\n".join(textos_recolectados)
        prompt = (
            f"Eres un Auto-Investigador Profundo. Has recolectado la siguiente información de internet "
            f"sobre el tema '{tema}'.\n"
            f"Redacta un reporte final muy profesional, estructurado con títulos y viñetas, "
            f"explicando los puntos clave y sacando una conclusión sólida.\n\n"
            f"DATOS RECOLECTADOS:\n{contexto_total}"
        )
        
        reporte_final = await call_llm(prompt, engine="hybrid")
        
        # Guardar el reporte
        import os
        import time
        output_dir = os.path.join(os.path.expanduser("~"), "Documentos", "Monica_Investigaciones")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, f"Investigacion_{int(time.time())}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(reporte_final)
            
        return f"✅ Investigación completada con éxito. El reporte detallado se guardó en:\n{filepath}\n\nRESUMEN RÁPIDO:\n{reporte_final[:500]}..."
        
    except Exception as e:
        return f"Error crítico en la investigación: {e}"
