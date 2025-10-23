import bcrypt
from flask import jsonify, request
from src.routes import api
from src.util.avatar import get_avatar
from src.util.logger import logger
from src.util.validator import Validator
from src.lib.roles import Roles
from src.lib.database import mysql
from src.middleware.auth import only_guest

@api.route('/auth/signup', methods=['POST'])
@only_guest()
def signup():
    
    # Campos del formulario
    data = request.form
    
    username = data.get('username', "")
    password = data.get('password', "")
    password_confirmation = data.get('password_confirmation', "")
    email = data.get('email', "")
    
    # Validar los datos
    validator = Validator()
    validator.is_valid_username(username)
    validator.is_valid_email(email)
    validator.is_strong_password(password)
    validator.passwords_match(password, password_confirmation)
    
    # Chequear que los datos no existan
    validator.username_exists(username)
    validator.email_exists(email)
    
    if validator.get_errors() != {}:
        errors = validator.get_errors()
        print(errors)
        return jsonify(error=errors), 400
    
    # Hashear la contraseña con <<bcrypt>>
    password = password.encode('utf-8')
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    
    # Insertar usuario en la base de datos y asignarle el rol usuario en USUARIO_ROL
    query = """
    INSERT INTO `USUARIO`
    (`Username`, `Password`, `Correo`, `Avatar_URL`, `FechaRegistro`) 
    VALUES (%s, %s, %s, %s, NOW())
    """
    
    with mysql.get_db().cursor() as cursor:
        cursor.execute(query, (username, password, email, get_avatar(username)))
        user_id = cursor.lastrowid  # este es el Usuario_ID recién generado
        mysql.get_db().commit() # Commit para crear el usuario
    
        # Insertar rol
        query_role = "INSERT INTO `USUARIO_ROL` (`Usuario_ID`, `Rol_ID`) VALUES (%s, %s)"
        cursor.execute(query_role, (user_id, Roles.Usuario.value))
        mysql.get_db().commit() # Commit para asignarle el rol por defecto
    
    logger.info(f"El usuario {username} se ha registrado.")
    return {"success": "El usuario se ha registrado correctamente."}, 201