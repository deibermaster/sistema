"""
Modelo de datos para representar procesos del sistema operativo.
Este módulo define las clases y enumeraciones necesarias para
representar y manipular procesos en el sistema de simulación.

Características:
- Estados de proceso (Listo, Ejecución, Terminado)
- Tipos de proceso (Expulsivo, No Expulsivo)
- Cálculo automático de tiempos de ejecución
- Manejo de quantum y tiempo restante
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EstadoProceso(Enum):
    """
    Estados posibles de un proceso en el sistema.
    
    Attributes:
        LISTO: Proceso listo para ejecutar
        EJECUCION: Proceso en ejecución
        TERMINADO: Proceso finalizado
    """
    LISTO = "LISTO"
    EJECUCION = "EJECUCION"
    TERMINADO = "TERMINADO"

class TipoProceso(Enum):
    """
    Tipos de proceso según su comportamiento con el quantum.
    
    Attributes:
        EXPULSIVO: Proceso que puede ser interrumpido al terminar su quantum
        NO_EXPULSIVO: Proceso que no puede ser interrumpido hasta terminar
    """
    EXPULSIVO = 0
    NO_EXPULSIVO = 1

@dataclass
class Proceso:
    """
    Clase que representa un proceso del sistema operativo.
    
    Attributes:
        id (int): Número consecutivo del catálogo
        pid (int): PID del proceso del sistema
        nombre (str): Nombre del ejecutable
        nombre_catalogo (str): Nombre en el catálogo (PID_nombre)
        usuario (str): Usuario que ejecuta el proceso
        descripcion (str): Descripción del proceso
        prioridad (TipoProceso): Tipo de proceso (expulsivo/no expulsivo)
        estado (EstadoProceso): Estado actual del proceso
        tiempo_restante (Optional[int]): Tiempo restante de ejecución
        tiempo_inicio (Optional[int]): Momento en que inició la ejecución
        tiempo_fin (Optional[int]): Momento en que terminó la ejecución
        tiempo_espera (int): Tiempo total de espera
        tiempo_respuesta (int): Tiempo hasta primera ejecución
        tiempo_retorno (int): Tiempo total de ejecución
    """
    id: int  # Número consecutivo del catálogo
    pid: int  # PID del proceso del sistema
    nombre: str  # Nombre del ejecutable
    nombre_catalogo: str  # Nombre en el catálogo (PID_nombre)
    usuario: str  # Usuario que ejecuta el proceso
    descripcion: str  # Descripción del proceso
    prioridad: TipoProceso  # 0 = expulsivo, 1 = no expulsivo
    estado: EstadoProceso = EstadoProceso.LISTO
    tiempo_restante: Optional[int] = None
    tiempo_inicio: Optional[int] = None
    tiempo_fin: Optional[int] = None
    tiempo_espera: int = 0
    tiempo_respuesta: int = 0
    tiempo_retorno: int = 0
    
    def __post_init__(self):
        """
        Inicializa valores por defecto después de la creación del objeto.
        El tiempo restante se calcula como la longitud de la descripción,
        donde cada carácter representa un quantum de ejecución.
        """
        if self.tiempo_restante is None:
            self.tiempo_restante = len(self.descripcion)  # Cada carácter es un quantum
            
    def actualizar_estado(self, nuevo_estado: EstadoProceso, tiempo_actual: int):
        """
        Actualiza el estado del proceso y calcula los tiempos correspondientes.
        
        Args:
            nuevo_estado (EstadoProceso): Nuevo estado del proceso
            tiempo_actual (int): Tiempo actual de la simulación
            
        Note:
            - Al iniciar ejecución se registra el tiempo de inicio
            - Al terminar se calculan tiempos de retorno, respuesta y espera
        """
        self.estado = nuevo_estado
        if nuevo_estado == EstadoProceso.EJECUCION and self.tiempo_inicio is None:
            self.tiempo_inicio = tiempo_actual
        elif nuevo_estado == EstadoProceso.TERMINADO:
            self.tiempo_fin = tiempo_actual
            self.tiempo_retorno = self.tiempo_fin - self.tiempo_inicio
            self.tiempo_respuesta = self.tiempo_inicio
            self.tiempo_espera = self.tiempo_retorno - len(self.descripcion)
            
    def ejecutar(self, quantum: int) -> int:
        """
        Ejecuta el proceso por un tiempo determinado.
        
        Args:
            quantum (int): Tiempo máximo de ejecución permitido
            
        Returns:
            int: Tiempo real de ejecución (puede ser menor que quantum
                 si el proceso termina antes)
        """
        tiempo_ejecutado = min(quantum, self.tiempo_restante)
        self.tiempo_restante -= tiempo_ejecutado
        return tiempo_ejecutado 