from flask import jsonify
from src.routes import api
from src.middleware.auth import auth_required
from src.util.logger import logger
from src.lib.database import mysql

@api.route('/words/get-words', methods=['GET'])
@auth_required(level=2)
def get_words(username):
    with mysql.get_db().cursor() as cursor:
        cursor.execute("SELECT `Palabra` FROM `PALABRA`")
        result = cursor.fetchall()
        words = [word[0] for word in result]
    return jsonify(words), 200