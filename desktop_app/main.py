import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import time
import sys
import os
from datetime import datetime
import queue
import xml.etree.ElementTree as ET

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_app.catalog import Catalogo
from desktop_app.simulador import Simulador
from desktop_app.rest_server import iniciar_servidor, actualizar_procesos

class CatalogUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Catálogo de Procesos")
        self.root.geometry("1200x800")
        
        # Inicializar variables
        self.catalogo = None
        self.simulador = None
        
        # Colas para comunicación entre hilos
        self.log_queue = queue.Queue()
        self.update_queue = queue.Queue()
        self.msg_queue = queue.Queue()  # Cola de mensajes entre hilos y GUI
        
        # Mapeo de estados a iconos
        self.estado_iconos = {
            'Listo': '⏳',
            'Ejecución': '▶️',
            'Terminado': '✅'
        }
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Iniciar servidor REST
        threading.Thread(target=iniciar_servidor, daemon=True).start()
        
        # Iniciar actualización de logs y tabla
        self.actualizar_logs()
        self.root.after(100, self.procesa_mensajes)  # Polling de la cola
        self.actualizar_tabla_periodicamente()
        
        # Cargar procesos del sistema al inicio
        self.actualizar_procesos_sistema()
        
        self.item_id_por_pid = {}  # Mapeo PID → item_id en la tabla
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Frame para configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.pack(fill="x", pady=5)
        
        # Campos de configuración
        ttk.Label(config_frame, text="Número de procesos:").grid(row=0, column=0, padx=5)
        self.num_procesos_var = tk.StringVar(value="5")
        ttk.Entry(config_frame, textvariable=self.num_procesos_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="TH (ms):").grid(row=0, column=2, padx=5)
        self.th_var = tk.StringVar(value="100")
        ttk.Entry(config_frame, textvariable=self.th_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(config_frame, text="Quantum (ms):").grid(row=0, column=4, padx=5)
        self.quantum_var = tk.StringVar(value="10")
        ttk.Entry(config_frame, textvariable=self.quantum_var, width=10).grid(row=0, column=5, padx=5)
        
        # Selector de filtro
        ttk.Label(config_frame, text="Filtrar por:").grid(row=0, column=6, padx=5)
        self.filtro_var = tk.StringVar(value="CPU")
        ttk.Radiobutton(config_frame, text="CPU", variable=self.filtro_var, value="CPU").grid(row=0, column=7)
        ttk.Radiobutton(config_frame, text="Memoria", variable=self.filtro_var, value="Memoria").grid(row=0, column=8)
        
        # Frame para tabla y detalles
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=5)
        
        # Frame para tabla de procesos
        table_frame = ttk.LabelFrame(content_frame, text="Procesos del Sistema", padding="10")
        table_frame.pack(side="left", fill="both", expand=True)
        
        columns = ("Catálogo", "PID", "Nombre", "Usuario", "Prioridad", "T.L", "R (ms)", "T.F (ms)", "T.R (ms)", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Configurar colores para estados
        self.tree.tag_configure('Listo', background='#B3E5FC')  # Azul claro
        self.tree.tag_configure('Ejecución', background='#FFE082')  # Amarillo claro
        self.tree.tag_configure('Terminado', background='#C8E6C9')  # Verde claro
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(fill="both", expand=True)
        
        # Scrollbar para tabla
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame para consola de logs
        log_frame = ttk.LabelFrame(main_frame, text="Consola de Logs", padding="10")
        log_frame.pack(fill="x", pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)
        
        # Frame para controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=5)
        
        # Botones de control
        ttk.Button(control_frame, text="Actualizar Procesos", command=self.actualizar_procesos_sistema).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Seleccionar Procesos", command=self.seleccionar_procesos).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Iniciar Simulación", command=self.iniciar_simulacion).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Pausar/Reanudar", command=self.toggle_pausa).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Detener Simulación", command=self.detener_simulacion).pack(side="left", padx=5)
        
    def procesa_mensajes(self):
        """Lee la cola y actualiza tabla y consola en el hilo de la GUI."""
        try:
            while True:
                tipo, payload = self.msg_queue.get_nowait()
                if tipo == 'log':
                    mensaje, color = payload
                    colores_validos = ["black", "orange", "red", "green"]
                    color_valido = color if color in colores_validos else "black"
                    self.log_text.insert(tk.END, mensaje + "\n", color_valido)
                    self.log_text.tag_configure(color_valido, foreground=color_valido)
                    self.log_text.see(tk.END)
                elif tipo == 'update_table':
                    pid, campo, valor = payload
                    item = self.item_id_por_pid.get(pid)
                    if item:
                        self.tree.set(item, campo, valor)
                elif tipo == 'state_change':
                    pid, nuevo_estado = payload
                    item = self.item_id_por_pid.get(pid)
                    if item:
                        self.tree.item(item, tags=(nuevo_estado,))
                        self.tree.set(item, 'Estado', f"{self.estado_iconos[nuevo_estado]} {nuevo_estado}")
        except queue.Empty:
            pass
        self.root.after(100, self.procesa_mensajes)

    def log(self, mensaje: str, tipo: str = "INFO"):
        color = {
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red",
            "SUCCESS": "green"
        }.get(tipo, "black")
        self.msg_queue.put(('log', (mensaje, color)))
        
    def actualizar_logs(self):
        """Actualiza la consola de logs con los mensajes pendientes"""
        while not self.log_queue.empty():
            mensaje, color = self.log_queue.get()
            self.log_text.insert(tk.END, mensaje + "\n", color)
            self.log_text.tag_configure(color, foreground=color)
            self.log_text.see(tk.END)
        self.root.after(100, self.actualizar_logs)
        
    def actualizar_procesos_sistema(self):
        """Actualiza la lista de procesos del sistema"""
        try:
            num_procesos = int(self.num_procesos_var.get())
            
            # Crear catálogo temporal
            catalogo_temp = Catalogo(0, "Sistema")
            procesos = catalogo_temp.seleccionar_procesos(num_procesos, self.filtro_var.get())
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Actualizar tabla
            for proc in procesos:
                self.tree.insert("", "end", values=(
                    "-",
                    proc.pid,
                    proc.nombre,
                    proc.usuario,
                    "No Expulsivo" if proc.prioridad == 1 else "Expulsivo",
                    proc.t_llegada,
                    proc.rafaga_total * int(self.th_var.get()),
                    "-",
                    "-",
                    f"{self.estado_iconos[proc.estado]} {proc.estado}"
                ), tags=(proc.estado,))
                
            self.log(f"Se cargaron {len(procesos)} procesos del sistema", "SUCCESS")
            self.log(f"Filtro aplicado: {self.filtro_var.get()}", "INFO")
            
        except ValueError as e:
            self.log(f"Error al cargar procesos: {str(e)}", "ERROR")
            messagebox.showerror("Error", str(e))
            
    def seleccionar_procesos(self):
        """Selecciona los procesos para la simulación"""
        try:
            num_procesos = int(self.num_procesos_var.get())
            # Pedir número y nombre de catálogo
            num_catalogo = simpledialog.askinteger("Catálogo", "Número de catálogo:")
            nombre_catalogo = simpledialog.askstring("Catálogo", "Nombre de catálogo:")
            if num_catalogo is None or nombre_catalogo is None:
                self.log("Selección de catálogo cancelada", "WARNING")
                return
            # Crear catálogo
            self.catalogo = Catalogo(num_catalogo, nombre_catalogo)
            procesos = self.catalogo.seleccionar_procesos(num_procesos, self.filtro_var.get())
            # Limpiar tabla y mapeo
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.item_id_por_pid.clear()
            # Asignar catálogo, nombre y t_llegada incremental
            for i, proc in enumerate(procesos, start=1):
                proc.catalogo = num_catalogo
                proc.nombre_catalogo = nombre_catalogo
                proc.t_llegada = i - 1
                item = self.tree.insert("", "end", values=(
                    f"{num_catalogo}-{i}",
                    proc.pid,
                    proc.nombre,
                    proc.usuario,
                    "No Expulsivo" if proc.prioridad == 1 else "Expulsivo",
                    proc.t_llegada,
                    proc.rafaga_total * int(self.th_var.get()),
                    "-",
                    "-",
                    f"{self.estado_iconos[proc.estado]} {proc.estado}"
                ), tags=(proc.estado,))
                self.item_id_por_pid[proc.pid] = item
            # Actualizar servidor REST
            actualizar_procesos([p.to_dict() for p in self.catalogo.procesos], self.catalogo.id, self.catalogo.nombre)
            self.log(f"Se han seleccionado {len(procesos)} procesos para simulación", "SUCCESS")
            self.log(f"Catálogo: {num_catalogo} - {nombre_catalogo}", "INFO")
            self.log("Procesos seleccionados:", "INFO")
            for proc in procesos:
                self.log(f"  - {proc.nombre} (PID: {proc.pid}) - {'No Expulsivo' if proc.prioridad == 1 else 'Expulsivo'}", "INFO")
            # Guardar XML actualizado
            guardar_procesos_xml(self.catalogo.procesos, "desktop_app/procesos.xml")
        except ValueError as e:
            self.log(f"Error al seleccionar procesos: {str(e)}", "ERROR")
            messagebox.showerror("Error", str(e))
            
    def iniciar_simulacion(self):
        """Inicia la simulación de procesos (multihilo, carácter a carácter)"""
        if not self.catalogo:
            self.log("Primero seleccione los procesos", "WARNING")
            messagebox.showerror("Error", "Primero seleccione los procesos")
            return
        try:
            th = int(self.th_var.get())
            self.th = th
            self.pausa_event = threading.Event()
            self.pausa_event.set()
            self.hilos = []
            self.simulacion_activa = True
            for proc in self.catalogo.procesos:
                t = threading.Thread(target=self.run_proceso, args=(proc, th), daemon=True)
                t.start()
                self.hilos.append(t)
            self.log("Simulación multihilo iniciada", "SUCCESS")
        except ValueError as e:
            self.log(f"Error al iniciar simulación: {str(e)}", "ERROR")
            messagebox.showerror("Error", str(e))

    def run_proceso(self, proc, th):
        """Simula la ejecución carácter a carácter de un proceso en un hilo"""
        self.msg_queue.put(('log', (f"[{self.now()}] [PID={proc.pid}] Hilo iniciado. Ráfaga total={proc.rafaga_total * th}ms", "INFO")))
        self.msg_queue.put(('state_change', (proc.pid, 'Ejecución')))
        archivo = f"proceso_{proc.pid}.txt"
        with open(archivo, "w", encoding="utf-8") as f:
            for idx, char in enumerate(proc.descripcion, start=1):
                self.pausa_event.wait()
                f.write(char)
                proc.rafaga_restante -= 1
                self.msg_queue.put(('update_table', (proc.pid, 'R (ms)', str(proc.rafaga_restante * th))))
                self.msg_queue.put(('log', (f"[{self.now()}] [PID={proc.pid}] Copiado carácter {idx}/{len(proc.descripcion)} '{char}'. Ráfaga remanente={proc.rafaga_restante * th}ms", "INFO")))
                time.sleep(th / 1000)
        proc.t_final = (idx) * th
        proc.turnaround = proc.t_final - proc.t_llegada * th
        self.msg_queue.put(('state_change', (proc.pid, 'Terminado')))
        self.msg_queue.put(('update_table', (proc.pid, 'T.F (ms)', str(proc.t_final))))
        self.msg_queue.put(('update_table', (proc.pid, 'T.R (ms)', str(proc.turnaround))))
        self.msg_queue.put(('log', (f"[{self.now()}] [PID={proc.pid}] Terminado. T.F={proc.t_final}ms, T.R={proc.turnaround}ms", "SUCCESS")))
        if all(p.estado == 'Terminado' for p in self.catalogo.procesos):
            self.simulacion_activa = False
            self.msg_queue.put(('log', (f"[{self.now()}] Simulación finalizada. Todos los procesos han terminado.", "SUCCESS")))

    def actualizar_tabla_proceso(self, proc):
        """Actualiza la fila de un proceso en la tabla"""
        item = self.item_id_por_pid.get(proc.pid)
        if item:
            self.tree.set(item, 'R (ms)', str(proc.rafaga_restante * self.th))
            self.tree.set(item, 'Estado', f"{self.estado_iconos[proc.estado]} {proc.estado}")
            if proc.estado == 'Terminado':
                self.tree.set(item, 'T.F (ms)', str(proc.t_final))
                self.tree.set(item, 'T.R (ms)', str(proc.turnaround))
            self.tree.item(item, tags=(proc.estado,))

    def cambiar_estado(self, proc, nuevo_estado):
        proc.estado = nuevo_estado
        self.msg_queue.put(('state_change', (proc.pid, nuevo_estado)))

    def now(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def toggle_pausa(self):
        """Pausa o reanuda la simulación"""
        if not hasattr(self, 'pausa_event') or not self.simulacion_activa:
            return
        if self.pausa_event.is_set():
            self.pausa_event.clear()
            self.log(f"[{self.now()}] Simulación en pausa.", "WARNING")
        else:
            self.pausa_event.set()
            self.log(f"[{self.now()}] Simulación reanudada.", "SUCCESS")

    def detener_simulacion(self):
        """Detiene la simulación"""
        if not hasattr(self, 'pausa_event') or not self.simulacion_activa:
            return
        self.simulacion_activa = False
        self.pausa_event.set()
        for proc in self.catalogo.procesos:
            if proc.estado != 'Terminado':
                self.cambiar_estado(proc, 'Terminado')
                proc.t_final = proc.rafaga_total * self.th
                proc.turnaround = proc.t_final - proc.t_llegada * self.th
                self.actualizar_tabla_proceso(proc)
        self.log(f"[{self.now()}] Simulación detenida. Todos los procesos marcados como terminados.", "INFO")

    def actualizar_tabla_periodicamente(self):
        """Actualiza la tabla cada 100ms si la simulación está activa"""
        if self.simulador and self.simulador.simulacion_activa:
            estado = self.simulador.obtener_estado()
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Procesos en ejecución
            for proc in estado['cola_ejecucion']:
                self.tree.insert("", "end", values=(
                    self.catalogo.id,
                    proc['pid'],
                    proc['nombre'],
                    proc['usuario'],
                    "No Expulsivo" if proc['prioridad'] == 1 else "Expulsivo",
                    proc['t_llegada'],
                    proc['rafaga_restante'] * self.simulador.th,
                    "-",
                    "-",
                    f"{self.estado_iconos[proc['estado']]} {proc['estado']}"
                ), tags=(proc['estado'],))
                
            # Procesos terminados
            for proc in estado['cola_terminados']:
                self.tree.insert("", "end", values=(
                    self.catalogo.id,
                    proc['pid'],
                    proc['nombre'],
                    proc['usuario'],
                    "No Expulsivo" if proc['prioridad'] == 1 else "Expulsivo",
                    proc['t_llegada'],
                    proc['rafaga_total'] * self.simulador.th,
                    proc['t_final'],
                    proc['turnaround'],
                    f"{self.estado_iconos[proc['estado']]} {proc['estado']}"
                ), tags=(proc['estado'],))
                
            # Procesos en listos
            for proc in estado['cola_listos']:
                self.tree.insert("", "end", values=(
                    self.catalogo.id,
                    proc['pid'],
                    proc['nombre'],
                    proc['usuario'],
                    "No Expulsivo" if proc['prioridad'] == 1 else "Expulsivo",
                    proc['t_llegada'],
                    proc['rafaga_restante'] * self.simulador.th,
                    "-",
                    "-",
                    f"{self.estado_iconos[proc['estado']]} {proc['estado']}"
                ), tags=(proc['estado'],))
                
        self.root.after(100, self.actualizar_tabla_periodicamente)

def guardar_procesos_xml(procesos, ruta_xml):
    # Crear la carpeta si no existe
    carpeta = os.path.dirname(ruta_xml)
    if carpeta and not os.path.exists(carpeta):
        os.makedirs(carpeta)
    root = ET.Element("procesos")
    for proc in procesos:
        p = ET.SubElement(root, "proceso")
        ET.SubElement(p, "catalogo").text = str(getattr(proc, 'catalogo', 1))
        ET.SubElement(p, "nombre_catalogo").text = getattr(proc, 'nombre_catalogo', 'Grupo1')
        ET.SubElement(p, "pid").text = str(proc.pid)
        ET.SubElement(p, "nombre").text = proc.nombre
        ET.SubElement(p, "usuario").text = proc.usuario
        ET.SubElement(p, "prioridad").text = str(proc.prioridad)
        ET.SubElement(p, "tLlegada").text = str(proc.t_llegada)
        ET.SubElement(p, "rafaga").text = str(proc.rafaga_total)
    tree = ET.ElementTree(root)
    tree.write(ruta_xml, encoding='utf-8', xml_declaration=True)

def main():
    # Iniciar aplicación de escritorio
    root = tk.Tk()
    app = CatalogUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 