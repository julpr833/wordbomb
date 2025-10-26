from flask import request, make_response
from src.routes import game
from src.middleware.auth import auth_required
from src.lib.rooms import Rooms 
from src.lib.room_config import RoomStatus
from src.lib.database import mysql

# Inicializamos la instancia Singleton de Rooms
rooms_manager = Rooms() 

@game.route('/join-room', methods=['POST'])
@auth_required(level=1)
def join_room_http(username):
    data = request.form
    room_code = data.get('room_code')
    
    if not room_code:
        return {"error": "Se requiere el código de la sala."}, 400

    room_data = rooms_manager.get_room_by_code(room_code)
    
    if not room_data:
        return {"error": "Sala no encontrada o no existe."}, 404
    
    # Verificar si el usuario ya está en otra sala diferente
    if rooms_manager.is_in_any_room(username):
        current_room = rooms_manager.get_player_room(username)
        # Comparar por identidad de objeto (misma referencia en memoria)
        if current_room is not room_data:
            return {"error": "Ya te encuentras en una sala."}, 400
            
    if len(room_data['players']) >= room_data['max_players']:
        print("La sala esta llena.")
        return {"error": "La sala está llena."}, 400
    
    if room_data['state'] == RoomStatus.PLAYING.value:
        return {"error": "El juego en esta sala ya ha comenzado."}, 400
    
    # Obtener el avatar del usuario
    avatar = None
    try:
        with mysql.get_db().cursor() as cursor:
            query = "SELECT Avatar_URL FROM USUARIO WHERE Username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result and result[0]:
                avatar = result[0]
    except Exception as e:
        print(f"Error obteniendo avatar: {e}")
    
    # Buscamos si el jugador ya está en la lista de jugadores (para reconexiones)
    player_exists = any(player["username"] == username for player in room_data['players'])
    
    if player_exists:
        # El jugador ya está en la sala (puede ser una reconexión)
        message = f"Ya conectado a la sala {room_code}."
        status_code = 200
    else:
        success = rooms_manager.join_player(room_code, username, avatar)
        
        if not success:
             # Esto debería ser redundante por las validaciones anteriores, pero es una buena práctica
             return {"error": "No fue posible unirte a la sala (posiblemente llena)."}, 500

        message = f"Unido a la sala {room_code} exitosamente."
        status_code = 200
    
    updated_room_data = rooms_manager.get_room_by_code(room_code)
    
    response = make_response({
        "success": True, 
        "message": message,
        "data": {"room": updated_room_data}
    }, status_code)

    response.set_cookie("ROOM", room_code)
    
    print(updated_room_data)
    return response