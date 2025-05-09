# Manual de Usuario: Simulador de Procesos

---

## 1. Introducción

Este sistema permite simular la planificación de procesos usando el algoritmo Round Robin, visualizando el avance y resultados tanto en una aplicación de escritorio como en una aplicación web.

---

## 2. Uso de la Aplicación de Escritorio

### 2.1. Inicio
- Ejecuta la app con:
  ```bash
  python desktop_app/main.py
  ```
- Se abrirá una ventana con varias secciones.

### 2.2. Selección de Procesos
- Indica el **número de procesos** a capturar.
- Elige el **criterio** (CPU o Memoria) para seleccionar los procesos más activos.
- Define los parámetros de simulación:
  - **TH (ms):** Tiempo de espera entre cada carácter simulado.
  - **Quantum (ms):** Quantum para la simulación Round Robin.
- Haz clic en **"Seleccionar Procesos"**.
- Se mostrará una tabla con los procesos seleccionados y se generará el archivo `procesos.xml`.

### 2.3. Simulación Local (opcional)
- Puedes iniciar una simulación local desde la app de escritorio para ver el avance de los procesos seleccionados.
- Usa los botones para **iniciar**, **pausar/reanudar** o **detener** la simulación.
- Observa los logs en la consola inferior.

### 2.4. Servir el XML
- En una terminal, ejecuta:
  ```bash
  python desktop_app/serve_xml.py
  ```
- Esto expone el archivo XML en [http://localhost:5000/procesos](http://localhost:5000/procesos)

---

## 3. Uso de la Aplicación Web

### 3.1. Inicio
- Ejecuta la app web con:
  ```bash
  python web_app/app.py
  ```
- Abre tu navegador en [http://127.0.0.1:5001/](http://127.0.0.1:5001/)

### 3.2. Cargar y Seleccionar Procesos
- La web carga automáticamente los procesos del XML.
- Verás tarjetas con los procesos disponibles.
- Haz clic en las tarjetas para seleccionar los procesos que deseas simular (se resaltan).

### 3.3. Configuración de Simulación
- Define el **Quantum** y el **Tiempo de Espera (TH)** en los campos correspondientes.
- Elige el modo "Simulación en Vivo" o "Histórico".

### 3.4. Control de Simulación
- Usa los botones:
  - **Iniciar Simulación:** Comienza la simulación Round Robin con los procesos seleccionados.
  - **Pausar:** Detiene temporalmente la simulación.
  - **Reanudar:** Continúa la simulación pausada.
  - **Detener:** Finaliza la simulación actual.

---

## 4. Interpretación de Tablas y Gráficas

### 4.1. Tabla de Resultados
- **PID:** Identificador del proceso.
- **Nombre:** Nombre del proceso.
- **Usuario:** Usuario propietario.
- **Prioridad:** 0 (Expulsivo) o 1 (No expulsivo).
- **T. Llegada:** Tiempo en que el proceso entra al sistema.
- **Ráfaga Total:** Cantidad total de trabajo (caracteres a copiar).
- **T. Final:** Tiempo en que el proceso terminó.
- **Turnaround:** Tiempo total desde llegada hasta finalización.
- **Estado:** Estado actual (Listo, Ejecución, Terminado).

### 4.2. Diagrama de Gantt
- Muestra visualmente el avance de cada proceso a lo largo del tiempo.
- Cada barra representa el tiempo en que un proceso estuvo en ejecución.
- El eje X es el tiempo; el eje Y son los procesos.
- Los colores indican el estado (ejecución, terminado, etc).

---

## 5. Consulta de Históricos
- Puedes cambiar al modo "Histórico" para ver simulaciones anteriores.
- Se listan todas las simulaciones guardadas.
- Al seleccionar una, puedes ver su tabla de resultados y diagrama de Gantt.

---

## 6. Manejo de Errores y Consejos
- Si la web muestra un error al cargar procesos, asegúrate de que el servidor Flask de la desktop esté corriendo y el XML exista.
- Si cambias el número de procesos o el criterio, vuelve a seleccionar procesos en la desktop y recarga la web.
- Puedes pausar y reanudar la simulación en cualquier momento desde la web.

---

## 7. Glosario Rápido
- **Quantum:** Tiempo máximo que un proceso puede estar en ejecución antes de ser interrumpido.
- **TH:** Tiempo de espera entre operaciones simuladas.
- **Turnaround:** Tiempo total que tarda un proceso desde que llega hasta que termina.
- **Expulsivo/No Expulsivo:** Indica si el proceso puede ser interrumpido (0=Sí, 1=No).

---

¡Listo! Con este manual puedes usar, entender y aprovechar todas las funcionalidades del sistema y sus visualizaciones. 