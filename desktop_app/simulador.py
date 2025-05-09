from collections import deque
import threading
import time
from typing import List, Callable, Optional
from datetime import datetime
from .proceso import Proceso

class Simulador:
    def __init__(self, th: int, quantum: int):
        self.th = th
        self.quantum = quantum
        self.cola_listos = deque()
        self.cola_ejecucion = deque()
        self.cola_terminados = []
        self.tiempo_global = 0
        self.pausa_event = threading.Event()
        self.pausa_event.set()
        self.simulacion_activa = False
        self.callback: Optional[Callable] = None
        
    def log(self, mensaje: str):
        """Registra un mensaje con timestamp"""
        if self.callback:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self.callback(f"[{timestamp}] {mensaje}")
        
    def iniciar(self, procesos: List[Proceso], callback: Optional[Callable] = None):
        """Inicia la simulación con la lista de procesos"""
        self.callback = callback
        self.cola_listos = deque(procesos)
        self.cola_ejecucion.clear()
        self.cola_terminados.clear()
        self.tiempo_global = 0
        self.simulacion_activa = True
        
        # Configurar callback para cada proceso
        for proc in self.cola_listos:
            proc.callback = callback
            
        # Configurar tiempos de llegada
        for i, proc in enumerate(self.cola_listos):
            proc.t_llegada = i
            
        self.log(f"Simulación iniciada con {len(procesos)} procesos")
        self.log(f"TH={self.th}ms, Quantum={self.quantum}ms")
        
        # Iniciar hilo de simulación
        threading.Thread(target=self._ejecutar_simulacion, daemon=True).start()
        
    def _ejecutar_simulacion(self):
        """Ejecuta la simulación en un hilo separado"""
        while self.simulacion_activa:
            self.pausa_event.wait()  # Esperar si está pausado
            
            # Mover proceso de listos a ejecución si hay espacio
            if self.cola_listos and not self.cola_ejecucion:
                proceso = self.cola_listos.popleft()
                proceso.cambiar_estado("Ejecución")
                proceso.num_ejecuciones += 1
                self.cola_ejecucion.append(proceso)
                
                self.log(f"CPU asignada a {proceso.nombre} (PID: {proceso.pid})")
                self.log(f"  - Ráfaga restante: {proceso.rafaga_restante * self.th}ms")
                
            # Ejecutar quantum
            if self.cola_ejecucion:
                proceso = self.cola_ejecucion[0]
                tiempo_ejecutado = min(self.quantum, proceso.rafaga_restante)
                
                # Simular ejecución
                time.sleep(tiempo_ejecutado * self.th / 1000)
                proceso.rafaga_restante -= tiempo_ejecutado
                proceso.historial.append(("Ejecución", tiempo_ejecutado))
                
                self.log(f"Quantum completado para {proceso.nombre} (PID: {proceso.pid})")
                self.log(f"  - Tiempo ejecutado: {tiempo_ejecutado * self.th}ms")
                self.log(f"  - Ráfaga restante: {proceso.rafaga_restante * self.th}ms")
                
                # Verificar si terminó
                if proceso.rafaga_restante <= 0:
                    proceso.cambiar_estado("Terminado")
                    proceso.t_final = self.tiempo_global + tiempo_ejecutado
                    proceso.turnaround = proceso.t_final - proceso.t_llegada
                    self.cola_terminados.append(proceso)
                    self.cola_ejecucion.popleft()
                    
                    self.log(f"Proceso {proceso.nombre} (PID: {proceso.pid}) ha terminado")
                    self.log(f"  - Tiempo final: {proceso.t_final}ms")
                    self.log(f"  - Turnaround: {proceso.turnaround}ms")
                else:
                    # Reinsertar según prioridad
                    self.cola_ejecucion.popleft()
                    if proceso.prioridad == 0:  # Expulsivo
                        proceso.cambiar_estado("Listo")
                        self.cola_listos.append(proceso)
                        self.log(f"Proceso {proceso.nombre} (PID: {proceso.pid}) vuelve a cola de listos (Expulsivo)")
                    else:  # No expulsivo
                        self.cola_ejecucion.append(proceso)
                        self.log(f"Proceso {proceso.nombre} (PID: {proceso.pid}) continúa en ejecución (No Expulsivo)")
                    
            self.tiempo_global += tiempo_ejecutado
            
            self.log(f"Tiempo global: {self.tiempo_global}ms")
            
            # Verificar si terminó la simulación
            if not self.cola_listos and not self.cola_ejecucion:
                self.simulacion_activa = False
                self.log("Simulación completada")
                self.log(f"Procesos terminados: {len(self.cola_terminados)}")
                self.log(f"Tiempo total: {self.tiempo_global}ms")
                    
    def pausar(self):
        """Pausa la simulación"""
        self.pausa_event.clear()
        self.log("Simulación pausada")
        
    def reanudar(self):
        """Reanuda la simulación"""
        self.pausa_event.set()
        self.log("Simulación reanudada")
        
    def detener(self):
        """Detiene la simulación"""
        self.simulacion_activa = False
        self.pausa_event.set()
        self.log("Simulación detenida")
        
    def obtener_estado(self) -> dict:
        """Retorna el estado actual de la simulación"""
        return {
            'cola_listos': [p.to_dict() for p in self.cola_listos],
            'cola_ejecucion': [p.to_dict() for p in self.cola_ejecucion],
            'cola_terminados': [p.to_dict() for p in self.cola_terminados],
            'tiempo_global': self.tiempo_global
        } 