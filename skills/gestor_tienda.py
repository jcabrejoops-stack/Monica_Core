# skills/gestor_tienda.py
import os
import time
from core.llm import call_llm

async def crear_landing_page(nombre_producto: str, textos_beneficios: list, imagenes: list, url_tienda_base: str):
    """
    Usa las habilidades de UI/UX de Mónica para generar una Landing Page profesional
    que venda un producto digital, e incluye los botones de conversión solicitados.
    """
    print(f"[Gestor Tienda] Analizando datos de producto: {nombre_producto}...")
    
    prompt = (
        f"Eres un Desarrollador Web Senior y experto en UI/UX Marketing. "
        f"Crea el código HTML, CSS y JS de una Landing Page de altísima conversión para el producto: '{nombre_producto}'.\n"
        f"Beneficios a resaltar: {', '.join(textos_beneficios[:3])}\n"
        f"Utiliza un diseño espectacular, moderno, modo oscuro premium.\n"
        f"En la parte inferior de la página DEBEN ir dos botones fijos grandes: \n"
        f"1. 'Conseguir' (estilo CTA vibrante)\n"
        f"2. 'Especialista' (estilo secundario o fantasma para hablar con un asesor)\n"
        f"Usa Vanilla HTML/CSS. Devuelve ÚNICAMENTE el código en bruto, sin markdown."
    )
    
    try:
        codigo_landing = await call_llm(prompt, engine="hybrid")
        codigo_landing = codigo_landing.replace("```html", "").replace("```", "").strip()
        
        # Guardar la Landing Page localmente
        base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Monica_Tienda_Remota", nombre_producto.replace(" ", "_"))
        os.makedirs(base_dir, exist_ok=True)
        
        archivo_index = os.path.join(base_dir, "index.html")
        with open(archivo_index, "w", encoding="utf-8") as f:
            f.write(codigo_landing)
            
        print(f"[Gestor Tienda] Landing Page creada y lista para despliegue: {archivo_index}")
        
        # 2. Generar el "Snippet" (Fragmento) para la Tienda Principal
        snippet_html = f"""
        <!-- Fragmento a inyectar en la tienda principal ({url_tienda_base}) -->
        <div class="producto-card" style="border:1px solid #333; border-radius:12px; padding:15px; text-align:center;">
            <img src="ruta_imagen.jpg" alt="{nombre_producto}" style="max-width:100%; border-radius:8px;">
            <h3 style="color:#fff; margin-top:10px;">{nombre_producto}</h3>
            <p style="color:#aaa; font-size:0.9rem;">{textos_beneficios[0] if textos_beneficios else 'Producto Premium'}</p>
            <a href="/{nombre_producto.replace(' ', '_').lower()}/index.html" style="display:inline-block; margin-top:10px; background:#00f0ff; color:#000; padding:8px 16px; border-radius:6px; text-decoration:none; font-weight:bold;">Ver Detalles</a>
        </div>
        """
        
        archivo_snippet = os.path.join(base_dir, "snippet_tienda.html")
        with open(archivo_snippet, "w", encoding="utf-8") as f:
            f.write(snippet_html)
            
        return f"¡Landing Page '{nombre_producto}' creada con éxito!\nEl código y el fragmento para tu tienda se guardaron en tu Escritorio: Monica_Tienda_Remota."
        
    except Exception as e:
        return f"Error en el Gestor de Tienda: {e}"
