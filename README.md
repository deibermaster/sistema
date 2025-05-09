# Simulador de Procesos: Desktop y Web

## Descripción General

Este proyecto implementa un sistema de simulación de procesos que consta de dos aplicaciones:

- **Aplicación de Escritorio (Desktop):** Permite seleccionar procesos reales del sistema, simular su ejecución, generar un archivo XML y exponerlo mediante un servidor local.
- **Aplicación Web (Web):** Consume el XML generado por la app de escritorio, permite seleccionar procesos, simular Round Robin, visualizar resultados y consultar históricos.

---

## Estructura del Proyecto

```
/carpeta_del_proyecto/
│
├── desktop_app/
│   ├── main.py                # App principal de escritorio (Tkinter)
│   ├── serve_xml.py           # Servidor Flask para exponer procesos.xml
│   ├── procesos.xml           # Archivo XML generado con los procesos
│   ├── catalog.py, proceso.py, ...
│   └── ...
│
├── web_app/
│   ├── app.py                 # Backend Flask
│   ├── config.py              # Configuración de endpoints y BD
│   ├── desktop_client.py      # Cliente para consumir el XML
│   ├── templates/index.html   # Frontend web (Bootstrap, JS)
│   └── ...
│
├── README.md                  # (Este archivo)
└── ...
```

---

## Requisitos

- **Python 3.8+**
- **Dependencias Desktop:**
  - tkinter
  - psutil
  - flask (solo para `serve_xml.py`)
- **Dependencias Web:**
  - flask
  - requests
  - sqlite3
  - plotly, bootstrap, toastr (CDN en el frontend)

Instala dependencias con:
```bash
pip install flask psutil requests
```

---

## Uso: App de Escritorio

1. **Ejecuta la app de escritorio:**
   ```bash
   python desktop_app/main.py
   ```
2. **Selecciona procesos:**
   - Indica el número de procesos, criterio (CPU/Memoria), TH y quantum.
   - Usa el botón "Seleccionar Procesos".
   - Se generará automáticamente el archivo `desktop_app/procesos.xml`.
3. **Inicia el servidor Flask para exponer el XML:**
   ```bash
   python desktop_app/serve_xml.py
   ```
   - El endpoint estará disponible en: [http://localhost:5000/procesos](http://localhost:5000/procesos)

---

## Uso: App Web

1. **Configura la URL del endpoint en `web_app/config.py`:**
   ```python
   DESKTOP_API_URL = os.getenv("DESKTOP_API_URL", "http://localhost:5000/procesos")
   ```
2. **Ejecuta la app web:**
   ```bash
   python web_app/app.py
   ```
   - El frontend estará disponible en: [http://127.0.0.1:5001/](http://127.0.0.1:5001/)
3. **Carga procesos y simula:**
   - Al entrar, la web carga los procesos del XML.
   - Selecciona procesos, define quantum y TH, y ejecuta la simulación.
   - Visualiza resultados, diagrama de Gantt y consulta históricos.

---

## Flujo de Trabajo

```
[Desktop App]
 ↓
Captura procesos reales → genera archivo XML → publica servicio API XML en localhost:5000
 ↓
[Web App]
 ↓
Consulta el API XML → muestra procesos → usuario selecciona → simula con RR → muestra resultados y gráficos
```

---

## Ejemplo de XML generado

```xml
<procesos>
  <proceso>
    <catalogo>1</catalogo>
    <nombre_catalogo>Grupo1</nombre_catalogo>
    <pid>1234</pid>
    <nombre>chrome.exe</nombre>
    <usuario>Juan</usuario>
    <prioridad>0</prioridad>
    <tLlegada>0</tLlegada>
    <rafaga>3400</rafaga>
  </proceso>
  <!-- Más procesos -->
</procesos>
```

---

## Consideraciones y Buenas Prácticas

- **El servidor Flask de la desktop debe estar corriendo para que la web funcione.**
- **Si la web no puede conectar, muestra un error claro (503/504).**
- **El XML se actualiza cada vez que seleccionas procesos en la desktop.**
- **La simulación Round Robin y el almacenamiento de históricos se realiza en la web.**
- **Puedes modificar el puerto en ambos lados si lo necesitas, pero deben coincidir.**

---

## Créditos y Licencia

- Autor: Deiber Adalberto Ramirez Molina
- Licencia: MIT

---

## Preguntas Frecuentes (FAQ)

**¿Qué hago si la web no carga procesos?**
- Verifica que el servidor Flask de la desktop esté corriendo y el XML exista.
- Prueba [http://localhost:5000/procesos](http://localhost:5000/procesos) en tu navegador.

**¿Puedo cambiar el número de procesos o el criterio?**
- Sí, desde la interfaz de la app de escritorio.

**¿Dónde se guardan los históricos?**
- En la base de datos SQLite de la app web (`simulaciones.db`).

**¿Puedo pausar/reanudar la simulación?**
- Sí, desde la interfaz web.

---

¡Listo! Con este README tienes toda la documentación para instalar, ejecutar y entender el flujo completo del sistema. 