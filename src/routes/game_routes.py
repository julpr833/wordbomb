from flask import Blueprint

game = Blueprint('game', __name__)

@game.route("/")
def index():
    return "Game"