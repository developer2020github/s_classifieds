'''
This module creates the database
'''
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
'''
Note on categories and sub categories:
even though a sub-category can be present in different

'''

'''
Examples
class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
'''

class Ad(Base):
    __tablename__ = 'ad'

    id = Column(Integer, primary_key=True)
    category = Column(String(250), nullable=False)
    sub_category = Column(String(250), nullable = False)


#engine = create_engine('sqlite:///restaurantmenu.db')
#code to created database
engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")
Base.metadata.create_all(engine)

