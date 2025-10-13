from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from src.database import mysql

# Acá se me complico porque me tiraba un AssertionError
# La solución fue meterle el @wraps para persisitir los metadatos
# Al programador leyendo esto, si queres añadir un decorador asegurate de cubrir el wrapper con @wraps

def auth_required(level=1):
    def decorator(fn):
        
        # Persistir metadatos, no es necesario pero es una buena práctica
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Si no tiene token, retorna 401 automáticamente
            verify_jwt_in_request() 
            
            # Saco el nombre de usuario usando la identidad del token
            username = get_jwt_identity()

            # Query, saco primero la ID del usuario con el nombre de usuario, después saco sus roles
            query = """
            SELECT * FROM `USUARIO_ROL`
            WHERE `USUARIO_ROL`.`Usuario_ID` = 
            (SELECT `ID_Usuario` FROM `USUARIO` WHERE `Username` = %s)
            """
            with mysql.get_db().cursor() as cursor:
                cursor.execute(query, (username))
                roles = [r[0] for r in cursor.fetchall()]
            
            if not roles:
                return {"error": "Usuario sin rol asignado"}, 403

            # Me fijo si el usuario tiene los permisos suficientes en cualquier ocurrencia de los roles
            if all(r < level for r in roles):
                return {"error": "Permiso denegado"}, 403

            # Si el usuario tiene los permisos suficientes, pasa a la función
            return fn(username=username, *args, **kwargs)
        return wrapper
    return decorator


def only_guest():
    def decorator(fn):
        # Persistir los metadatos
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Si acá no tira error es porque inició sesión
                verify_jwt_in_request()
                return {"error": f"Ya iniciaste sesión"}, 400
            except Exception:
                # Si tira excepción es que no tiene token o no es válido, por eso seguimos
                return fn(*args, **kwargs)
        return wrapper
    return decorator