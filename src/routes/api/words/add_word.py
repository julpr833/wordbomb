from flask import request
from src.routes import api
from src.middleware.auth import auth_required
from src.util.validator import Validator
from src.lib.database import mysql, get_user_id
from src.util.audit_actions import AuditActions

@api.route('/words/add-word', methods=['POST'])
@auth_required(level=2)
def add_word(username):
    data = request.form
    
    # Traigo la palabra del formulario
    word = data.get('word', "")
    
    validator = Validator()
    
    # Validaciones, no debe tener espacios, ser solo letras y tener al menos 2 letras
    if not validator.is_valid_word(word):
        return validator.get_errors(), 400  
    
    if validator.word_exists(word):
        return {"error": "La palabra ya existe"}, 400
    
    # Inserto la palabra    
    with mysql.get_db().cursor() as cursor:
        cursor.execute("INSERT INTO `PALABRA` (`Palabra`) VALUES (%s)", (word))
        # Audito la acción
        user_id = get_user_id(username)
        cursor.execute("INSERT INTO `REGISTRO_AUDITORIA` (`Administrador_ID`, `Accion_ID`, `FechaRegistro`) VALUES (%s, %s, NOW())", (user_id, AuditActions.ADD_WORD.value))
        mysql.get_db().commit()
        
    return {"success": f"Palabra {word} añadida correctamente."}, 201