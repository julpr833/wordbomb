from flask import request
from src.routes import api
from src.middleware.auth import auth_required
from src.util.validator import Validator
from src.lib.database import mysql

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
    
    # Inserto la palabra    
    with mysql.get_db().cursor() as cursor:
        cursor.execute("INSERT INTO `PALABRA` (`Palabra`) VALUES (%s)", (word))
        mysql.get_db().commit()
        
    return {"success": f"Palabra {word} añadida correctamente."}, 201