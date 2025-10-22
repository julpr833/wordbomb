from flask import request, jsonify
from src.routes import api
from src.util.validator import Validator
from src.lib.database import mysql

# Middleware
from src.middleware.auth import auth_required

@api.route('/users/profile', methods=['GET'])
@auth_required(level=1) # Requiere permisos de usuario logueado
def get_profile(username):
    # Validar existencia del usuario
    validator = Validator()
    if not validator.username_exists(username):
        return {"error": "El nombre de usuario no existe"}, 404
    
    # Traer el perfil desde la base de datos
    query = """
    SELECT `Username`, `Correo`, `Avatar_URL`, `FechaRegistro`, `Vetado`
    FROM `USUARIO` 
    WHERE `Username` = %s
    """
    
    # Enviar la información al perfil luego de ejecutar la consulta
    with mysql.get_db().cursor() as cursor:
        cursor.execute(query, username)
        userinfo = cursor.fetchone()
        userinfo = {
            "username": userinfo[0],
            "email": userinfo[1],
            "avatar_url": userinfo[2],
            "registration_date": userinfo[3],
            "banned": userinfo[4]
        }
    
    return jsonify(userinfo)