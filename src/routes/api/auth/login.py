from flask import request, jsonify
from src.routes import api
from src.util.validator import Validator
from src.lib.database import mysql

# JWT
from flask_jwt_extended import create_access_token

# Middleware
from src.middleware.auth import only_guest

@api.route('/auth/login', methods=['POST'])
@only_guest()
def login():
    # Campos del formulario
    data = request.form

    username = data.get('username', "")
    password = data.get('password', "")

    # Validar existencia del usuario
    validator = Validator()
    if not validator.username_exists(username):
        return {"error": "El nombre de usuario no existe"}, 400
    
    # Traer la contraseña hasheada desde la base de datos
    with mysql.get_db().cursor() as cursor:
        cursor.execute("SELECT `Password` FROM `USUARIO` WHERE `Username` = %s", username)
        hashed_password = cursor.fetchone()[0]
    
    # Validar la contraseña
    if not validator.correct_password(password, hashed_password):
        return {"error": "La contraseña es incorrecta"}, 401
    
    # Traer el perfil del usuario de la base de datos para devolverlo
    with mysql.get_db().cursor() as cursor:
        query = """
        SELECT `Username`, `Correo`, `Avatar_URL`, `FechaRegistro`, `Vetado`
        FROM `USUARIO` 
        WHERE `Username` = %s
        """
        cursor.execute(query, username)
        userinfo = cursor.fetchone()
        userinfo = {
            "username": userinfo[0],
            "email": userinfo[1],
            "avatar": userinfo[2],
            "registration_date": userinfo[3],
            "banned": userinfo[4]
        }
    
    # Crear la sesión para el usuario
    access_token = create_access_token(identity=username)
    return jsonify(user=userinfo, token=access_token)
