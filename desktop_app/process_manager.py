"""
Gestor de procesos del sistema operativo.
Este módulo implementa clases y funciones para gestionar procesos del sistema
operativo, incluyendo su monitoreo y obtención de métricas.

Características:
- Monitoreo de procesos del sistema en tiempo real
- Obtención de métricas (CPU, memoria, estado)
- Clasificación de procesos por criterios
- Manejo de errores de acceso y procesos zombis
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import psutil
from datetime import datetime

@dataclass(frozen=True)
class ProcesoMeta:
    """
    Clase inmutable que almacena metadatos de un proceso del sistema.
    
    Attributes:
        pid (int): Identificador del proceso
        nombre (str): Nombre del proceso
        usuario (str): Usuario que ejecuta el proceso
        cpu (float): Porcentaje de uso de CPU
        memoria (float): Porcentaje de uso de memoria
        estado (str): Estado actual del proceso
        tiempo_creacion (str): Fecha y hora de creación del proceso
    """
    pid: int
    nombre: str
    usuario: str
    cpu: float
    memoria: float
    estado: str
    tiempo_creacion: str

@dataclass
class Proceso:
    """
    Clase que representa un proceso en el sistema.
    
    Attributes:
        pid (int): Identificador del proceso
        nombre (str): Nombre del proceso
        usuario (str): Usuario que ejecuta el proceso
        descripcion (str): Descripción del proceso
        prioridad (int): Prioridad del proceso
        estado (str): Estado actual del proceso
        t_llegada (int): Tiempo de llegada
        t_final (int): Tiempo de finalización
        rafaga_total (int): Duración total de la ráfaga
        rafaga_restante (int): Duración restante de la ráfaga
        num_ejecuciones (int): Número de ejecuciones
        turnaround (int): Tiempo total de ejecución
        historial (List[Tuple[str, int]]): Historial de estados
    """
    pid: int
    nombre: str
    usuario: str
    descripcion: str
    prioridad: int
    estado: str = "Listo"
    t_llegada: int = 0
    t_final: int = 0
    rafaga_total: int = 0
    rafaga_restante: int = 0
    num_ejecuciones: int = 0
    turnaround: int = 0
    historial: List[Tuple[str, int]] = field(default_factory=list)
    
    def __post_init__(self):
        """
        Inicializa los valores calculados del proceso.
        
        - Calcula la ráfaga total basada en la longitud de la descripción
        - Inicializa la ráfaga restante
        """
        # Calcular ráfaga total basada en la descripción
        self.rafaga_total = len(self.descripcion)
        self.rafaga_restante = self.rafaga_total
        
    def to_dict(self) -> dict:
        """
        Convierte el proceso a un diccionario.
        
        Returns:
            dict: Diccionario con todos los atributos del proceso
        """
        return {
            'pid': self.pid,
            'nombre': self.nombre,
            'usuario': self.usuario,
            'descripcion': self.descripcion,
            'prioridad': self.prioridad,
            'estado': self.estado,
            't_llegada': self.t_llegada,
            't_final': self.t_final,
            'rafaga_total': self.rafaga_total,
            'rafaga_restante': self.rafaga_restante,
            'num_ejecuciones': self.num_ejecuciones,
            'turnaround': self.turnaround,
            'historial': self.historial
        }

def listar_procesos(n: int, criterio: str) -> List[ProcesoMeta]:
    """
    Lista los n procesos más activos según el criterio especificado.
    
    Args:
        n (int): Número de procesos a recuperar
        criterio (str): Criterio de ordenamiento ("cpu" o "memoria")
        
    Returns:
        List[ProcesoMeta]: Lista de objetos ProcesoMeta ordenados por el criterio
        
    Raises:
        ValueError: Si n es mayor que el total de procesos disponibles
        
    El proceso:
    1. Obtiene información de todos los procesos del sistema
    2. Filtra procesos inaccesibles o zombis
    3. Ordena por el criterio especificado
    4. Retorna los n primeros procesos
    """
    procesos = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
        try:
            info = proc.info
            create_time = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            
            procesos.append(ProcesoMeta(
                pid=info['pid'],
                nombre=info['name'],
                usuario=info['username'],
                cpu=info['cpu_percent'],
                memoria=info['memory_percent'],
                estado=info['status'],
                tiempo_creacion=create_time
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    # Ordenar por criterio
    key = 'cpu' if criterio.lower() == "cpu" else 'memoria'
    procesos.sort(key=lambda x: getattr(x, key), reverse=True)
    
    # Verificar n
    total_procesos = len(procesos)
    if n > total_procesos:
        raise ValueError(f"Se solicitaron {n} procesos pero solo hay {total_procesos} disponibles")
        
    return procesos[:n] 