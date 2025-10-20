from flask import request
from src.routes import api
from src.middleware.auth import auth_required
from src.util.audit_actions import AuditActions
from src.lib.database import mysql, get_user_id
from src.lib.words import Words

@api.route('/words/remove-word', methods=['DELETE'])
@auth_required(level=2)
def remove_word(username):
    data = request.form
    
    word_id = data.get('word_id', None)
    
    # Asegurar que word_id sea un entero
    try:
        int(word_id)
    except ValueError:
        return {"error": "word_id debe ser un entero"}, 400
    
    # La funcion word_exists_id valida que la palabra exista
    # En caso de que exista, la devuelve, de lo contrario devuelve False
    word = Words().get_word_by_id(int(word_id))
    
    # En caso de que no exista, como va a ser False simplemente retornamos error
    # El chequeo de word_id is None es un poco de overengineering pero bueno...
    if word_id is None or word is False:
        return {"error": "Palabra no encontrada"}, 404
    
    # Eliminamos la palabra
    with mysql.get_db().cursor() as cursor:
        words = Words()
        words.remove_word(word)
        user_id = get_user_id(username)
        cursor.execute("INSERT INTO `REGISTRO_AUDITORIA` (`Administrador_ID`, `Accion_ID`, `FechaRegistro`) VALUES (%s, %s, NOW())", (user_id, AuditActions.REMOVE_WORD.value))
        mysql.get_db().commit()
        
    return {"success": f"Palabra {word} eliminada correctamente."}, 201