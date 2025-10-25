from flask import request, make_response
from src.routes import game
from src.middleware.auth import auth_required
from src.lib.rooms import Rooms 
from src.lib.room_config import RoomStatus

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
            
    if len(room_data['players']) >= room_data['max_players']:
        return {"error": "La sala está llena."}, 400
    
    if room_data['state'] == RoomStatus.PLAYING.value:
         return {"error": "El juego en esta sala ya ha comenzado."}, 400
    
    # Buscamos si el jugador ya está en la lista de jugadores (para reconexiones)
    player_exists = any(player["username"] == username for player in room_data['players'])
    
    if player_exists:
        # El jugador ya está en la sala (puede ser una reconexión)
        message = f"Ya conectado a la sala {room_code}."
        status_code = 200
    else:
        success = rooms_manager.join_player(room_code, username)
        
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
    return response