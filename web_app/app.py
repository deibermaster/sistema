import sys
import os
import json
import sqlite3
import threading
import time
from datetime import datetime
from collections import deque
from typing import List, Dict, Optional
from flask import Flask, render_template, jsonify, request, abort
from werkzeug.exceptions import HTTPException

from config import DB_PATH, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from desktop_client import (
    fetch_procesos_desktop,
    DesktopClientError,
    DesktopConnectionError,
    DesktopTimeoutError,
    DesktopResponseError
)

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.simulacion import Simulador, ResultadoSimulacion
from models.proceso import Proceso, EstadoProceso

# --- Configuración de BD ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS simulaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            quantum INTEGER,
            th INTEGER,
            estado TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS resultados (
            sim_id INTEGER,
            pid INTEGER,
            nombre TEXT,
            usuario TEXT,
            prioridad INTEGER,
            t_llegada INTEGER,
            rafaga_total INTEGER,
            t_final INTEGER,
            turnaround INTEGER,
            estado TEXT,
            historial TEXT,
            PRIMARY KEY (sim_id, pid)
        )''')
        conn.commit()
init_db()

app = Flask(__name__)

# Variables globales para el estado de la simulación
simulaciones = {}  # id: {hilo, colas, ...}
simulacion_id_counter = 1
simulaciones_lock = threading.Lock()

# --- Utilidades ---
def guardar_simulacion_bd(quantum, th, estado):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO simulaciones (fecha, quantum, th, estado) VALUES (?, ?, ?, ?)",
                  (datetime.now().isoformat(), quantum, th, estado))
        sim_id = c.lastrowid
        conn.commit()
        return sim_id

def guardar_resultados_bd(sim_id, procesos):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for proc in procesos:
            c.execute("""
                INSERT OR REPLACE INTO resultados (sim_id, pid, nombre, usuario, prioridad, t_llegada, rafaga_total, t_final, turnaround, estado, historial)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sim_id, proc['pid'], proc['nombre'], proc['usuario'], proc['prioridad'],
                proc['t_llegada'], proc['rafaga_total'], proc['t_final'], proc['turnaround'],
                proc['estado'], json.dumps(proc['historial'])
            ))
        conn.commit()

def cargar_resultados_bd(sim_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM resultados WHERE sim_id=?", (sim_id,))
        rows = c.fetchall()
        resultados = []
        for row in rows:
            resultados.append({
                'pid': row[1], 'nombre': row[2], 'usuario': row[3], 'prioridad': row[4],
                't_llegada': row[5], 'rafaga_total': row[6], 't_final': row[7],
                'turnaround': row[8], 'estado': row[9], 'historial': json.loads(row[10])
            })
        return resultados

def cargar_simulaciones_bd():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, fecha, quantum, th, estado FROM simulaciones ORDER BY id DESC")
        return [dict(zip(['id','fecha','quantum','th','estado'], row)) for row in c.fetchall()]

def simular_round_robin(sim_id, procesos, th, quantum):
    cola_listos = deque(procesos)
    cola_ejecucion = deque()
    cola_terminados = []
    tiempo_global = 0
    pausa_event = threading.Event()
    pausa_event.set()
    simulaciones[sim_id]['pausa_event'] = pausa_event
    simulaciones[sim_id]['estado'] = 'ejecutando'
    
    while simulaciones[sim_id]['estado'] == 'ejecutando' and (cola_listos or cola_ejecucion):
        pausa_event.wait()
        if cola_listos and not cola_ejecucion:
            proceso = cola_listos.popleft()
            proceso['estado'] = "Ejecución"
            cola_ejecucion.append(proceso)
            
        if cola_ejecucion:
            proceso = cola_ejecucion[0]
            tiempo_ejecutado = min(quantum, proceso['rafaga_restante'])
            time.sleep(tiempo_ejecutado * th / 1000)
            proceso['rafaga_restante'] -= tiempo_ejecutado
            proceso['historial'].append(("Ejecución", tiempo_ejecutado))
            
            if proceso['rafaga_restante'] <= 0:
                proceso['estado'] = "Terminado"
                proceso['t_final'] = tiempo_global + tiempo_ejecutado
                proceso['turnaround'] = proceso['t_final'] - proceso['t_llegada']
                cola_terminados.append(proceso)
                cola_ejecucion.popleft()
            else:
                cola_ejecucion.popleft()
                if proceso['prioridad'] == 0:
                    proceso['estado'] = "Listo"
                    cola_listos.append(proceso)
                else:
                    cola_ejecucion.append(proceso)
                    
        tiempo_global += tiempo_ejecutado
        
    simulaciones[sim_id]['estado'] = 'finalizada'
    guardar_resultados_bd(sim_id, cola_terminados)

# --- Rutas ---
@app.route('/')
def index():
    """Renderiza la página principal"""
    return render_template('index.html')

@app.route('/api/procesos', methods=['GET'])
def obtener_procesos():
    """Obtiene la lista de procesos desde la aplicación de escritorio"""
    try:
        procesos = fetch_procesos_desktop()
        return jsonify(procesos)
    except DesktopConnectionError as e:
        return jsonify({'error': str(e)}), 503
    except DesktopTimeoutError as e:
        return jsonify({'error': str(e)}), 504
    except DesktopResponseError as e:
        return jsonify({'error': str(e)}), 502

@app.route('/api/simular', methods=['POST'])
def simular():
    """Inicia una nueva simulación"""
    try:
        th = int(request.args.get('th', 100))
        quantum = int(request.args.get('quantum', 1))
        
        # Obtener procesos desde la app de escritorio
        procesos = fetch_procesos_desktop()
        
        # Filtrar por PIDs seleccionados si se especifican
        selected_pids = request.json.get('pids', [p['pid'] for p in procesos])
        procesos_seleccionados = [p for p in procesos if p['pid'] in selected_pids]
        
        if not procesos_seleccionados:
            abort(400, description="No se seleccionó ningún proceso válido")
            
        # Iniciar simulación
        sim_id = guardar_simulacion_bd(quantum, th, 'ejecutando')
        with simulaciones_lock:
            simulaciones[sim_id] = {'estado': 'ejecutando', 'procesos': procesos_seleccionados}
            
        hilo = threading.Thread(
            target=simular_round_robin,
            args=(sim_id, procesos_seleccionados, th, quantum),
            daemon=True
        )
        hilo.start()
        simulaciones[sim_id]['hilo'] = hilo
        
        return jsonify({'simulation_id': sim_id}), 202
        
    except DesktopConnectionError as e:
        return jsonify({'error': str(e)}), 503
    except DesktopTimeoutError as e:
        return jsonify({'error': str(e)}), 504
    except DesktopResponseError as e:
        return jsonify({'error': str(e)}), 502
    except ValueError as e:
        return jsonify({'error': f"Parámetros inválidos: {str(e)}"}), 400

@app.route('/api/simular/<int:sim_id>', methods=['GET'])
def estado_simulacion(sim_id):
    """Obtiene el estado actual de una simulación"""
    with simulaciones_lock:
        sim = simulaciones.get(sim_id)
        if not sim:
            return jsonify({'error': 'Simulación no encontrada'}), 404
        return jsonify({'estado': sim['estado']})

@app.route('/api/simular/<int:sim_id>/pausar', methods=['POST'])
def pausar_simulacion(sim_id):
    """Pausa una simulación en curso"""
    with simulaciones_lock:
        sim = simulaciones.get(sim_id)
        if not sim:
            return jsonify({'error': 'Simulación no encontrada'}), 404
        sim['pausa_event'].clear()
        sim['estado'] = 'pausada'
    return jsonify({'mensaje': 'Simulación pausada'})

@app.route('/api/simular/<int:sim_id>/reiniciar', methods=['POST'])
def reiniciar_simulacion(sim_id):
    """Reinicia una simulación pausada"""
    with simulaciones_lock:
        sim = simulaciones.get(sim_id)
        if not sim:
            return jsonify({'error': 'Simulación no encontrada'}), 404
        sim['pausa_event'].set()
        sim['estado'] = 'ejecutando'
    return jsonify({'mensaje': 'Simulación reanudada'})

@app.route('/api/resultados/<int:sim_id>', methods=['GET'])
def resultados_simulacion(sim_id):
    """Obtiene los resultados de una simulación"""
    resultados = cargar_resultados_bd(sim_id)
    if not resultados:
        return jsonify({'error': 'No hay resultados para esta simulación'}), 404
    return jsonify(resultados)

@app.route('/api/historicos', methods=['GET'])
def historicos():
    """Obtiene el historial de simulaciones"""
    return jsonify(cargar_simulaciones_bd())

# --- Manejador de errores ---
@app.errorhandler(HTTPException)
def handle_http_error(error):
    """Maneja errores HTTP de forma consistente"""
    response = jsonify({
        'error': error.description,
        'code': error.code
    })
    response.status_code = error.code
    return response

if __name__ == '__main__':
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    ) 