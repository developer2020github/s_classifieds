from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_database import Base, Ad
engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")
Ad.__table__.drop(engine)
