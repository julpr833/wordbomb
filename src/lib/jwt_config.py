revoked_tokens = set()

def register_jwt_handlers(jwt):
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return {"error": "Token faltante o inválido."}, 401

    @jwt.invalid_token_loader
    def invalid_token_response(error):
        return {"error": "El token no es válido."}, 422

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return {"error": "El token ha expirado, iniciá sesión de nuevo."}, 401

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_payload):
        return {"error": "El token fue revocado."}, 401
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']  # JWT ID
        return jti in revoked_tokens
