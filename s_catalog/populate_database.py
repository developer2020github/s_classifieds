from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_database import Base, Ad
# from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random

engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Add ads
ad = Ad(category="first category", sub_category="first sub_category")
session.add(ad)

session.commit()
