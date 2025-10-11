from app import app
from os import getenv

if __name__ == "__main__":
    app.run("0.0.0.0", port=getenv("PORT", 7777), debug=True)