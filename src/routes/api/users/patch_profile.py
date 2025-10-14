import bcrypt
from flask import request
from src.routes import api
from src.util.logger import logger
from src.util.validator import Validator
from src.util.rand_str import generate_random_string
from src.lib.database import mysql
from src.middleware.auth import auth_required
from src.util.avatar import get_avatar

@api.route('/users/profile', methods=['PATCH'])
@auth_required(level=1)
def patch_profile(username):
    
    # Campos del formulario
    data = request.form
    
    new_username = data.get('new_username', "")
    regen_avatar = data.get('regen_avatar', False)
    new_password = data.get('new_password', "")
    new_pass_confirm = data.get('new_pass_confirm', "")
    
    if regen_avatar:
        regen_avatar = True
    
    # Validar los datos
    validator = Validator()
    
    # Concatenar las actualizaciones del perfil
    updates = {}
    with mysql.get_db().cursor() as cursor:
        # Si actualiza nombre de usuario
        if new_username and validator.is_valid_username(new_username) and not validator.username_exists(new_username):
            updates["Username"] = new_username

        # Si actualiza contraseña
        if new_password and validator.is_strong_password(new_password) and validator.passwords_match(new_password, new_pass_confirm):
            password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            updates["Password"] = password

        # Si actualiza avatar
        if regen_avatar:
            rand_avatar_seed = generate_random_string(10)
            updates["Avatar_URL"] = get_avatar(rand_avatar_seed)

        # Si hay actualizaciones válidas
        if updates:
            fields = ", ".join(f"`{key}` = %s" for key in updates.keys())
            cursor.execute(f"UPDATE `USUARIO` SET {fields} WHERE `Username` = %s", (*updates.values(), username))
            mysql.get_db().commit()

    # Si hay errores devolver errores
    if validator.get_errors() != {}:
        errors = validator.get_errors()
        return errors, 400
    
    return {"status": "success"}, 200