import requests
import xml.etree.ElementTree as ET
import socket
from typing import List, Optional
from models.proceso import Proceso, EstadoProceso

class RestClient:
    def __init__(self):
        self.base_url = self._encontrar_servidor()
        
    def _encontrar_servidor(self, puerto_inicial: int = 5000, max_intentos: int = 10) -> str:
        """Busca el servidor REST intentando diferentes puertos"""
        for puerto in range(puerto_inicial, puerto_inicial + max_intentos):
            try:
                url = f'http://localhost:{puerto}/procesos'
                response = requests.get(url)
                if response.status_code == 200:
                    return f'http://localhost:{puerto}'
            except requests.exceptions.ConnectionError:
                continue
        raise ConnectionError("No se pudo conectar al servidor REST")
        
    def xml_to_proceso(self, xml_elem: ET.Element) -> Proceso:
        """Convierte un elemento XML a un objeto Proceso."""
        return Proceso(
            id=int(xml_elem.find("id").text),
            nombre=xml_elem.find("nombre").text,
            tiempo_llegada=int(xml_elem.find("tiempo_llegada").text),
            tiempo_servicio=int(xml_elem.find("tiempo_servicio").text),
            prioridad=int(xml_elem.find("prioridad").text),
            estado=EstadoProceso(xml_elem.find("estado").text),
            tiempo_restante=int(xml_elem.find("tiempo_restante").text),
            tiempo_inicio=int(xml_elem.find("tiempo_inicio").text) if xml_elem.find("tiempo_inicio") is not None else None,
            tiempo_fin=int(xml_elem.find("tiempo_fin").text) if xml_elem.find("tiempo_fin") is not None else None,
            tiempo_espera=int(xml_elem.find("tiempo_espera").text),
            tiempo_respuesta=int(xml_elem.find("tiempo_respuesta").text),
            tiempo_retorno=int(xml_elem.find("tiempo_retorno").text)
        )
        
    def obtener_procesos(self) -> List[dict]:
        """Obtiene la lista de procesos del servidor REST"""
        try:
            response = requests.get(f'{self.base_url}/procesos')
            response.raise_for_status()
            
            # Parsear XML
            root = ET.fromstring(response.content)
            procesos = []
            
            for proc_elem in root.findall('proceso'):
                proceso = {
                    'pid': int(proc_elem.find('pid').text),
                    'nombre': proc_elem.find('nombre').text,
                    'usuario': proc_elem.find('usuario').text,
                    'descripcion': proc_elem.find('descripcion').text,
                    'prioridad': int(proc_elem.find('prioridad').text),
                    'estado': 'Listo'  # Estado inicial
                }
                
                # Campos opcionales
                if proc_elem.find('cpu') is not None:
                    proceso['cpu'] = float(proc_elem.find('cpu').text)
                if proc_elem.find('memoria') is not None:
                    proceso['memoria'] = float(proc_elem.find('memoria').text)
                    
                procesos.append(proceso)
                
            return procesos
            
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener procesos: {e}")
            return []
            
    def agregar_proceso(self, proceso: Proceso) -> bool:
        """Agrega un nuevo proceso al servidor."""
        try:
            response = requests.post(f"{self.base_url}/procesos", json=proceso.__dict__)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error al agregar proceso: {e}")
            return False
            
    def actualizar_proceso(self, proceso: Proceso) -> bool:
        """Actualiza un proceso existente en el servidor."""
        try:
            response = requests.put(f"{self.base_url}/procesos/{proceso.id}", json=proceso.__dict__)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error al actualizar proceso: {e}")
            return False
            
    def eliminar_proceso(self, proceso_id: int) -> bool:
        """Elimina un proceso del servidor."""
        try:
            response = requests.delete(f"{self.base_url}/procesos/{proceso_id}")
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error al eliminar proceso: {e}")
            return False 