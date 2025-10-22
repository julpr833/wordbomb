from flask import request, make_response
from src.routes import game
from src.middleware.auth import auth_required
from src.lib.room_config import Gamemodes, Difficulty
from src.lib.rooms import Rooms

@game.route('/create-room', methods=['POST'])
@auth_required(level=1)
def create_room(username):
    data = request.form
    
    # Obtener datos del formulario
    room_owner = username
    
    try:
        room_lives = int(data.get('lives', 3))
        room_maxplayers = int(data.get('max_players', 4))
    except ValueError:
        return {"error": "Los campos lives y max_players deben ser enteros"}, 400
    
    room_gamemode = data.get('game_mode', Gamemodes.CLASSIC.value)
    room_difficulty = data.get('difficulty', Difficulty.NORMAL.value)
    
    # Validaciones básicas
    if room_lives < 1 or room_lives > 10:
        return {"error": "Las vidas deben estar entre 1 y 10"}, 400
        
    if room_maxplayers < 2 or room_maxplayers > 10:
        return {"error": "Los jugadores deben estar entre 2 y 10"}, 400

    # Validar que gamemode y difficulty sean válidos
    valid_gamemodes = [gm.value for gm in Gamemodes]
    valid_difficulties = [diff.value for diff in Difficulty]
    
    if room_gamemode not in valid_gamemodes:
        return {"error": "Modo de juego inválido"}, 400
        
    if room_difficulty not in valid_difficulties:
        return {"error": "Dificultad inválida"}, 400

    rooms = Rooms()
    room = rooms.add_room(
        room_owner, 
        room_gamemode, 
        room_difficulty, 
        room_lives, 
        room_maxplayers
    )
      
    response = make_response({"success": f"Sala creada exitosamente.", "room_code": room}, 201)
    response.set_cookie("ROOM", room)
    return response