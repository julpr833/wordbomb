from flask import jsonify
from src.routes import api
from src.lib.database import mysql
from src.middleware.auth import auth_required

@api.route('/users/get-all', methods=['GET'])
@auth_required(level=2) 
def get_all_players(username):
    """
    Devuelve la lista de todos los jugadores registrados.
    Incluye: ID, Username, Correo, FechaRegistro, Vetado -> status
    """
    with mysql.get_db().cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID_Usuario,
                FechaRegistro,
                Username,
                Vetado
            FROM USUARIO
            ORDER BY FechaRegistro DESC
        """)
        rows = cursor.fetchall()
        cols = [col[0] for col in cursor.description]  # nombres de columnas

    # Convertir tuplas a diccionarios
    players = []
    for row in rows:
        row_dict = dict(zip(cols, row))
        players.append({
            "id": row_dict["ID_Usuario"],
            "username": row_dict["Username"],
            "registration_date": row_dict["FechaRegistro"].isoformat() if hasattr(row_dict["FechaRegistro"], "isoformat") else row_dict["FechaRegistro"],
            "status": "BANEADO" if int(row_dict["Vetado"]) == 1 else "ACTIVO"
        })

    return jsonify({"players": players}), 200
