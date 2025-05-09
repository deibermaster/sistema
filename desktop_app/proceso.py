from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable
import threading
import time
from datetime import datetime
from .file_writer import escribir_caracter, crear_archivo_proceso

@dataclass
class Proceso:
    pid: int
    nombre: str
    usuario: str
    descripcion: str
    prioridad: int  # 0=Expulsivo, 1=No expulsivo
    estado: str = "Listo"
    t_llegada: int = 0
    t_final: int = 0
    rafaga_total: int = 0
    rafaga_restante: int = 0
    num_ejecuciones: int = 0
    turnaround: int = 0
    historial: List[Tuple[str, int]] = field(default_factory=list)
    callback: Optional[Callable] = None
    archivo: Optional[str] = None
    
    def __post_init__(self):
        """Inicializa los valores calculados"""
        self.rafaga_total = len(self.descripcion)
        self.rafaga_restante = self.rafaga_total
        self.archivo = crear_archivo_proceso(self.pid, self.nombre, self.descripcion)
        
    def log(self, mensaje: str):
        """Registra un mensaje con timestamp y PID"""
        if self.callback:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self.callback(f"[{timestamp}] [PID={self.pid}] {mensaje}")
            
    def cambiar_estado(self, nuevo_estado: str):
        """Cambia el estado del proceso y registra el cambio"""
        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.log(f"Estado {estado_anterior} → {nuevo_estado}")
        
    def ejecutar(self, th: int, pausa_event: threading.Event):
        """Ejecuta el proceso copiando su descripción carácter a carácter"""
        self.cambiar_estado("Ejecución")
        self.historial.append(("Ejecución", 0))
        
        self.log(f"Hilo iniciado. Descripción tiene {len(self.descripcion)} caracteres → ráfaga total= TH×{len(self.descripcion)} = {th * len(self.descripcion)}ms")
        
        for i, char in enumerate(self.descripcion):
            # Esperar si está pausado
            pausa_event.wait()
            
            # Copiar carácter
            escribir_caracter(self.archivo, char)
            self.rafaga_restante -= 1
            self.num_ejecuciones += 1
            
            self.log(f"Copiado carácter {i+1}/{len(self.descripcion)} ('{char}'). Ráfaga restante={self.rafaga_restante * th}ms")
            
            # Dormir TH ms
            time.sleep(th / 1000)
            
        self.cambiar_estado("Terminado")
        self.t_final = self.num_ejecuciones * th
        self.turnaround = self.t_final - self.t_llegada
        self.historial.append(("Terminado", self.t_final))
        
        self.log(f"Estado Ejecución → Terminado. Tiempo final= {self.t_final}ms. Turnaround={self.t_final}–{self.t_llegada}={self.turnaround}ms")
            
    def to_dict(self) -> dict:
        """Convierte el proceso a un diccionario"""
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