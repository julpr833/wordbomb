from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
from src import socketio
from src.lib.rooms import Rooms
from src.lib.game_logic import GameLogic
from src.lib.room_config import RoomStatus
import time
import threading

# Instancias globales
rooms_manager = Rooms()
game_logic = None  # Se inicializará en el primer uso

# Diccionario para almacenar timers de turnos
turn_timers = {}

# Diccionario para almacenar el estado del juego de cada sala
game_states = {}

def get_game_logic():
    """Obtiene la instancia de GameLogic, inicializándola si es necesario"""
    global game_logic
    if game_logic is None:
        game_logic = GameLogic()
    return game_logic

def init_game_state(room_code: str, room_data: dict):
    """Inicializa el estado del juego para una sala"""
    players = room_data['players']
    
    game_states[room_code] = {
        'current_player_index': 0,
        'alive_players': list(range(len(players))),  # Índices de jugadores vivos
        'player_lives': {i: room_data['lives'] for i in range(len(players))},
        'used_words': [],
        'current_prompt': None,
        'turn_start_time': None,
        'round_number': 1
    }

def get_turn_time_limit(difficulty: int) -> int:
    """Retorna el tiempo límite en segundos según la dificultad"""
    time_limits = {
        1: 15,  # EASY: 15 segundos
        2: 12,  # NORMAL: 12 segundos
        3: 10   # HARD: 10 segundos
    }
    return time_limits.get(difficulty, 12)

def cancel_turn_timer(room_code: str):
    """Cancela el timer del turno actual"""
    if room_code in turn_timers:
        timer = turn_timers[room_code]
        if timer and timer.is_alive():
            timer.cancel()
        del turn_timers[room_code]

def start_turn_timer(room_code: str, time_limit: int):
    """Inicia un timer para el turno actual"""
    cancel_turn_timer(room_code)
    
    def on_timeout():
        handle_turn_timeout(room_code)
    
    timer = threading.Timer(time_limit, on_timeout)
    timer.daemon = True
    turn_timers[room_code] = timer
    timer.start()

def handle_turn_timeout(room_code: str):
    """Maneja cuando se acaba el tiempo de un turno"""
    room_data = rooms_manager.get_room_by_code(room_code)
    if not room_data or room_code not in game_states:
        return
    
    game_state = game_states[room_code]
    current_idx = game_state['current_player_index']
    
    # El jugador pierde una vida
    game_state['player_lives'][current_idx] -= 1
    
    current_player = room_data['players'][current_idx]
    
    socketio.emit('player_timeout', {
        'username': current_player['username'],
        'lives_remaining': game_state['player_lives'][current_idx]
    }, room=room_code)
    
    # Verificar si el jugador fue eliminado
    if game_state['player_lives'][current_idx] <= 0:
        game_state['alive_players'].remove(current_idx)
        
        socketio.emit('player_eliminated', {
            'username': current_player['username'],
            'remaining_players': len(game_state['alive_players'])
        }, room=room_code)
        
        # Verificar si hay un ganador
        if len(game_state['alive_players']) <= 1:
            end_game(room_code)
            return
    
    # Pasar al siguiente turno
    next_turn(room_code)

def next_turn(room_code: str):
    """Avanza al siguiente turno"""
    room_data = rooms_manager.get_room_by_code(room_code)
    if not room_data or room_code not in game_states:
        return
    
    game_state = game_states[room_code]
    
    # Obtener siguiente jugador vivo
    current_idx = game_state['current_player_index']
    next_idx = get_game_logic().get_next_player_index(
        current_idx, 
        len(room_data['players']), 
        game_state['alive_players']
    )
    
    game_state['current_player_index'] = next_idx
    game_state['round_number'] += 1
    
    # Generar nuevo prompt
    prompt = get_game_logic().generate_prompt(
        room_data['gamemode'],
        room_data['difficulty']
    )
    game_state['current_prompt'] = prompt
    game_state['turn_start_time'] = time.time()
    
    # Incrementar turno en la sala
    rooms_manager.next_turn(room_code)
    
    next_player = room_data['players'][next_idx]
    time_limit = get_turn_time_limit(room_data['difficulty'])
    
    # Iniciar timer del turno
    start_turn_timer(room_code, time_limit)
    
    # Emitir evento de nuevo turno
    socketio.emit('new_turn', {
        'player': next_player['username'],
        'player_index': next_idx,
        'prompt': prompt,
        'time_limit': time_limit,
        'round': game_state['round_number'],
        'lives': {room_data['players'][i]['username']: game_state['player_lives'][i] 
                  for i in range(len(room_data['players']))}
    }, room=room_code)

def end_game(room_code: str):
    """Finaliza el juego y determina el ganador"""
    room_data = rooms_manager.get_room_by_code(room_code)
    if not room_data or room_code not in game_states:
        return
    
    cancel_turn_timer(room_code)
    game_state = game_states[room_code]
    
    # Determinar ganador
    if len(game_state['alive_players']) == 1:
        winner_idx = game_state['alive_players'][0]
        winner = room_data['players'][winner_idx]
    else:
        # Si no hay jugadores vivos, el ganador es quien tiene más puntos
        winner = max(room_data['players'], key=lambda p: p['points'])
    
    # Guardar ganador en la sala
    rooms_manager.set_winner(room_code, winner['username'])
    
    # Emitir evento de fin de juego
    socketio.emit('game_ended', {
        'winner': winner['username'],
        'final_scores': [
            {
                'username': p['username'],
                'points': p['points'],
                'lives': game_state['player_lives'][i]
            }
            for i, p in enumerate(room_data['players'])
        ],
        'total_rounds': game_state['round_number'],
        'total_words': len(game_state['used_words'])
    }, room=room_code)
    
    # Guardar partida en base de datos
    try:
        rooms_manager.end_game(room_code)
    except Exception as e:
        print(f"Error guardando partida: {e}")
    
    # Limpiar estado del juego
    if room_code in game_states:
        del game_states[room_code]

@socketio.on('connect')
def handle_connect():
    """Maneja la conexión de un cliente"""
    print(f"Cliente conectado: {request.sid}")
    emit('connected', {'message': 'Conectado al servidor'})

@socketio.on('disconnect')
def handle_disconnect():
    """Maneja la desconexión de un cliente"""
    print(f"Cliente desconectado: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    """Maneja cuando un jugador se une a una sala"""
    room_code = data.get('room_code')
    username = data.get('username')
    
    if not room_code or not username:
        emit('error', {'message': 'Faltan datos requeridos'})
        return
    
    room_data = rooms_manager.get_room_by_code(room_code)
    
    if not room_data:
        emit('error', {'message': 'Sala no encontrada'})
        return
    
    # Unir al jugador a la sala de Socket.IO
    join_room(room_code)
    
    # Emitir a todos en la sala que un jugador se unió
    emit('player_joined', {
        'username': username,
        'players': room_data['players'],
        'room_info': {
            'code': room_code,
            'gamemode': room_data['gamemode'],
            'difficulty': room_data['difficulty'],
            'lives': room_data['lives'],
            'max_players': room_data['max_players'],
            'state': room_data['state']
        }
    }, room=room_code)
    
    print(f"{username} se unió a la sala {room_code}")

@socketio.on('leave_room')
def handle_leave_room(data):
    """Maneja cuando un jugador sale de una sala"""
    room_code = data.get('room_code')
    username = data.get('username')
    
    if not room_code or not username:
        return
    
    room_data = rooms_manager.get_room_by_code(room_code)
    
    if room_data:
        # Eliminar al jugador de la lista de jugadores
        room_data['players'] = [p for p in room_data['players'] if p['username'] != username]
        
        # Si el juego está en curso, manejar la eliminación
        if room_data['state'] == RoomStatus.PLAYING.value and room_code in game_states:
            game_state = game_states[room_code]
            
            # Encontrar índice del jugador
            player_idx = None
            for i, player in enumerate(room_data['players']):
                if player['username'] == username:
                    player_idx = i
                    break
            
            if player_idx is not None and player_idx in game_state['alive_players']:
                game_state['alive_players'].remove(player_idx)
                game_state['player_lives'][player_idx] = 0
                
                # Verificar si hay un ganador
                if len(game_state['alive_players']) <= 1:
                    end_game(room_code)
                elif player_idx == game_state['current_player_index']:
                    # Si era el turno del jugador que salió, pasar al siguiente
                    cancel_turn_timer(room_code)
                    next_turn(room_code)
        
        # Si la sala queda vacía, eliminarla
        if len(room_data['players']) == 0:
            rooms_manager.rooms.pop(room_code)
            rooms_manager.room_count -= 1
            print(f"Sala {room_code} eliminada (sin jugadores)")
    
    leave_room(room_code)
    
    emit('player_left', {
        'username': username
    }, room=room_code)
    
    print(f"{username} salió de la sala {room_code}")

@socketio.on('start_game')
def handle_start_game(data):
    """Maneja el inicio del juego"""
    room_code = data.get('room_code')
    username = data.get('username')
    
    if not room_code:
        emit('error', {'message': 'Código de sala requerido'})
        return
    
    room_data = rooms_manager.get_room_by_code(room_code)
    
    if not room_data:
        emit('error', {'message': 'Sala no encontrada'})
        return
    
    # Verificar que el usuario es el creador
    if room_data['creator'] != username:
        emit('error', {'message': 'Solo el creador puede iniciar el juego'})
        return
    
    # Verificar que hay al menos 2 jugadores
    if len(room_data['players']) < 2:
        emit('error', {'message': 'Se necesitan al menos 2 jugadores'})
        return
    
    # Verificar que el juego no ha iniciado
    if room_data['state'] == RoomStatus.PLAYING.value:
        emit('error', {'message': 'El juego ya ha iniciado'})
        return
    
    # Iniciar el juego
    rooms_manager.start_game(room_code)
    init_game_state(room_code, room_data)
    
    # Emitir evento de inicio
    emit('game_started', {
        'message': 'El juego ha comenzado',
        'players': room_data['players'],
        'gamemode': room_data['gamemode'],
        'difficulty': room_data['difficulty'],
        'lives': room_data['lives']
    }, room=room_code)
    
    print(f"Juego iniciado en sala {room_code}")
    
    # Iniciar el primer turno
    next_turn(room_code)

@socketio.on('submit_word')
def handle_submit_word(data):
    """Maneja cuando un jugador envía una palabra"""
    room_code = data.get('room_code')
    username = data.get('username')
    word = data.get('word', '').strip().upper()
    
    if not room_code or not username or not word:
        emit('error', {'message': 'Faltan datos requeridos'})
        return
    
    room_data = rooms_manager.get_room_by_code(room_code)
    
    if not room_data or room_code not in game_states:
        emit('error', {'message': 'Sala no encontrada o juego no iniciado'})
        return
    
    game_state = game_states[room_code]
    current_idx = game_state['current_player_index']
    current_player = room_data['players'][current_idx]
    
    # Verificar que es el turno del jugador
    if current_player['username'] != username:
        emit('error', {'message': 'No es tu turno'})
        return
    
    # Calcular tiempo tomado
    time_taken = time.time() - game_state['turn_start_time']
    
    # Validar la palabra
    validation = get_game_logic().validate_word(
        word,
        game_state['current_prompt'],
        game_state['used_words']
    )
    
    if validation['valid']:
        # Palabra válida
        cancel_turn_timer(room_code)
        
        # Calcular puntos
        points = get_game_logic().calculate_points(word, time_taken, room_data['difficulty'])
        
        # Agregar puntos al jugador
        rooms_manager.player_add_points(room_code, username, points)
        current_player['points'] += points
        
        # Agregar palabra a la lista de usadas
        game_state['used_words'].append(word)
        rooms_manager.add_word(room_code, word, username)
        
        # Emitir palabra correcta
        emit('word_accepted', {
            'username': username,
            'word': word,
            'points': points,
            'total_points': current_player['points'],
            'time_taken': round(time_taken, 2)
        }, room=room_code)
        
        # Pasar al siguiente turno
        next_turn(room_code)
    else:
        # Palabra inválida - el jugador pierde una vida
        game_state['player_lives'][current_idx] -= 1
        
        emit('word_rejected', {
            'username': username,
            'word': word,
            'reason': validation['reason'],
            'lives_remaining': game_state['player_lives'][current_idx]
        }, room=room_code)
        
        # Verificar si el jugador fue eliminado
        if game_state['player_lives'][current_idx] <= 0:
            cancel_turn_timer(room_code)
            game_state['alive_players'].remove(current_idx)
            
            emit('player_eliminated', {
                'username': username,
                'remaining_players': len(game_state['alive_players'])
            }, room=room_code)
            
            # Verificar si hay un ganador
            if len(game_state['alive_players']) <= 1:
                end_game(room_code)
                return
            
            # Pasar al siguiente turno
            next_turn(room_code)
        else:
            # El jugador sigue vivo, puede intentar de nuevo
            # No cancelamos el timer, sigue corriendo
            pass

@socketio.on('send_message')
def handle_send_message(data):
    """Maneja mensajes de chat en la sala"""
    room_code = data.get('room_code')
    username = data.get('username')
    message = data.get('message', '').strip()
    
    if not room_code or not username or not message:
        return
    
    emit('chat_message', {
        'username': username,
        'message': message,
        'timestamp': int(time.time() * 1000)
    }, room=room_code)

@socketio.on('typing_word')
def handle_typing_word(data):
    """Transmite en tiempo real lo que el jugador está escribiendo"""
    room_code = data.get('room_code')
    username = data.get('username')
    word = data.get('word', '')
    
    if not room_code or not username:
        return
    
    # Emitir a todos en la sala excepto al que está escribiendo
    emit('player_typing', {
        'username': username,
        'word': word
    }, room=room_code, include_self=False)

@socketio.on('get_room_state')
def handle_get_room_state(data):
    """Obtiene el estado actual de una sala (útil para reconexiones)"""
    room_code = data.get('room_code')
    
    if not room_code:
        emit('error', {'message': 'Código de sala requerido'})
        return
    
    room_data = rooms_manager.get_room_by_code(room_code)
    
    if not room_data:
        emit('error', {'message': 'Sala no encontrada'})
        return
    
    response = {
        'room_code': room_code,
        'players': room_data['players'],
        'state': room_data['state'],
        'gamemode': room_data['gamemode'],
        'difficulty': room_data['difficulty'],
        'lives': room_data['lives'],
        'max_players': room_data['max_players']
    }
    
    # Si el juego está en curso, agregar información del juego
    if room_code in game_states:
        game_state = game_states[room_code]
        current_idx = game_state['current_player_index']
        
        response['game_state'] = {
            'current_player': room_data['players'][current_idx]['username'],
            'current_prompt': game_state['current_prompt'],
            'round': game_state['round_number'],
            'player_lives': {room_data['players'][i]['username']: game_state['player_lives'][i] 
                           for i in range(len(room_data['players']))},
            'used_words_count': len(game_state['used_words'])
        }
    
    emit('room_state', response)

print("Game events loaded successfully")
