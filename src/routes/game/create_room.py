from flask import request
from src.routes import game
from src.middleware.auth import auth_required
from src.lib.room_config import Gamemodes, Difficulty
from src.lib.rooms import Rooms

@game.route('/', methods=['POST'])
@auth_required(level=1)
def create_room(username):
    data = request.form
    
    room_owner = username
    room_lives = data.get('lives', 3)
    room_maxplayers = data.get('max_players', 4)
    room_gamemode = data.get('game_mode', Gamemodes.CLASSIC.value)
    room_difficulty = data.get('difficulty', Difficulty.NORMAL.value)
        
    return {"success": f"Sala creada exitosamente."}, 201
