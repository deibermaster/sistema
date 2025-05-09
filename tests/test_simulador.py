import pytest
from models.proceso import Proceso, EstadoProceso
from models.simulacion import Simulador, ResultadoSimulacion

def test_crear_proceso():
    proceso = Proceso(
        id=1,
        nombre="Test",
        tiempo_llegada=0,
        tiempo_servicio=5,
        prioridad=1
    )
    
    assert proceso.id == 1
    assert proceso.nombre == "Test"
    assert proceso.tiempo_llegada == 0
    assert proceso.tiempo_servicio == 5
    assert proceso.prioridad == 1
    assert proceso.estado == EstadoProceso.LISTO
    assert proceso.tiempo_restante == 5

def test_actualizar_estado():
    proceso = Proceso(
        id=1,
        nombre="Test",
        tiempo_llegada=0,
        tiempo_servicio=5,
        prioridad=1
    )
    
    proceso.actualizar_estado(EstadoProceso.EJECUCION, 1)
    assert proceso.estado == EstadoProceso.EJECUCION
    assert proceso.tiempo_inicio == 1
    
    proceso.actualizar_estado(EstadoProceso.TERMINADO, 6)
    assert proceso.estado == EstadoProceso.TERMINADO
    assert proceso.tiempo_fin == 6
    assert proceso.tiempo_retorno == 6
    assert proceso.tiempo_respuesta == 1
    assert proceso.tiempo_espera == 1

def test_ejecutar_proceso():
    proceso = Proceso(
        id=1,
        nombre="Test",
        tiempo_llegada=0,
        tiempo_servicio=5,
        prioridad=1
    )
    
    tiempo_ejecutado = proceso.ejecutar(3)
    assert tiempo_ejecutado == 3
    assert proceso.tiempo_restante == 2
    
    tiempo_ejecutado = proceso.ejecutar(3)
    assert tiempo_ejecutado == 2
    assert proceso.tiempo_restante == 0

def test_simulador():
    simulador = Simulador(quantum=2)
    
    # Agregar procesos
    p1 = Proceso(id=1, nombre="P1", tiempo_llegada=0, tiempo_servicio=4, prioridad=1)
    p2 = Proceso(id=2, nombre="P2", tiempo_llegada=1, tiempo_servicio=3, prioridad=2)
    
    simulador.agregar_proceso(p1)
    simulador.agregar_proceso(p2)
    
    # Iniciar simulación
    simulador.iniciar_simulacion()
    
    # Ejecutar pasos
    assert simulador.siguiente_paso()  # P1 ejecuta 2 unidades
    assert p1.tiempo_restante == 2
    assert p1.estado == EstadoProceso.LISTO
    
    assert simulador.siguiente_paso()  # P2 ejecuta 2 unidades
    assert p2.tiempo_restante == 1
    assert p2.estado == EstadoProceso.LISTO
    
    assert simulador.siguiente_paso()  # P1 ejecuta 2 unidades
    assert p1.tiempo_restante == 0
    assert p1.estado == EstadoProceso.TERMINADO
    
    assert simulador.siguiente_paso()  # P2 ejecuta 1 unidad
    assert p2.tiempo_restante == 0
    assert p2.estado == EstadoProceso.TERMINADO
    
    # Verificar resultados
    resultados = simulador.obtener_resultados()
    assert resultados is not None
    assert resultados.tiempo_total == 6
    assert len(resultados.procesos_no_expulsivos) == 0  # Ningún proceso es no expulsivo con quantum=2

def test_simulador_pausa():
    simulador = Simulador(quantum=2)
    
    p1 = Proceso(id=1, nombre="P1", tiempo_llegada=0, tiempo_servicio=4, prioridad=1)
    simulador.agregar_proceso(p1)
    simulador.iniciar_simulacion()
    
    # Ejecutar un paso
    assert simulador.siguiente_paso()
    
    # Pausar simulación
    simulador.pausar_simulacion()
    assert not simulador.siguiente_paso()
    
    # Reanudar simulación
    simulador.reanudar_simulacion()
    assert simulador.siguiente_paso() 