from typing import List, Dict, Any
from .proceso import Proceso
from .process_manager import listar_procesos

class Catalogo:
    def __init__(self, id: int, nombre: str):
        self.id = id
        self.nombre = nombre
        self.procesos: List[Proceso] = []
        
    def agregar_proceso(self, proceso: Proceso):
        """Agrega un proceso al catálogo"""
        self.procesos.append(proceso)
        
    def seleccionar_procesos(self, n: int, criterio: str) -> List[Proceso]:
        """Selecciona los n procesos más activos según el criterio"""
        # Obtener procesos del sistema
        procesos_meta = listar_procesos(n, criterio)
        
        # Convertir a objetos Proceso
        for proc_meta in procesos_meta:
            # Determinar prioridad (0=Expulsivo, 1=No expulsivo)
            prioridad = 1 if proc_meta.usuario == 'SYSTEM' else 0
            
            # Crear nuevo Proceso
            proceso = Proceso(
                pid=proc_meta.pid,
                nombre=proc_meta.nombre,
                usuario=proc_meta.usuario,
                descripcion=f"Proceso {proc_meta.nombre}",
                prioridad=prioridad
            )
            self.agregar_proceso(proceso)
            
        return self.procesos
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el catálogo a un diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'procesos': [p.to_dict() for p in self.procesos]
        } 