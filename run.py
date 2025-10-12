from src import create_app
from os import getenv

app = create_app()

if __name__ == "__main__":
    app.run("127.0.0.1", port=getenv("PORT", 7777), debug=True)