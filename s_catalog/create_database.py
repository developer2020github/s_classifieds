'''
This module creates the database
'''
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
'''
Note on categories and sub categories:
even though a sub-category with same name can be present in different category, it is
not the same sub-category. I.e., "houses" in "properties for sale" are not
same as "houses" in "properties for rent".

Relashion is "one to multiple" - one category can refer to multiple sub-categories.
From the sub-category side relatiship is multiple to one - i.e. , if we know sub-category id - we should be able to
find out category from it. For this reason ad does not need explicitly specified category,
only sub-category.

City is just list of unique cities.
So is User.

Ad.
Ad table has multiple - to - one relationship with following tables
- cities
- users
- sub-categories : as mentioned above, extra relation with sub-categories is not needed as category can be determined
based on sub-category

users should be able to provide emails, contact names and phones different from the ones they registered under.
'''


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    sub_categories = relationship("SubCategory", back_populates="category")


class SubCategory(Base):
    __tablename__ = 'sub_category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="sub_categories")
    ads = relationship("Ad", back_populates ="sub_category") # this should be list of ads in current sub-category


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    ads = relationship("Ad", back_populates="city")


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250))
    phone = Column(String(50))
    ads = relationship("Ad", back_populates="user")


class Ad(Base):
    __tablename__ = 'ad'

    id = Column(Integer, primary_key=True)

    sub_category_id = Column(Integer, ForeignKey('sub_category.id'))
    sub_category = relationship("SubCategory", back_populates="ads") # this should add .sub_category attribute to all ads

    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship("City", back_populates="ads")

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="ads")

    contact_name = Column(String(250), nullable=False)

    primary_contact = Column(String(250), nullable=False) # shoudl be an anumeration - phone numebr or e-mail being available
    # options

    contact_email = Column(String(250))
    contact_phone = Column(String(250))
    text = Column(Text())
    price = Column(Float())
    currency = Column(String(10))
    title = Column(String(250))

if __name__ == "__main__":
    engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")
    Base.metadata.create_all(engine)

