from flask import jsonify
from src.routes import api
from flask_jwt_extended import get_jwt, jwt_required
from src.lib.jwt_config import revoked_tokens

@api.route('auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  # Identificador del token
    revoked_tokens.add(jti)
    return jsonify(sucess="Logged out"), 200