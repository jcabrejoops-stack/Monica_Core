import sqlite3
import os
from pathlib import Path

# Definir la ruta de la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "marketing_crm.db"

def get_connection():
    """Devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabla de Leads (Contactos extraídos y gestionados)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT,
        telefono TEXT,
        direccion TEXT,
        estado TEXT DEFAULT 'Nuevos', -- Nuevos, Prospectado, Nutricion, Cliente
        categoria TEXT, -- Ej. Restaurantes, Cafeterias
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ultima_interaccion TIMESTAMP,
        notas TEXT
    )
    ''')
    
    # 2. Tabla de Productos (Arsenal Digital)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion_breve TEXT,
        textos_variantes TEXT, -- JSON con variantes de texto para evitar spam
        url_producto TEXT,
        imagenes TEXT, -- JSON con rutas de imágenes
        videos TEXT, -- JSON con rutas de videos
        precio REAL,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. Tabla de Listas de Nutrición (Campañas)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS listas_nutricion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria TEXT,
        textos_variantes TEXT, -- JSON con los mensajes a intercalar
        multimedia TEXT, -- JSON con el arsenal de imágenes/videos a usar
        frecuencia_dias INTEGER DEFAULT 1,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 4. Tabla de Historial de Compras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        producto_id INTEGER,
        fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        monto REAL,
        FOREIGN KEY(lead_id) REFERENCES leads(id),
        FOREIGN KEY(producto_id) REFERENCES productos(id)
    )
    ''')

    conn.commit()
    conn.close()

# Inicializar automáticamente al importar
init_db()
