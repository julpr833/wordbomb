
from sqlalchemy import create_engine
from os import getenv

# Conectar a la base de datos
def init_database():
    host = getenv("MYSQL_HOST")
    port = getenv("MYSQL_PORT")
    user = getenv("MYSQL_USER")
    password = getenv("MYSQL_PASSWORD")
    db_name = getenv("MYSQL_DB")
    
    if not all([host, port, user, password, db_name]):
        raise RuntimeError("Missing environment variables for database connection.")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(url)

    return engine