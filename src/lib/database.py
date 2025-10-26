from flaskext.mysql import MySQL

mysql = MySQL()

def get_user_id(username: str, db_connection=None) -> bool | int:
    """
    Obtiene el ID de un usuario por su username.
    Si se proporciona db_connection, lo usa; si no, obtiene uno nuevo.
    """
    if db_connection:
        # Usar la conexión proporcionada
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT `ID_Usuario` FROM `USUARIO` WHERE `Username` = %s", (username,))
            result = cursor.fetchone()
            if result is None:
                return False
            return result[0]  # Tupla: primer elemento
    else:
        # Obtener nueva conexión (requiere contexto de Flask)
        with mysql.get_db().cursor() as cursor:
            cursor.execute("SELECT `ID_Usuario` FROM `USUARIO` WHERE `Username` = %s", (username,))
            result = cursor.fetchone()
            if result is None:
                return False
            return result[0]  # Tupla: primer elemento