from re import match

import bcrypt
from src.lib.database import mysql

class Validator:
    def __init__(self):
        # Diccionario con los errores de validacion
        self.errors = {}
        
    def is_valid_email(self, email: str) -> bool:
        # Expresion regular para correos electrónicos
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        if not match(email_regex, email):
            self.errors["email"] = "El correo electrónico no es válido."
            return False
        return True

    def is_valid_username(self, username: str) -> bool:
        # Expresión regular para nombres de usuario
        username_regex = r'^[a-zA-Z0-9_]{3,15}$'

        if not match(username_regex, username):
            self.errors["username"] = "El nombre de usuario no es válido."
            return False
        return True

    def is_strong_password(self, password: str) -> bool:
        if len(password) < 8:
            self.errors["password_length"] = "La contraseña debe tener al menos 8 caracteres."
        
        if not any(char.isupper() for char in password):
            self.errors["password_uppercase"] = "La contraseña debe contener al menos una letra mayúscula."
        
        if not any(char.islower() for char in password):
            self.errors["password_lowercase"] = "La contraseña debe contener al menos una letra minúscula."
        
        if not any(char.isdigit() for char in password):
            self.errors["password_digit"] = "La contraseña debe contener al menos un número."
        
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for char in password):
            self.errors["password_special"] = "La contraseña debe contener al menos un carácter especial."
        
        # Chequeo con un fallback para evitar el KeyError
        if any([
            self.errors.get("password_length", False),
            self.errors.get("password_uppercase", False),
            self.errors.get("password_lowercase", False),
            self.errors.get("password_digit", False),
            self.errors.get("password_special", False)
        ]):
            return False
        
        return True
    
    def passwords_match(self, password: str, password_confirmation: str) -> bool:
        if password != password_confirmation:
            self.errors["password_confirmation"] = "Las contraseñas no coinciden."
            return False
        return True
    
    def email_exists(self, email: str) -> bool:
        with mysql.get_db().cursor() as cursor:
            cursor.execute("SELECT * FROM `USUARIO` WHERE `Correo` = %s", (email))
            if cursor.fetchone() is not None:
                self.errors["email_exists"] = "El correo electrónico ya está registrado."
                return True
        return False
        
    def username_exists(self, username: str) -> bool:
        with mysql.get_db().cursor() as cursor:
            cursor.execute("SELECT * FROM `USUARIO` WHERE `Username` = %s", (username))
            if cursor.fetchone() is not None:
                self.errors["username_exists"] = "El nombre de usuario ya está registrado."
                return True
        return False
        
    def correct_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def is_valid_word(self, word: str) -> bool:
        if len(word) < 2:
            self.errors["word_length"] = "La palabra debe tener al menos 2 letras."
            return False
        if not word.isalpha():
            self.errors["word_alpha"] = "La palabra debe contener solo letras."
            return False
        return True
    
    def word_exists_id(self, word_id: int) -> bool | str:
        with mysql.get_db().cursor() as cursor:
            
            cursor.execute("SELECT `Palabra` FROM `PALABRA` WHERE `ID_Palabra` = %s", (word_id))
            result = cursor.fetchone()
            
            if result is None:
                self.errors["word_exists"] = "La palabra no existe."
                return False
            
            word = result[0]
        return word
    
    def get_errors(self):
        return self.errors