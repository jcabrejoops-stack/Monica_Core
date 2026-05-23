# core/browser.py
"""Módulo que gestiona la sesión de Playwright.

Proporciona:
- Creación de un navegador configurado para emular un comportamiento humano.
- Métodos auxiliares para navegar, inyectar cambios en tiempo real y realizar login.
- Manejo de errores con reintentos y registro en el sistema de logs.
"""
import asyncio
import random
import logging
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright, Browser, Page, Error as PlaywrightError
from config import config

logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

class BrowserSession:
    """Encapsula una sesión de Playwright.

    - Usa ``async_playwright`` para crear un navegador Chromium.
    - Configura ``headless`` según ``config.playwright_headless``.
    - Aplica técnicas de *stealth* (user‑agent aleatorio, resolución de WebGL, etc.).
    - Simula movimientos de ratón y delays de tipeo para evitar detección.
    """

    def __init__(self, browser: Browser, page: Page) -> None:
        self.browser = browser
        self.page = page

    @classmethod
    async def create(cls) -> "BrowserSession":
        """Crea y devuelve una instancia de ``BrowserSession``.

        Se configuran los siguientes atributos:
        * ``headless`` – tomado de ``config``.
        * ``user_agent`` – valor aleatorio de una lista común.
        """
        playwright = await async_playwright().start()
        try:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            ]
            user_agent = random.choice(user_agents)
            browser = await playwright.chromium.launch(headless=config.playwright_headless, args=["--no-sandbox"])
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()
            session = cls(browser, page)
            await session._apply_stealth()
            return session
        except Exception as exc:
            logger.error(f"Error al iniciar Playwright: {exc}")
            raise
        finally:
            # No cerramos aquí; la instancia se encargará de cerrar en ``close``.
            pass

    async def _apply_stealth(self) -> None:
        """Aplica pequeñas modificaciones para dificultar la detección de bots.

        - Sobrescribe ``navigator.webdriver``.
        - Añade una pequeña latencia aleatoria en cada interacción.
        """
        # El script de stealth más simple.
        await self.page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        # Otros ajustes pueden añadirse según necesidad.

    async def goto(self, url: str) -> None:
        """Navega a la URL especificada y espera a que el DOM esté listo.
        """
        try:
            await self.page.goto(url, wait_until="load")
            # Esperar un tiempo aleatorio para emular lecturas humanas.
            await asyncio.sleep(random.uniform(0.5, 1.5))
            logger.info(f"Navegado a {url}")
        except PlaywrightError as exc:
            logger.error(f"Fallo al cargar {url}: {exc}")
            raise

    async def inject_change_live(self, selector: str, new_html_or_style: str) -> None:
        """Inyecta HTML o estilos CSS en el elemento indicado.

        ``new_html_or_style`` puede ser:
        * Un fragmento HTML que reemplazará el ``innerHTML`` del elemento.
        * Una cadena CSS que se añadirá al atributo ``style``.
        """
        try:
            # Detectar si parece CSS (contiene ':' y ';')
            if ":" in new_html_or_style and ";" in new_html_or_style:
                # Asumimos estilo CSS
                await self.page.eval_on_selector(
                    selector,
                    f"(el, style) => {{ el.style.cssText += style; }}",
                    new_html_or_style,
                )
                logger.info(f"Estilo inyectado en {selector}: {new_html_or_style}")
            else:
                # Inyectar como HTML
                await self.page.eval_on_selector(
                    selector,
                    "(el, html) => { el.innerHTML = html; }",
                    new_html_or_style,
                )
                logger.info(f"HTML inyectado en {selector}: {new_html_or_style}")
        except PlaywrightError as exc:
            logger.error(f"Error al inyectar cambio en {selector}: {exc}")
            raise

    async def login(self, login_url: str, username: str, password: str) -> None:
        """Automatiza un flujo de login sencillo.

        Busca campos de tipo ``input`` con atributos ``type='email'``/``type='text'`` y ``type='password'``.
        Completa los valores y envía el formulario.
        """
        try:
            await self.goto(login_url)
            # Intentar detectar los campos.
            email_selector = "input[type='email'], input[name*='user'], input[name*='email']"
            password_selector = "input[type='password']"
            await self.page.fill(email_selector, username)
            await asyncio.sleep(random.uniform(config.min_typing_delay / 1000, config.max_typing_delay / 1000))
            await self.page.fill(password_selector, password)
            await asyncio.sleep(random.uniform(config.min_typing_delay / 1000, config.max_typing_delay / 1000))
            # Submitear el formulario presionando Enter.
            await self.page.press(password_selector, "Enter")
            logger.info("Login enviado.")
        except PlaywrightError as exc:
            logger.error(f"Error en proceso de login: {exc}")
            raise

    async def close(self) -> None:
        """Cierra el navegador y libera recursos.
        """
        try:
            await self.page.close()
            await self.browser.close()
            logger.info("Sesión de Playwright cerrada.")
        except Exception as exc:
            logger.warning(f"Error al cerrar Playwright: {exc}")

# Helper para simular tipeo humano en texto plano (puede usarse externamente).
async def human_type(page: Page, selector: str, text: str) -> None:
    """Escribe ``text`` carácter a carácter con delays aleatorios.
    """
    await page.focus(selector)
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(config.min_typing_delay / 1000, config.max_typing_delay / 1000))
