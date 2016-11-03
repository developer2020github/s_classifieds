#https://www.youtube.com/watch?v=PJK950Gp780
#https://www.youtube.com/watch?v=xTumGVC90_0
from flask_sqlalchemy import SQLAlchemy


def create_db(flask_app):
    db = SQLAlchemy(flask_app)
    return db

