from flaskext.mysql import MySQL

mysql = MySQL()

def get_user_id(username: str) -> bool | int:
    with mysql.get_db().cursor() as cursor:
        cursor.execute("SELECT `ID_Usuario` FROM `USUARIO` WHERE `Username` = %s", (username))
        result = cursor.fetchone()
        if result is None:
            return False
        return result[0]