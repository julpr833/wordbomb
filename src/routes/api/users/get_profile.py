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
    SELECT `ID_Usuario`, `Username`, `Correo`, `Avatar_URL`, `FechaRegistro`, `Vetado`, `Rol_ID`
    FROM `USUARIO` 
    LEFT JOIN `USUARIO_ROL` ON `USUARIO`.`ID_Usuario` = `USUARIO_ROL`.`Usuario_ID`
    WHERE `Username` = %s
    """
    
    # Enviar la información al perfil luego de ejecutar la consulta
    with mysql.get_db().cursor() as cursor:
        cursor.execute(query, username)
        userinfo = cursor.fetchone()
        userinfo = {
            "id": userinfo[0],
            "username": userinfo[1],
            "email": userinfo[2],
            "avatar_url": userinfo[3],
            "registration_date": userinfo[4],
            "banned": userinfo[5],
            "role": userinfo[6]
        }
    
    return jsonify(userinfo)