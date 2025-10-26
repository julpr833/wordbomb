from flask import Flask

# Variables de entorno
from dotenv import load_dotenv
from os import getenv

# Base de datos
from src.lib.database import mysql
import pymysql.cursors

# Enrutador
import src.routes as router

# JWT
from flask_jwt_extended import JWTManager
import src.lib.jwt_config as jwt_config

# Juego
from src.lib.rooms import Rooms
from src.lib.words import Words

# SocketIO
from flask_socketio import SocketIO
socketio = SocketIO()

# CORS
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Cargar todas las rutas
    router.load_all_routes()

    # Modularizar rutas
    app.register_blueprint(router.api, url_prefix="/api")
    app.register_blueprint(router.game, url_prefix="/game")
    
    
    SESSION_SECRET = getenv("SESSION_SECRET")

    # Configuración de la clave de sesión
    if SESSION_SECRET is None:
        raise Exception("SESSION_SECRET is not set in the .env file.")
    
    # Clave de sesión
    app.config['JWT_SECRET_KEY'] = SESSION_SECRET
    
    # Configuración de la base de datos
    app.config['MYSQL_DATABASE_HOST'] = getenv("MYSQL_HOST")
    app.config['MYSQL_DATABASE_USER'] =  getenv("MYSQL_USER")
    app.config['MYSQL_DATABASE_PASSWORD'] = getenv("MYSQL_PASSWORD")
    app.config['MYSQL_DATABASE_DB'] = getenv("MYSQL_DB")
    app.config['MYSQL_DATABASE_CURSORCLASS'] = pymysql.cursors.DictCursor  # Devolver diccionarios
    
    # Iniciar base de datos
    mysql.init_app(app)
    
    # Inicializar JWT
    jwt = JWTManager(app)
    jwt_config.register_jwt_handlers(jwt)
    
    # Iniciar WS
    socketio.init_app(app, cors_allowed_origins=getenv("FRONTEND_URL"))
    
    # Inicializar eventos de SocketIO
    from src.events import init_socketio_events
    init_socketio_events()
    
    # CORS
    CORS(app, 
        resources=
        {r"/*": 
            {
                "origins": getenv("FRONTEND_URL"),
                "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
                "allowed_headers": ["Content-Type", "Authorization"],
            }
        })
    
    # Inicializar juego
    # ajajaj a ver esto es muy terrorista pero no queria refactorizar todo :v
    with app.test_request_context():
        Rooms() # Iniciar Singleton
        Words() # Iniciar Singleton
    
    # Guardar referencia a la app DESPUÉS de inicializar
    rooms = Rooms()
    rooms.set_app(app)

    return app