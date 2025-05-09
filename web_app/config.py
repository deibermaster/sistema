import os

# Configuración de la API de escritorio
DESKTOP_API_URL = os.getenv("DESKTOP_API_URL", "http://localhost:5000/procesos")
DESKTOP_API_TIMEOUT = float(os.getenv("DESKTOP_API_TIMEOUT", "2.0"))

# Configuración de la base de datos
DB_PATH = os.getenv("DB_PATH", "simulaciones.db")

# Configuración de la aplicación Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true" 