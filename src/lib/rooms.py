import random
from string import ascii_uppercase
import time
from src.lib.room_config import Gamemodes, Difficulty, RoomStatus
from src.lib.database import mysql, get_user_id

class Rooms():
    # Patron de diseño usando Singleton para obtener siempre
    # La misma referencia de memoria a esta clase en el Heap
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.rooms = {}
            cls._instance.room_count = 0
            cls._instance.app = None
        return cls._instance

    def set_app(self, app):
        """Guardar referencia a la app de Flask"""
        self.app = app

    def __init__(self):
        # Evita re-inicializar si ya fue creada y me mando a volar el KeyError nuevamente
        if not getattr(self, "_initialized", False):
            self._initialized = True
    
    def __gen_room_code__(self):
        code = ""
        # Generar un codigo único de 6 caracteres
        while code == "" or code in self.rooms:
            code = "".join(random.choice(ascii_uppercase) for _ in range(6))
        return code
    
    def add_room(self, 
                creator: str, 
                gamemode: int = Gamemodes.CLASSIC.value, 
                difficulty: int = Difficulty.NORMAL.value, 
                lives: int = 3, 
                max_players: int = 4
            ):
        code = self.__gen_room_code__()
        self.rooms[code] = {
            "players": [], 
            "state": RoomStatus.WAITING.value, 
            "gamemode": gamemode, 
            "difficulty": difficulty, 
            "lives": lives, 
            "max_players": max_players,
            "words": [],
            "creator": creator,
            "turn": 0,
            "winner": None,
            "creation_time": int(round(time.time() * 1000))
        }
        self.room_count += 1
        return code
    
    def get_all_rooms(self):
        return self.rooms
    
    def get_room_by_code(self, code):
        if code in self.rooms:
            return self.rooms[code]
        return None
    
    def join_player(self, code, username, avatar=None):
        if code in self.rooms:
            if len(self.rooms[code]["players"]) >= self.rooms[code]["max_players"]:
                return False
            
            self.rooms[code]["players"].append({
                "username": username,
                "points": 0,
                "avatar": avatar
            })
            return True
        return False
    
    def remove_player(self, code, username):
        if code in self.rooms:
            self.rooms[code]["players"].remove(username)
            return True
        return False
    
    def get_players(self, code):
        if code in self.rooms:
            return self.rooms[code]["players"]
        return []
    
    def start_game(self, code):
        if code in self.rooms:
            self.rooms[code]["state"] = RoomStatus.PLAYING.value
            
    def add_word(self, code, word, username=None):
        if code in self.rooms:
            self.rooms[code]["words"].append({
                "word": word,
                "turn": self.rooms[code]["turn"],
                "username": username
            })
    
    def next_turn(self, code):
        if code in self.rooms:
            self.rooms[code]["turn"] += 1
    
    def player_add_points(self, code, username, points):
        if code in self.rooms:
            for player in self.rooms[code]["players"]:
                if player["username"] == username:
                    player["points"] += points
                    break
    
    def get_winner(self, code):
        if code in self.rooms:
            return max(self.rooms[code]["players"], key=lambda x: x["points"])["username"]    
        
    def set_winner(self, code, username):
        if code in self.rooms:
            self.rooms[code]["winner"] = username
    
    def is_in_any_room(self, username):
        for room in self.rooms.values():
            for player in room["players"]:
                if player["username"] == username:
                    return True
        return False
    
    def get_player_room(self, username):
        for room in self.rooms.values():
            for player in room["players"]:
                if player["username"] == username:
                    return room
            
    def end_game(self, code):
        if code not in self.rooms:
            return
            
        room = self.rooms[code]
        
        # Guardar partida en la base de datos
        try:
            from datetime import datetime
            print(f"[BD] Iniciando guardado de partida {code}")
            print(f"[BD] Datos de la sala: {room}")
            
            # Usar el contexto de la aplicación para acceder a la BD
            if not self.app:
                print("[BD] Error: No hay referencia a la app de Flask")
                return
                
            with self.app.app_context():
                db = mysql.get_db()
                with db.cursor() as cursor:
                    # 1. Insertar la partida
                    query = """
                    INSERT INTO PARTIDA (FechaInicio, FechaFinalizacion, TotalPalabras, TotalTurnos, Ganador_ID, Creador_ID)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    fecha_inicio = datetime.fromtimestamp(room['creation_time'] / 1000)
                    fecha_fin = datetime.now()
                    total_palabras = len(room.get('words', []))
                    total_turnos = room.get('turn', 0)
                    ganador_id = get_user_id(room.get('winner'), db) if room.get('winner') else None
                    creador_id = get_user_id(room['creator'], db)
                    
                    print(f"[BD] Insertando partida: inicio={fecha_inicio}, fin={fecha_fin}, palabras={total_palabras}, turnos={total_turnos}")
                    cursor.execute(query, (fecha_inicio, fecha_fin, total_palabras, total_turnos, ganador_id, creador_id))
                    partida_id = cursor.lastrowid
                    print(f"[BD] Partida insertada con ID: {partida_id}")
                    
                    # 2. Insertar participantes
                    print(f"[BD] Insertando {len(room['players'])} participantes")
                    for player in room['players']:
                        query = """
                        INSERT INTO PARTIDA_PARTICIPANTE (Usuario_ID, Partida_ID, PuntosGanados)
                        VALUES (%s, %s, %s)
                        """
                        usuario_id = get_user_id(player['username'], db)
                        puntos = player.get('points', 0)
                        cursor.execute(query, (usuario_id, partida_id, puntos))
                        print(f"[BD] Participante insertado: {player['username']} con {puntos} puntos")
                    
                    # 3. Insertar palabras usadas
                    print(f"[BD] Insertando {len(room.get('words', []))} palabras")
                    palabras_insertadas = 0
                    for word_data in room.get('words', []):
                        try:
                            palabra = word_data.get('word', '').upper()
                            username_palabra = word_data.get('username')
                            turno = word_data.get('turn', 0)
                            
                            if not palabra or not username_palabra:
                                print(f"[BD] Palabra omitida (datos incompletos): {word_data}")
                                continue
                            
                            # Obtener ID de la palabra
                            query_word = "SELECT ID_Palabra FROM PALABRA WHERE Palabra = %s"
                            cursor.execute(query_word, (palabra,))
                            result = cursor.fetchone()
                            
                            if result:
                                palabra_id = result[0]  # Tupla: primer elemento
                                usuario_id = get_user_id(username_palabra, db)
                                
                                if usuario_id:
                                    query = """
                                    INSERT INTO PALABRAS_PARTIDA (Partida_ID, Palabra_ID, Usuario_ID, Turno)
                                    VALUES (%s, %s, %s, %s)
                                    """
                                    cursor.execute(query, (partida_id, palabra_id, usuario_id, turno))
                                    palabras_insertadas += 1
                                    print(f"[BD] Palabra insertada: {palabra} por {username_palabra} en turno {turno}")
                            else:
                                print(f"[BD] Palabra no encontrada en diccionario: {palabra}")
                        except Exception as e:
                            print(f"[BD] Error guardando palabra {word_data}: {e}")
                    
                    print(f"[BD] Total palabras insertadas: {palabras_insertadas}")
                    
                    db.commit()
                    print(f"Partida {partida_id} guardada correctamente en la base de datos")
                
        except Exception as e:
            print(f"Error guardando partida en BD: {e}")
            db.rollback()
        
        # Eliminar la sala
        self.rooms.pop(code)
        self.room_count -= 1
        print(f"Sala {code} eliminada correctamente")