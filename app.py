from flask import Flask
from dotenv import load_dotenv
from os import getenv
from database import init_database

app = Flask(__name__)

# Cargar variables de entorno
load_dotenv()

SESSION_SECRET = getenv("SESSION_SECRET")


if SESSION_SECRET is None:
    raise Exception("SESSION_SECRET is not set in the .env file.")
    
app.config["SECRET_KEY"] = SESSION_SECRET

# Iniciar base de datos
DATABASE = init_database()

# Importar rutas
import api