import pytest
from models.proceso import Proceso, EstadoProceso
from models.simulacion import Simulador

def test_transicion_listo_a_ejecucion():
    proceso = Proceso(
        id=1,
        nombre="Test",
        tiempo_llegada=0,
        tiempo_servicio=5,
        prioridad=1
    )
    
    assert proceso.estado == EstadoProceso.LISTO
    proceso.actualizar_estado(EstadoProceso.EJECUCION, 1)
    assert proceso.estado == EstadoProceso.EJECUCION
    assert proceso.tiempo_inicio == 1

def test_transicion_ejecucion_a_listo():
    proceso = Proceso(
        id=1,
        nombre="Test",
        tiempo_llegada=0,
        tiempo_servicio=5,
        prioridad=1
    )
    
    proceso.actualizar_estado(EstadoProceso.EJECUCION, 1)
    proceso.actualizar_estado(EstadoProceso.LISTO, 2)
    assert proceso.estado == EstadoProceso.LISTO
    assert proceso.tiempo_inicio == 1  # No debe cambiar

def test_transicion_ejecucion_a_terminado():
    proceso = Proceso(
        id=1,
        nombre="Test",
        tiempo_llegada=0,
        tiempo_servicio=5,
        prioridad=1
    )
    
    proceso.actualizar_estado(EstadoProceso.EJECUCION, 1)
    proceso.actualizar_estado(EstadoProceso.TERMINADO, 6)
    assert proceso.estado == EstadoProceso.TERMINADO
    assert proceso.tiempo_fin == 6
    assert proceso.tiempo_retorno == 6
    assert proceso.tiempo_respuesta == 1
    assert proceso.tiempo_espera == 1

def test_transiciones_simulador():
    simulador = Simulador(quantum=2)
    
    p1 = Proceso(id=1, nombre="P1", tiempo_llegada=0, tiempo_servicio=4, prioridad=1)
    p2 = Proceso(id=2, nombre="P2", tiempo_llegada=1, tiempo_servicio=3, prioridad=2)
    
    simulador.agregar_proceso(p1)
    simulador.agregar_proceso(p2)
    simulador.iniciar_simulacion()
    
    # P1: LISTO -> EJECUCION
    assert simulador.siguiente_paso()
    assert p1.estado == EstadoProceso.LISTO  # Vuelve a LISTO después del quantum
    
    # P2: LISTO -> EJECUCION
    assert simulador.siguiente_paso()
    assert p2.estado == EstadoProceso.LISTO  # Vuelve a LISTO después del quantum
    
    # P1: LISTO -> EJECUCION -> TERMINADO
    assert simulador.siguiente_paso()
    assert p1.estado == EstadoProceso.TERMINADO
    
    # P2: LISTO -> EJECUCION -> TERMINADO
    assert simulador.siguiente_paso()
    assert p2.estado == EstadoProceso.TERMINADO

def test_transiciones_con_pausa():
    simulador = Simulador(quantum=2)
    
    p1 = Proceso(id=1, nombre="P1", tiempo_llegada=0, tiempo_servicio=4, prioridad=1)
    simulador.agregar_proceso(p1)
    simulador.iniciar_simulacion()
    
    # P1: LISTO -> EJECUCION
    assert simulador.siguiente_paso()
    assert p1.estado == EstadoProceso.LISTO
    
    # Pausar simulación
    simulador.pausar_simulacion()
    assert not simulador.siguiente_paso()
    assert p1.estado == EstadoProceso.LISTO  # Estado no debe cambiar durante la pausa
    
    # Reanudar simulación
    simulador.reanudar_simulacion()
    assert simulador.siguiente_paso()
    assert p1.estado == EstadoProceso.TERMINADO 