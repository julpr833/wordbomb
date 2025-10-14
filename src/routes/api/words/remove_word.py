from flask import request
from src.routes import api
from src.middleware.auth import auth_required
from src.util.validator import Validator
from src.lib.database import mysql

@api.route('/words/remove-word', methods=['DELETE'])
@auth_required(level=2)
def remove_word(username):
    data = request.form
    
    word_id = data.get('word_id', None)
    
    # La funcion word_exists_id valida que la palabra exista
    # En caso de que exista, la devuelve, de lo contrario devuelve False
    validator = Validator()
    word = validator.word_exists_id(word_id)
    
    # En caso de que no exista, como va a ser False simplemente retornamos error
    # El chequeo de word_id is None es un poco de overengineering pero bueno...
    if word_id is None or word is False:
        return {"error": "Palabra no encontrada"}, 404
    
    # Eliminamos la palabra
    with mysql.get_db().cursor() as cursor:
        cursor.execute("DELETE FROM `PALABRA` WHERE `ID_Palabra` = %s", (word_id))
        mysql.get_db().commit()
        
    return {"success": f"Palabra {word} eliminada correctamente."}, 201