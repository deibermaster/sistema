"""
Paquete de modelos para la simulación de procesos.
Este módulo exporta las clases y enumeraciones necesarias para
la simulación de procesos del sistema operativo.

Clases exportadas:
- Proceso: Representa un proceso del sistema
- EstadoProceso: Estados posibles de un proceso
- Simulador: Implementa la lógica de simulación Round Robin
- ResultadoSimulacion: Contiene los resultados de una simulación
- TipoFiltro: Tipos de filtro para selección de procesos
"""

from .proceso import Proceso, EstadoProceso
from .simulacion import Simulador, ResultadoSimulacion, TipoFiltro

__all__ = ['Proceso', 'EstadoProceso', 'Simulador', 'ResultadoSimulacion', 'TipoFiltro'] 