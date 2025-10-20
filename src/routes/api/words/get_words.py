from flask import jsonify
from src.routes import api
from src.middleware.auth import auth_required
from src.lib.words import Words

@api.route('/words/get-words', methods=['GET'])
@auth_required(level=2)
def get_words(username):
    words = Words()
    all_words = words.get_words()
    return jsonify(all_words), 200