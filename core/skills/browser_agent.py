from playwright.async_api import async_playwright
from config import config

async def browser_navigate(url: str, extract_text: bool = True) -> dict:
    """
    Navega a una URL usando Playwright y extrae el texto limpio de la página
    u obtiene información básica para que Mónica la lea en memoria.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=config.playwright_headless)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            
            title = await page.title()
            text_content = ""
            
            if extract_text:
                # Extraer todo el texto visible (útil para que el LLM lo lea)
                text_content = await page.evaluate("document.body.innerText")
                # Limpiamos exceso de espacios para no gastar tantos tokens
                text_content = " ".join(text_content.split())
                if len(text_content) > 4000:
                    text_content = text_content[:4000] + "... [truncado]"
            
            await browser.close()
            
            return {
                "success": True,
                "title": title,
                "url": url,
                "content": text_content
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
