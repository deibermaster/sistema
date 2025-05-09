from dataclasses import dataclass, field
from typing import List, Tuple
import psutil
from datetime import datetime

@dataclass(frozen=True)
class ProcesoMeta:
    pid: int
    nombre: str
    usuario: str
    cpu: float
    memoria: float
    estado: str
    tiempo_creacion: str

@dataclass
class Proceso:
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
        # Calcular ráfaga total basada en la descripción
        self.rafaga_total = len(self.descripcion)
        self.rafaga_restante = self.rafaga_total
        
    def to_dict(self) -> dict:
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
        n: Número de procesos a recuperar
        criterio: "cpu" o "memoria"
        
    Returns:
        Lista de objetos ProcesoMeta ordenados por el criterio
        
    Raises:
        ValueError: Si n es mayor que el total de procesos
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