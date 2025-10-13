from flask import request, jsonify
from src.routes import api
from src.util.validator import Validator
from src.database import mysql

# JWT
from flask_jwt_extended import create_access_token

# Middleware
from src.middleware.auth import only_guest

@api.route('/auth/login', methods=['POST'])
@only_guest()
def login():
    # Campos del formulario
    data = request.form

    username = data.get('username')
    password = data.get('password')

    # Validar existencia del usuario
    validator = Validator()
    if not validator.username_exists(username):
        return {"error": "El nombre de usuario no existe"}, 404
    
    # Traer la contraseña hasheada desde la base de datos
    with mysql.get_db().cursor() as cursor:
        cursor.execute("SELECT `Password` FROM `USUARIO` WHERE `Username` = %s", username)
        hashed_password = cursor.fetchone()[0]
    
    # Validar la contraseña
    if not validator.correct_password(password, hashed_password):
        return {"error": "La contraseña es incorrecta"}, 401
    
    # Crear la sesión para el usuario
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)
