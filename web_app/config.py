"""
Configuración de la aplicación web.
Este módulo contiene todas las variables de configuración necesarias
para el funcionamiento de la aplicación web de simulación de procesos.

Las variables pueden ser configuradas mediante variables de entorno
o usarán los valores por defecto especificados.
"""

import os

# Configuración de la API de escritorio
DESKTOP_API_URL = os.getenv("DESKTOP_API_URL", "http://localhost:5000/procesos")
"""
URL base de la API de la aplicación de escritorio.
Por defecto: http://localhost:5000/procesos
"""

DESKTOP_API_TIMEOUT = float(os.getenv("DESKTOP_API_TIMEOUT", "2.0"))
"""
Tiempo máximo de espera (en segundos) para las peticiones a la API de escritorio.
Por defecto: 2.0 segundos
"""

# Configuración de la base de datos
DB_PATH = os.getenv("DB_PATH", "simulaciones.db")
"""
Ruta al archivo de base de datos SQLite.
Por defecto: simulaciones.db en el directorio actual
"""

# Configuración de la aplicación Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
"""
Host donde se ejecutará el servidor Flask.
Por defecto: 0.0.0.0 (todas las interfaces)
"""

FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
"""
Puerto donde se ejecutará el servidor Flask.
Por defecto: 5001
"""

FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
"""
Modo debug de Flask.
Por defecto: True
""" 