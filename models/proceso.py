from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EstadoProceso(Enum):
    LISTO = "LISTO"
    EJECUCION = "EJECUCION"
    TERMINADO = "TERMINADO"

class TipoProceso(Enum):
    EXPULSIVO = 0
    NO_EXPULSIVO = 1

@dataclass
class Proceso:
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
        if self.tiempo_restante is None:
            self.tiempo_restante = len(self.descripcion)  # Cada carácter es un quantum
            
    def actualizar_estado(self, nuevo_estado: EstadoProceso, tiempo_actual: int):
        self.estado = nuevo_estado
        if nuevo_estado == EstadoProceso.EJECUCION and self.tiempo_inicio is None:
            self.tiempo_inicio = tiempo_actual
        elif nuevo_estado == EstadoProceso.TERMINADO:
            self.tiempo_fin = tiempo_actual
            self.tiempo_retorno = self.tiempo_fin - self.tiempo_inicio
            self.tiempo_respuesta = self.tiempo_inicio
            self.tiempo_espera = self.tiempo_retorno - len(self.descripcion)
            
    def ejecutar(self, quantum: int) -> int:
        tiempo_ejecutado = min(quantum, self.tiempo_restante)
        self.tiempo_restante -= tiempo_ejecutado
        return tiempo_ejecutado 