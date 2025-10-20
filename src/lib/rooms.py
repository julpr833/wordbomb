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
        return cls._instance

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
    
    def add_room(self, creator, gamemode=Gamemodes.CLASSIC.value, difficulty=Difficulty.NORMAL.value, lives=3, max_players=4):
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
    
    def join_player(self, code, username):
        if code in self.rooms:
            self.rooms[code]["players"].append({
                "username": username,
                "points": 0
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
            
    def add_word(self, code, word):
        if code in self.rooms:
            self.rooms[code]["words"].append({
                "word": word,
                "turn": self.rooms[code]["turn"]
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
            
    def end_game(self, code):
        if code in self.rooms:
            end_time = int(round(time.time() * 1000))
            with mysql.get_db.cursor() as cursor:
                
                # Primero registro la partida en la tabla de partidas
                
                query = """
                INSERT INTO `PARTIDA`
                (, 
                `FechaInicio`, `FechaFinalizacion`, 
                `TotalPalabras`, `TotalTurnos`, 
                `Ganador_ID`, `Creador_ID`
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    self.rooms[code]["creation_time"],
                    end_time,
                    len(self.rooms[code]["words"]),
                    self.rooms[code]["turn"],
                    self.rooms[code]["winner"],
                    self.rooms[code]["creator"]
                )
                cursor.execute(query, values)
                
                # Necesito la ID de la ultima partida registrada
                last_game_id = cursor.lastrowid
                
                # Ahora registro los participantes de la partida
                
                for player in self.rooms[code]["players"]:
                    query = """
                    INSERT INTO `PARTIDA_PARTICIPANTE`
                    (`Usuario_ID`, `Partida_ID`, `PuntosGanados`)
                    VALUES (%s, %s, %s)
                    """
                    values = (get_user_id(player["username"]), last_game_id, player["points"])
                    cursor.execute(query, values)
                    
                # Por ultimo registro todas las palabras usadas en la partida
                
                for word in self.rooms[code]["words"]:
                    query = """
                    INSERT INTO `PALABRAS_PARTIDA`
                    (`Partida_ID`, `Palabra_ID`, `Usuario_ID`, `Turno`)
                    VALUES (%s, %s, %s, %s)
                    """
                    values = (last_game_id, )
                    cursor.execute(query, values)
                    
                mysql.get_db.commit()
                
                self.rooms.pop(code)
                self.room_count -= 1