from flask import Flask

# Variables de entorno
from dotenv import load_dotenv
from os import getenv

# Base de datos
from src.database import mysql

# Enrutador
import src.routes as router

# JWT
from flask_jwt_extended import JWTManager

load_dotenv()

def create_app():
    app = Flask(__name__)
    jwt = JWTManager(app)
    router.load_all_routes()

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
    mysql.init_app(app)

    return app