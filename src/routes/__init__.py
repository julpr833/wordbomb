import importlib
import pathlib
from flask import Blueprint
from src.util.logger import logger

api = Blueprint('api', __name__)
game = Blueprint('game', __name__)

def load_all_routes():
    # ./routes
    base_path = pathlib.Path(__file__).parent
    
    # Todos los terminados en .py en ./routes y sus subcarpetas
    for py_file in base_path.rglob("*.py"):
        # Ignorar este archivo
        if py_file.name == "__init__.py":
            continue
        
        # Crear nombre del modulo, a routes el concateno <x> con un "." como separador.
        module_name = ".".join(py_file.relative_to(base_path.parent).with_suffix("").parts)

        logger.success(f"Cargando ruta: {module_name}")

        # Especificar a Python el nombre del módulo y dónde cargarlo
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        
        # Crea un módulo vacio con ese nombre en memoria
        module = importlib.util.module_from_spec(spec)
        
        # Rellena la memoria con el código del archivo para ejecutarlo
        spec.loader.exec_module(module)