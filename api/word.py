from app import app
from flask import request
from markupsafe import escape

@app.route("/word")
def word():
    """
    TODO: Implement this

    /word?word=<word>
    Returns Boolean value associated to word's existence in the cache.
    
    PARAMS
    :word <str>: The word to check
    
    OUTPUT
    :<bool>: Whether if it exists or not.
    """
    word = request.args.get("word")
    return f"{escape(word)}."