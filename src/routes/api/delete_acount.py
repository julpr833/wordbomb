import bcrypt
from flask import request
from src.routes import api
from src.util.logger import logger
from src.util.validator import Validator
from src.lib.database import mysql
from src.middleware.auth import auth_required

@api.route('/users/delete-account', methods=['DELETE'])
@auth_required(level=1)
def delete_account(username):
    
    # Campos del formulario
    data = request.form
    
    # Como método de verificación para eliminar la cuenta pedimos la contraseña
    password = data.get('password', "")
    
    # Instanciar validador
    validator = Validator()
    
    # Traer la contraseña hasheada desde la base de datos
    with mysql.get_db().cursor() as cursor:
        cursor.execute("SELECT `Password` FROM `USUARIO` WHERE `Username` = %s", username)
        hashed_password = cursor.fetchone()[0]
    
    # Validar la contraseña
    if not validator.correct_password(password, hashed_password):
        return {"error": "La contraseña es incorrecta"}, 401

    # Eliminar la cuenta
    with mysql.get_db().cursor() as cursor:
        cursor.execute("DELETE FROM `USUARIO` WHERE `Username` = %s", username)
        mysql.get_db().commit()
    
    return {"status": "success"}, 200