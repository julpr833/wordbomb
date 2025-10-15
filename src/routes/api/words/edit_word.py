from flask import request
from src.routes import api
from src.middleware.auth import auth_required
from src.util.audit_actions import AuditActions
from src.util.validator import Validator
from src.lib.database import mysql, get_user_id

@api.route('/words/edit-word', methods=['PATCH'])
@auth_required(level=2)
def edit_word(username):
    data = request.form
    
    word_id = data.get('word_id', None)
    new_word = data.get('new_word', None)
    
    # La funcion word_exists_id valida que la palabra exista
    # En caso de que exista, la devuelve, de lo contrario devuelve False
    validator = Validator()
    word = validator.word_exists_id(word_id)
    
    # Validamos la nueva palabra
    if not validator.is_valid_word(new_word):
        return validator.get_errors(), 400
    
    # En caso de que no exista, como va a ser False simplemente retornamos error
    # El chequeo de word_id is None es un poco de overengineering pero bueno...
    if word_id is None or word is False:
        return {"error": "Palabra no encontrada"}, 404
    
    # Eliminamos la palabra
    with mysql.get_db().cursor() as cursor:
        cursor.execute("UPDATE `PALABRA` SET `Palabra` = %s WHERE `ID_Palabra` = %s", (new_word, word_id))
        user_id = get_user_id(username)
        cursor.execute("INSERT INTO `REGISTRO_AUDITORIA` (`Administrador_ID`, `Accion_ID`, `FechaRegistro`) VALUES (%s, %s, NOW())", (user_id, AuditActions.EDIT_WORD.value))
        mysql.get_db().commit()
        
    return {"success": f"La palabra {word} fue actualizada."}, 201