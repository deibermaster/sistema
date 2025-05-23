"""
Servidor REST para la aplicación de escritorio.
Este módulo implementa un servidor REST usando FastAPI que expone endpoints
para obtener información sobre los procesos en ejecución y el catálogo actual.

Características:
- Endpoint para obtener lista de procesos en formato XML
- Manejo automático de puertos disponibles
- Actualización en tiempo real del estado de procesos
- Integración con el catálogo de procesos
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import uvicorn
import threading
import socket
import time
import psutil
from .catalog import Catalogo

app = FastAPI()

# Variables globales para almacenar el estado
procesos_actuales: Dict[str, Any] = {}
catalogo_actual: Dict = {
    'id': 1,
    'nombre': 'Catálogo Principal'
}

def encontrar_puerto_disponible(puerto_inicial: int = 8000, max_intentos: int = 20) -> int:
    """
    Busca un puerto disponible en el sistema.
    
    Args:
        puerto_inicial (int): Puerto desde donde comenzar la búsqueda
        max_intentos (int): Número máximo de puertos a intentar
        
    Returns:
        int: Número de puerto disponible
        
    Raises:
        RuntimeError: Si no se encuentra un puerto disponible
    """
    # Primero, intentar liberar el puerto si está en uso
    for puerto in range(puerto_inicial, puerto_inicial + max_intentos):
        try:
            # Verificar si hay algún proceso usando el puerto
            for conn in psutil.net_connections():
                if conn.laddr.port == puerto:
                    try:
                        # Intentar terminar el proceso que usa el puerto
                        psutil.Process(conn.pid).terminate()
                        time.sleep(0.5)  # Esperar a que se libere el puerto
                    except:
                        pass
                        
            # Intentar usar el puerto
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', puerto))
                return puerto
        except OSError:
            continue
            
    # Si no se encuentra un puerto, intentar con localhost
    for puerto in range(puerto_inicial, puerto_inicial + max_intentos):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', puerto))
                return puerto
        except OSError:
            continue
            
    raise RuntimeError(f"No se pudo encontrar un puerto disponible después de {max_intentos} intentos")

def actualizar_procesos(procesos: Dict[str, Any], catalogo_id: int, catalogo_nombre: str):
    """
    Actualiza la lista de procesos en el servidor.
    
    Args:
        procesos (Dict[str, Any]): Diccionario con la información de los procesos
        catalogo_id (int): ID del catálogo actual
        catalogo_nombre (str): Nombre del catálogo actual
    """
    procesos_actuales['procesos'] = procesos
    procesos_actuales['catalogo_id'] = catalogo_id
    procesos_actuales['catalogo_nombre'] = catalogo_nombre

@app.get("/procesos")
def obtener_procesos():
    """
    Endpoint para obtener la lista de procesos en formato XML.
    
    Returns:
        Response: Respuesta HTTP con el XML de procesos
        
    El XML generado tiene la siguiente estructura:
    <procesos>
        <proceso>
            <pid>...</pid>
            <nombre>...</nombre>
            <usuario>...</usuario>
            <descripcion>...</descripcion>
            <prioridad>...</prioridad>
            <estado>...</estado>
            <t_llegada>...</t_llegada>
            <t_final>...</t_final>
            <rafaga_total>...</rafaga_total>
            <rafaga_restante>...</rafaga_restante>
            <num_ejecuciones>...</num_ejecuciones>
            <turnaround>...</turnaround>
            <historial>
                <evento>
                    <estado>...</estado>
                    <duracion>...</duracion>
                </evento>
            </historial>
        </proceso>
    </procesos>
    """
    root = ET.Element("procesos")
    
    for proc in procesos_actuales.get('procesos', []):
        proceso = ET.SubElement(root, "proceso")
        ET.SubElement(proceso, "pid").text = str(proc['pid'])
        ET.SubElement(proceso, "nombre").text = proc['nombre']
        ET.SubElement(proceso, "usuario").text = proc['usuario']
        ET.SubElement(proceso, "descripcion").text = proc['descripcion']
        ET.SubElement(proceso, "prioridad").text = str(proc['prioridad'])
        ET.SubElement(proceso, "estado").text = proc['estado']
        ET.SubElement(proceso, "t_llegada").text = str(proc['t_llegada'])
        ET.SubElement(proceso, "t_final").text = str(proc['t_final'])
        ET.SubElement(proceso, "rafaga_total").text = str(proc['rafaga_total'])
        ET.SubElement(proceso, "rafaga_restante").text = str(proc['rafaga_restante'])
        ET.SubElement(proceso, "num_ejecuciones").text = str(proc['num_ejecuciones'])
        ET.SubElement(proceso, "turnaround").text = str(proc['turnaround'])
        
        historial = ET.SubElement(proceso, "historial")
        for estado, duracion in proc['historial']:
            evento = ET.SubElement(historial, "evento")
            ET.SubElement(evento, "estado").text = estado
            ET.SubElement(evento, "duracion").text = str(duracion)
    
    xml_str = ET.tostring(root, encoding='unicode')
    return Response(content=xml_str, media_type="application/xml")

def iniciar_servidor():
    """
    Inicia el servidor REST en el puerto 5000.
    
    Raises:
        Exception: Si hay un error al iniciar el servidor
    """
    try:
        puerto = 5000  # PUERTO FIJO
        print(f"Iniciando servidor REST en el puerto {puerto}")
        uvicorn.run(app, host="127.0.0.1", port=puerto)
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        raise

if __name__ == "__main__":
    iniciar_servidor() 