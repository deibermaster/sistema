from typing import List, Dict, Optional
from .proceso import Proceso, EstadoProceso
from dataclasses import dataclass
from enum import Enum

class TipoFiltro(Enum):
    CPU = "CPU"
    MEMORIA = "MEMORIA"

@dataclass
class ResultadoSimulacion:
    procesos: List[Proceso]
    tiempo_total: int
    tiempo_medio_espera: float
    tiempo_medio_respuesta: float
    tiempo_medio_retorno: float
    diagrama_gantt: List[Dict[str, int]]
    procesos_no_expulsivos: List[Proceso]

class Simulador:
    def __init__(self, quantum: int = 1):
        self.quantum = quantum
        self.tiempo_actual = 0
        self.procesos: List[Proceso] = []
        self.cola_listos: List[Proceso] = []
        self.proceso_actual: Optional[Proceso] = None
        self.procesos_terminados: List[Proceso] = []
        self.diagrama_gantt: List[Dict[str, int]] = []
        self.pausado = False
        
    def agregar_proceso(self, proceso: Proceso):
        self.procesos.append(proceso)
        
    def iniciar_simulacion(self):
        self.tiempo_actual = 0
        self.cola_listos = []
        self.proceso_actual = None
        self.procesos_terminados = []
        self.diagrama_gantt = []
        self.pausado = False
        
        # Ordenar procesos por tiempo de llegada
        self.procesos.sort(key=lambda p: p.tiempo_llegada)
        
    def pausar_simulacion(self):
        self.pausado = True
        
    def reanudar_simulacion(self):
        self.pausado = False
        
    def siguiente_paso(self) -> bool:
        if self.pausado:
            return False
            
        # Agregar procesos que han llegado
        for proceso in self.procesos:
            if proceso.tiempo_llegada == self.tiempo_actual and proceso not in self.cola_listos:
                self.cola_listos.append(proceso)
                
        # Si no hay proceso actual y hay procesos en cola
        if self.proceso_actual is None and self.cola_listos:
            self.proceso_actual = self.cola_listos.pop(0)
            self.proceso_actual.actualizar_estado(EstadoProceso.EJECUCION, self.tiempo_actual)
            
        # Ejecutar proceso actual
        if self.proceso_actual:
            tiempo_ejecutado = self.proceso_actual.ejecutar(self.quantum)
            self.diagrama_gantt.append({
                "proceso_id": self.proceso_actual.id,
                "inicio": self.tiempo_actual,
                "fin": self.tiempo_actual + tiempo_ejecutado
            })
            
            self.tiempo_actual += tiempo_ejecutado
            
            # Verificar si el proceso ha terminado
            if self.proceso_actual.tiempo_restante == 0:
                self.proceso_actual.actualizar_estado(EstadoProceso.TERMINADO, self.tiempo_actual)
                self.procesos_terminados.append(self.proceso_actual)
                self.proceso_actual = None
            else:
                # El proceso no ha terminado, volver a la cola
                self.proceso_actual.actualizar_estado(EstadoProceso.LISTO, self.tiempo_actual)
                self.cola_listos.append(self.proceso_actual)
                self.proceso_actual = None
        else:
            self.tiempo_actual += 1
            
        # Verificar si la simulación ha terminado
        return len(self.procesos_terminados) < len(self.procesos)
        
    def obtener_resultados(self) -> ResultadoSimulacion:
        if not self.procesos_terminados:
            return None
            
        tiempo_total = self.tiempo_actual
        tiempo_medio_espera = sum(p.tiempo_espera for p in self.procesos_terminados) / len(self.procesos_terminados)
        tiempo_medio_respuesta = sum(p.tiempo_respuesta for p in self.procesos_terminados) / len(self.procesos_terminados)
        tiempo_medio_retorno = sum(p.tiempo_retorno for p in self.procesos_terminados) / len(self.procesos_terminados)
        
        # Identificar procesos no expulsivos (aquellos que no fueron interrumpidos)
        procesos_no_expulsivos = [
            p for p in self.procesos_terminados
            if p.tiempo_servicio == p.tiempo_retorno - p.tiempo_llegada
        ]
        
        return ResultadoSimulacion(
            procesos=self.procesos_terminados,
            tiempo_total=tiempo_total,
            tiempo_medio_espera=tiempo_medio_espera,
            tiempo_medio_respuesta=tiempo_medio_respuesta,
            tiempo_medio_retorno=tiempo_medio_retorno,
            diagrama_gantt=self.diagrama_gantt,
            procesos_no_expulsivos=procesos_no_expulsivos
        ) 