from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relationship("Address", back_populates="user")

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="addresses")

#http://docs.sqlalchemy.org/en/latest/orm/backref.html
# a more useful tutorial:
#http://flask-sqlalchemy.pocoo.org/2.1/models/.
'''
 backref is a simple way to also declare a new property on the Address class.
 You can then also use my_address.person to get to the person at that address.
 I.e, in one to many relationship backref on parent class gives easier
 access to parent from child records.
'''
u1 = User()
a1 = Address()
#u1.addresses
print(a1.user)