from flask import request, jsonify
from src.routes import api
from src.util.validator import Validator
from src.lib.database import mysql, get_user_id

# Middleware
from src.middleware.auth import auth_required

@api.route('/users/stats', methods=['GET'])
@auth_required(level=1) # Requiere permisos de usuario logueado
def get_stats(username):
    # Validar existencia del usuario
    validator = Validator()
    if not validator.username_exists(username):
        return {"error": "El nombre de usuario no existe"}, 404
    
    user_id = get_user_id(username)
    
    # Traer las partidas que gano desde la base de datos
    query = """
    SELECT 
        (SELECT COUNT(*) FROM `PARTIDA` WHERE `Ganador_ID` = %s) AS wins,
        (SELECT COUNT(*) FROM `PARTIDA_PARTICIPANTE` WHERE `Usuario_ID` = %s) AS total_games
    """
    
    userstats = {
        "wins": 0,
        "winrate": 0
    }
    
    # Enviar la información al perfil luego de ejecutar la consulta
    with mysql.get_db().cursor() as cursor:
        cursor.execute(query, (user_id, user_id))
        result = cursor.fetchall()
        userstats["wins"] = result[0][0]
        userstats["winrate"] = (result[0][0] / (result[0][1] if result[0][1] != 0 else 1) * 100)
    
    return jsonify(userstats)