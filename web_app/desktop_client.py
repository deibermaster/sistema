"""
Cliente para comunicación con la aplicación de escritorio.
Este módulo proporciona la funcionalidad para obtener la lista de procesos
desde la aplicación de escritorio mediante una API REST que devuelve XML.

Características:
- Comunicación HTTP con la aplicación de escritorio
- Parsing de respuestas XML
- Manejo de errores de conexión y timeout
- Conversión de datos XML a formato de procesos
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from flask import current_app
from config import DESKTOP_API_URL, DESKTOP_API_TIMEOUT

class DesktopClientError(Exception):
    """
    Excepción base para errores del cliente de escritorio.
    Todas las excepciones específicas heredan de esta clase.
    """
    pass

class DesktopConnectionError(DesktopClientError):
    """
    Error que se lanza cuando no se puede establecer conexión
    con la aplicación de escritorio.
    """
    pass

class DesktopTimeoutError(DesktopClientError):
    """
    Error que se lanza cuando la conexión con la aplicación
    de escritorio excede el tiempo máximo de espera.
    """
    pass

class DesktopResponseError(DesktopClientError):
    """
    Error que se lanza cuando la respuesta de la aplicación
    de escritorio no es válida o no contiene datos esperados.
    """
    pass

def fetch_procesos_desktop() -> List[Dict]:
    """
    Obtiene los procesos desde la aplicación de escritorio.
    
    Esta función realiza una petición HTTP GET a la API de la aplicación
    de escritorio, parsea la respuesta XML y convierte cada proceso
    al formato requerido por el simulador.
    
    La respuesta XML debe tener el siguiente formato:
    <procesos>
        <proceso>
            <pid>123</pid>
            <nombre>proceso1</nombre>
            <usuario>user1</usuario>
            <descripcion>descripcion del proceso</descripcion>
            <prioridad>0</prioridad>
        </proceso>
        ...
    </procesos>
    
    Returns:
        List[Dict]: Lista de diccionarios con la información de cada proceso.
            Cada diccionario contiene:
            - pid (int): ID del proceso
            - nombre (str): Nombre del proceso
            - usuario (str): Usuario propietario
            - descripcion (str): Descripción del proceso
            - prioridad (int): Prioridad del proceso (0 o 1)
            - t_llegada (int): Tiempo de llegada (inicializado en 0)
            - rafaga_total (int): Duración total del proceso
            - rafaga_restante (int): Tiempo restante de ejecución
            - t_final (int): Tiempo de finalización (None inicialmente)
            - turnaround (int): Tiempo total de ejecución (None inicialmente)
            - estado (str): Estado actual del proceso
            - historial (list): Lista de eventos del proceso
        
    Raises:
        DesktopConnectionError: Si no se puede establecer conexión con la app
        DesktopTimeoutError: Si la conexión excede el tiempo máximo de espera
        DesktopResponseError: Si la respuesta no es válida o no contiene procesos
    """
    try:
        # Realizar petición HTTP GET a la API
        response = requests.get(
            DESKTOP_API_URL,
            timeout=DESKTOP_API_TIMEOUT
        )
        response.raise_for_status()
        
        # Parsear respuesta XML
        root = ET.fromstring(response.content)
        procesos = []
        
        # Procesar cada elemento proceso en el XML
        for proc_elem in root.findall('proceso'):
            try:
                # Convertir datos XML a diccionario de proceso
                proceso = {
                    'pid': int(proc_elem.find('pid').text),
                    'nombre': proc_elem.find('nombre').text,
                    'usuario': proc_elem.find('usuario').text,
                    'descripcion': proc_elem.find('descripcion').text,
                    'prioridad': int(proc_elem.find('prioridad').text),
                    't_llegada': 0,
                    'rafaga_total': len(proc_elem.find('descripcion').text),
                    'rafaga_restante': len(proc_elem.find('descripcion').text),
                    't_final': None,
                    'turnaround': None,
                    'estado': 'Listo',
                    'historial': []
                }
                procesos.append(proceso)
            except (AttributeError, ValueError) as e:
                # Registrar error y continuar con siguiente proceso
                current_app.logger.error(f"Error al procesar proceso: {e}")
                continue
                
        # Verificar que se encontraron procesos válidos
        if not procesos:
            raise DesktopResponseError("No se encontraron procesos válidos")
            
        return procesos
        
    except requests.exceptions.Timeout:
        # Error por timeout en la conexión
        current_app.logger.error("Timeout al consultar App Desktop")
        raise DesktopTimeoutError("El servicio de procesos está tardando demasiado")
        
    except requests.exceptions.ConnectionError:
        # Error por imposibilidad de conexión
        current_app.logger.error("No se pudo conectar con la App Desktop")
        raise DesktopConnectionError("Servicio de procesos no disponible")
        
    except requests.exceptions.HTTPError as e:
        # Error en la respuesta HTTP
        current_app.logger.error(f"App Desktop devolvió error {e.response.status_code}")
        raise DesktopResponseError(f"Error en respuesta de procesos: {e}")
        
    except ET.ParseError as e:
        # Error al parsear el XML
        current_app.logger.error(f"Error al parsear XML: {e}")
        raise DesktopResponseError("Respuesta XML inválida") 