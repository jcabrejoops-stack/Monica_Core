"""
Módulo de Web Scraping para Mónica.
Provee funciones para extraer información útil de internet.
"""
import re
import urllib.request
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def extract_emails(url: str) -> dict:
    """
    Navega a una URL y extrae todos los correos electrónicos visibles en el HTML.
    Devuelve un diccionario con los resultados.
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read()
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        
        # Expresión regular básica para correos
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
        return {"status": "success", "url": url, "emails": list(emails)}
    except Exception as e:
        logger.error(f"Error extrayendo correos en {url}: {e}")
        return {"status": "error", "message": str(e)}

def extract_social_links(url: str) -> dict:
    """
    Busca enlaces a redes sociales comunes (LinkedIn, Twitter, Facebook, Instagram) en la página.
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read()
        soup = BeautifulSoup(html, "html.parser")
        
        social_links = []
        networks = ['linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com', 'x.com']
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(net in href.lower() for net in networks):
                if href not in social_links:
                    social_links.append(href)
                    
        return {"status": "success", "url": url, "social_links": social_links}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def scrape_text(url: str) -> dict:
    """
    Extrae todo el texto legible de un sitio web. Útil para resumir páginas.
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read()
        soup = BeautifulSoup(html, "html.parser")
        
        # Eliminar scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        return {"status": "success", "url": url, "content_length": len(text), "text": text[:2000] + "..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
