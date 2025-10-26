from flask import request, make_response
from src.routes import game
from src.middleware.auth import auth_required
from src.lib.room_config import Gamemodes, Difficulty
from src.lib.rooms import Rooms
from src.lib.database import mysql

@game.route('/create-room', methods=['POST'])
@auth_required(level=1)
def create_room(username):
    data = request.form
    
    # Obtener datos del formulario
    room_owner = username
    
    try:
        room_lives = int(data.get('lives', 3))
        room_maxplayers = int(data.get('max_players', 4))    
        room_gamemode = int(data.get('game_mode', Gamemodes.CLASSIC.value))
        room_difficulty = int(data.get('difficulty', Difficulty.NORMAL.value))
    except ValueError:
        return {"error": "Los parámetros deben ser enteros"}, 400
    
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
    
    # Si el usuario ya está en una sala, removerlo primero
    if rooms.is_in_any_room(username):
        current_room = rooms.get_player_room(username)
        if current_room:
            # Obtener el código de la sala actual
            current_room_code = None
            for code, room_data in rooms.get_all_rooms().items():
                if room_data == current_room:
                    current_room_code = code
                    break
            
            if current_room_code:
                # Remover al jugador de la sala actual
                current_room['players'] = [p for p in current_room['players'] if p['username'] != username]
    
    room = rooms.add_room(
        room_owner, 
        room_gamemode, 
        room_difficulty, 
        room_lives, 
        room_maxplayers
    )
    
    # Obtener el avatar del creador
    avatar = None
    try:
        with mysql.get_db().cursor() as cursor:
            query = "SELECT Avatar_URL FROM USUARIO WHERE Username = %s"
            cursor.execute(query, (room_owner,))
            result = cursor.fetchone()
            if result and result[0]:
                avatar = result[0]
    except Exception as e:
        print(f"Error obteniendo avatar: {e}")
    
    # Meter al creador a la sala
    rooms.join_player(room, room_owner, avatar)
      
    response = make_response({"success": f"Sala creada exitosamente.", "room_code": room}, 201)
    response.set_cookie("ROOM", room)
    print(rooms.get_room_by_code(room))
    return response