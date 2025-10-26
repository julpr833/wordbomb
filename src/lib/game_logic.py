import random
import string
from src.lib.room_config import Gamemodes, Difficulty
from src.lib.words import Words

class GameLogic:
    """
    Lógica del juego Word Bomb
    Maneja los 3 modos de juego: Classic, Reversed, Hardcore
    """
    
    def __init__(self):
        self.words_manager = Words()
    
    def generate_prompt(self, gamemode: int, difficulty: int) -> dict:
        """
        Genera un prompt según el modo de juego y dificultad
        
        Modos:
        - CLASSIC (1): Letras consecutivas que deben estar en la palabra
        - REVERSED (2): Letras que NO deben estar en la palabra
        - HARDCORE (3): Letras en posiciones específicas
        
        Dificultad:
        - EASY (1): 2 letras
        - NORMAL (2): 2-3 letras
        - HARD (3): 3-4 letras
        """
        
        if gamemode == Gamemodes.CLASSIC.value:
            return self._generate_classic_prompt(difficulty)
        elif gamemode == Gamemodes.REVERSED.value:
            return self._generate_reversed_prompt(difficulty)
        elif gamemode == Gamemodes.HARDCORE.value:
            return self._generate_hardcore_prompt(difficulty)
        else:
            return self._generate_classic_prompt(difficulty)
    
    def _generate_classic_prompt(self, difficulty: int) -> dict:
        """
        Modo CLASSIC: Genera sílabas con sentido (consonante-vocal o vocal-consonante)
        Ejemplo: "BO", "AR", "TE" - sílabas que tienen sentido fonético
        """
        # Consonantes y vocales comunes en español
        consonantes = 'BCDFGHJLMNPQRSTVWXYZ'
        vocales = 'AEIOU'
        
        # Sílabas comunes en español
        silabas_comunes = [
            'BA', 'BE', 'BI', 'BO', 'BU',
            'CA', 'CE', 'CI', 'CO', 'CU',
            'DA', 'DE', 'DI', 'DO', 'DU',
            'FA', 'FE', 'FI', 'FO', 'FU',
            'GA', 'GE', 'GI', 'GO', 'GU',
            'HA', 'HE', 'HI', 'HO', 'HU',
            'JA', 'JE', 'JI', 'JO', 'JU',
            'LA', 'LE', 'LI', 'LO', 'LU',
            'MA', 'ME', 'MI', 'MO', 'MU',
            'NA', 'NE', 'NI', 'NO', 'NU',
            'PA', 'PE', 'PI', 'PO', 'PU',
            'RA', 'RE', 'RI', 'RO', 'RU',
            'SA', 'SE', 'SI', 'SO', 'SU',
            'TA', 'TE', 'TI', 'TO', 'TU',
            'VA', 'VE', 'VI', 'VO', 'VU',
            'AR', 'ER', 'IR', 'OR', 'UR',
            'AL', 'EL', 'IL', 'OL', 'UL',
            'AN', 'EN', 'IN', 'ON', 'UN'
        ]
        
        if difficulty == Difficulty.EASY.value:
            # Fácil: una sílaba simple
            prompt = random.choice(silabas_comunes)
        elif difficulty == Difficulty.NORMAL.value:
            # Normal: 2 letras o una sílaba
            prompt = random.choice(silabas_comunes)
        else:  # HARD
            # Difícil: combinación de 2 sílabas o 3 letras
            if random.random() < 0.5:
                # Dos sílabas
                prompt = random.choice(silabas_comunes[:30])  # Primera mitad
            else:
                # 3 letras con patrón consonante-vocal-consonante
                consonante1 = random.choice(consonantes)
                vocal = random.choice(vocales)
                consonante2 = random.choice(consonantes)
                prompt = consonante1 + vocal + consonante2
        
        return {
            "type": "classic",
            "prompt": prompt,
            "value": prompt,
            "description": f"Palabra que contenga: {prompt}"
        }
    
    def _generate_reversed_prompt(self, difficulty: int) -> dict:
        """
        Modo REVERSED: Genera letras que NO deben aparecer en la palabra
        Ejemplo: "AE" - la palabra NO debe contener ni "A" ni "E"
        """
        if difficulty == Difficulty.EASY.value:
            length = 2
        elif difficulty == Difficulty.NORMAL.value:
            length = random.choice([2, 3])
        else:  # HARD
            length = random.choice([3, 4])
        
        # Evitar letras muy comunes para que no sea imposible
        common_letters = 'AEIOU'
        available_letters = string.ascii_uppercase
        
        # En dificultad fácil, evitamos usar solo vocales
        if difficulty == Difficulty.EASY.value:
            available_letters = ''.join([l for l in string.ascii_uppercase if l not in 'AEIOU'])
        
        letters = ''.join(random.sample(available_letters, length))
        
        return {
            "type": "reversed",
            "prompt": letters,
            "description": f"Palabra SIN las letras: {letters}"
        }
    
    def _generate_hardcore_prompt(self, difficulty: int) -> dict:
        """
        Modo HARDCORE: Genera letras en posiciones específicas
        Ejemplo: "_O_B_" - la palabra debe tener O en posición 2 y B en posición 4
        """
        if difficulty == Difficulty.EASY.value:
            word_length = random.choice([4, 5])
            num_letters = 2
        elif difficulty == Difficulty.NORMAL.value:
            word_length = random.choice([5, 6])
            num_letters = random.choice([2, 3])
        else:  # HARD
            word_length = random.choice([6, 7, 8])
            num_letters = random.choice([3, 4])
        
        # Crear patrón con guiones bajos
        pattern = ['_'] * word_length
        
        # Seleccionar posiciones aleatorias para las letras
        positions = random.sample(range(word_length), num_letters)
        
        # Asignar letras aleatorias a esas posiciones
        for pos in positions:
            pattern[pos] = random.choice(string.ascii_uppercase)
        
        pattern_str = ''.join(pattern)
        
        return {
            "type": "hardcore",
            "prompt": pattern_str,
            "description": f"Palabra con patrón: {pattern_str}",
            "length": word_length
        }
    
    def validate_word(self, word: str, prompt: dict, used_words: list) -> dict:
        """
        Valida si una palabra es correcta según el prompt y las reglas del juego
        
        Retorna:
        {
            "valid": bool,
            "reason": str,
            "word_id": int (si es válida)
        }
        """
        word = word.upper().strip()
        
        # Validación 1: Palabra no vacía
        if not word:
            return {"valid": False, "reason": "La palabra está vacía"}
        
        # Validación 2: Solo letras
        if not word.isalpha():
            return {"valid": False, "reason": "La palabra debe contener solo letras"}
        
        # Validación 3: Longitud mínima
        if len(word) < 3:
            return {"valid": False, "reason": "La palabra debe tener al menos 3 letras"}
        
        # Validación 4: Palabra ya usada en esta partida
        if word in used_words:
            return {"valid": False, "reason": "Esta palabra ya fue usada"}
        
        # Validación 5: Palabra existe en la base de datos
        word_id = self.words_manager.get_word(word)
        if word_id is False:
            return {"valid": False, "reason": "La palabra no existe en el diccionario"}
        
        # Validación 6: Cumple con las reglas del modo de juego
        if prompt["type"] == "classic":
            if prompt["prompt"] not in word:
                return {"valid": False, "reason": f"La palabra debe contener '{prompt['prompt']}'"}
        
        elif prompt["type"] == "reversed":
            forbidden_letters = prompt["prompt"]
            for letter in forbidden_letters:
                if letter in word:
                    return {"valid": False, "reason": f"La palabra no debe contener '{letter}'"}
        
        elif prompt["type"] == "hardcore":
            pattern = prompt["prompt"]
            if len(word) != len(pattern):
                return {"valid": False, "reason": f"La palabra debe tener {len(pattern)} letras"}
            
            for i, letter in enumerate(pattern):
                if letter != '_' and word[i] != letter:
                    return {"valid": False, "reason": f"La letra en posición {i+1} debe ser '{letter}'"}
        
        return {"valid": True, "reason": "Palabra válida", "word_id": word_id}
    
    def calculate_points(self, word: str, time_taken: float, difficulty: int) -> int:
        """
        Calcula los puntos ganados por una palabra
        
        Factores:
        - Longitud de la palabra (más letras = más puntos)
        - Tiempo de respuesta (más rápido = más puntos)
        - Dificultad (mayor dificultad = multiplicador)
        """
        base_points = len(word) * 10
        
        # Bonus por velocidad (máximo 50 puntos extra)
        # Si responde en menos de 5 segundos, bonus completo
        time_bonus = max(0, 50 - int(time_taken * 5))
        
        # Multiplicador por dificultad
        difficulty_multiplier = {
            Difficulty.EASY.value: 1.0,
            Difficulty.NORMAL.value: 1.5,
            Difficulty.HARD.value: 2.0
        }.get(difficulty, 1.0)
        
        total_points = int((base_points + time_bonus) * difficulty_multiplier)
        
        return total_points
    
    def get_next_player_index(self, current_index: int, total_players: int, alive_players: list) -> int:
        """
        Obtiene el índice del siguiente jugador que está vivo
        """
        next_index = (current_index + 1) % total_players
        attempts = 0
        
        # Buscar el siguiente jugador vivo
        while next_index not in alive_players and attempts < total_players:
            next_index = (next_index + 1) % total_players
            attempts += 1
        
        return next_index if next_index in alive_players else current_index
