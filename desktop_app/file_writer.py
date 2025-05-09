import os

def crear_archivo_proceso(pid: int, nombre: str, descripcion: str) -> str:
    """
    Crea o trunca un archivo para el proceso y escribe su descripción.
    
    Args:
        pid: ID del proceso
        nombre: Nombre del proceso
        descripcion: Descripción a escribir
        
    Returns:
        str: Ruta del archivo creado
    """
    # Crear directorio si no existe
    os.makedirs("catalogo", exist_ok=True)
    
    # Crear archivo
    archivo = f"catalogo/proceso_{pid}_{nombre}.txt"
    with open(archivo, "w") as f:
        f.write(descripcion)
        
    return archivo
        
def escribir_caracter(archivo: str, caracter: str):
    """Escribe un carácter en el archivo del proceso"""
    with open(archivo, 'a', encoding='utf-8') as f:
        f.write(caracter) 