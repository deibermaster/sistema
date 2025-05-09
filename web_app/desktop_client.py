import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from flask import current_app
from config import DESKTOP_API_URL, DESKTOP_API_TIMEOUT

class DesktopClientError(Exception):
    """Excepción base para errores del cliente de escritorio"""
    pass

class DesktopConnectionError(DesktopClientError):
    """Error de conexión con la aplicación de escritorio"""
    pass

class DesktopTimeoutError(DesktopClientError):
    """Timeout al conectar con la aplicación de escritorio"""
    pass

class DesktopResponseError(DesktopClientError):
    """Error en la respuesta de la aplicación de escritorio"""
    pass

def fetch_procesos_desktop() -> List[Dict]:
    """
    Obtiene los procesos desde la aplicación de escritorio.
    
    Returns:
        List[Dict]: Lista de procesos con sus atributos
        
    Raises:
        DesktopConnectionError: Si no se puede conectar con la app de escritorio
        DesktopTimeoutError: Si la conexión excede el timeout
        DesktopResponseError: Si la respuesta no es válida
    """
    try:
        response = requests.get(
            DESKTOP_API_URL,
            timeout=DESKTOP_API_TIMEOUT
        )
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        procesos = []
        
        for proc_elem in root.findall('proceso'):
            try:
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
                current_app.logger.error(f"Error al procesar proceso: {e}")
                continue
                
        if not procesos:
            raise DesktopResponseError("No se encontraron procesos válidos")
            
        return procesos
        
    except requests.exceptions.Timeout:
        current_app.logger.error("Timeout al consultar App Desktop")
        raise DesktopTimeoutError("El servicio de procesos está tardando demasiado")
        
    except requests.exceptions.ConnectionError:
        current_app.logger.error("No se pudo conectar con la App Desktop")
        raise DesktopConnectionError("Servicio de procesos no disponible")
        
    except requests.exceptions.HTTPError as e:
        current_app.logger.error(f"App Desktop devolvió error {e.response.status_code}")
        raise DesktopResponseError(f"Error en respuesta de procesos: {e}")
        
    except ET.ParseError as e:
        current_app.logger.error(f"Error al parsear XML: {e}")
        raise DesktopResponseError("Respuesta XML inválida") 