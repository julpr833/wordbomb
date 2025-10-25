from flask import jsonify, request
from src.routes import api
from src.lib.database import mysql
from src.middleware.auth import auth_required

@api.route('/users/ban', methods=['PATCH'])
@auth_required(level=2)
def ban_user(username):
    data = request.form
    target_id = data.get('id', None)
    ban_status = data.get('ban', None)  # Espera "1" para banear, "0" para desbanear

    if not target_id or ban_status is None:
        return jsonify(error="Faltan campos requeridos (username, ban)"), 400

    # Validar valor de ban (solo 0 o 1)
    if str(ban_status) not in ["0", "1"]:
        return jsonify(error="El valor de 'ban' debe ser 0 o 1"), 400

    with mysql.get_db().cursor() as cursor:
        # Verificar si el usuario existe
        cursor.execute("SELECT ID_Usuario FROM USUARIO WHERE ID_Usuario = %s", (target_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify(error=f"El usuario '{target_id}' no existe"), 404

        # Actualizar el estado de baneo
        cursor.execute(
            "UPDATE USUARIO SET Vetado = %s WHERE ID_Usuario = %s",
            (int(ban_status), target_id)
        )
        mysql.get_db().commit()

    action = "baneado" if int(ban_status) == 1 else "desbaneado"
    return jsonify(message=f"Usuario '{target_id}' {action} exitosamente"), 200
