from src.lib.database import mysql

class Words():
    # Patron de diseño usando Singleton para obtener siempre
    # La misma referencia de memoria a esta clase en el Heap
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.words = []
        return cls._instance

    def __init__(self, words: list = []):
        # Solo cachear la primera vez
        # Aca usé getattr para evitar el KeyError
        if not getattr(self, "_initialized", False):
            self.words = words
            self.__cache_all_words__()
            self._initialized = True  # evita recargar datos cada vez
    
    def __cache_all_words__(self):
        with mysql.get_db().cursor() as cursor:
            cursor.execute("SELECT `ID_Palabra`, `Palabra` FROM `PALABRA`")
            result = cursor.fetchall()
            for word in result:
                self.words.append({
                    "id": word[0],
                    "word": word[1] 
                })   
                
    def get_word(self, to_search: str) -> int | bool:
        for word in self.words:
            if word['word'] == to_search:
                return word['id']
        return False

    def get_word_by_id(self, word_id: int) -> str | bool:
        # Basandome en el principio inverso...
        for w in self.words:
            if w['id'] == word_id:
                return w['word']
        return False
    
    def get_words(self) -> list[str]:
        return self.words
            
    def add_word(self, word: str) -> bool:
        if word in self.words:
            return False
        
        with mysql.get_db().cursor() as cursor:
            cursor.execute("INSERT INTO `PALABRA` (`Palabra`) VALUES (%s)", (word))
            mysql.get_db().commit()
            self.words.append({
                "id": cursor.lastrowid,
                "word": word
                })
            print(self.words)
            return True
    
    def remove_word(self, word: str) -> bool:
        to_delete = self.get_word(word)
        if to_delete is False:
            print("No existe la palabra")
            return False
        
        with mysql.get_db().cursor() as cursor:
            cursor.execute("DELETE FROM `PALABRA` WHERE `Palabra` = %s", (word))
            mysql.get_db().commit()
            delete_index = [word['word'] for word in self.words].index(word)
            del self.words[delete_index]
            print(self.words)
            return True
    
    def edit_word(self, word_id: int, new_word: str) -> bool:
        if new_word in self.words:
            return False
        
        with mysql.get_db().cursor() as cursor:
            cursor.execute("UPDATE `PALABRA` SET `Palabra` = %s WHERE `ID_Palabra` = %s", (new_word, word_id))
            mysql.get_db().commit()
            for word in self.words:
                if word["id"] == word_id:
                    word["word"] = new_word
            return True