from flask import Flask
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    from src.routes.api_routes import api
    from src.routes.game_routes import game

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(game, url_prefix="/game")
    
    SESSION_SECRET = getenv("SESSION_SECRET")

    # Configuración de la clave de sesión
    if SESSION_SECRET is None:
        raise Exception("SESSION_SECRET is not set in the .env file.")
    app.config["SECRET_KEY"] = SESSION_SECRET

    return app