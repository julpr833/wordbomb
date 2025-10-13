from flask import request, jsonify
from src.routes import api
from src.util.validator import Validator
from src.lib.database import mysql

# Middleware
from src.middleware.auth import auth_required

@api.route('/users/profile', methods=['GET'])
@auth_required(level=1) # Requiere permisos de usuario logueado
def get_profile(username):
    # Campos del formulario
    user_to_get = request.args.get('username', '')

    # Asegurar que solo puede acceder a su perfil
    if user_to_get != username:
        return {"error": "No tienes permiso para acceder a este perfil"}, 403

    # Validar existencia del usuario
    validator = Validator()
    if not validator.username_exists(username):
        return {"error": "El nombre de usuario no existe"}, 404
    
    # Traer el perfil desde la base de datos
    query = """
    SELECT `Username`, `Correo`, `Avatar_URL`, `FechaRegistro`, `PuntosTotales`, `Vetado`
    FROM `USUARIO` 
    WHERE `Username` = %s
    """
    
    # Enviar la información al perfil luego de ejecutar la consulta
    with mysql.get_db().cursor() as cursor:
        cursor.execute(query, user_to_get)
        userinfo = cursor.fetchone()
        userinfo = {
            "username": userinfo[0],
            "email": userinfo[1],
            "avatar_url": userinfo[2],
            "registration_date": userinfo[3],
            "total_points": userinfo[4],
            "banned": userinfo[5]
        }
    
    return jsonify(userinfo)