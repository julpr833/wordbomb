from src import create_app, socketio
from os import getenv

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=getenv("PORT", 7777), debug=True)
