"""
This module defines the database schema for s-classifieds application and, if run, creates database.

Tables:
 Category: ad categories
 SubCategory: ad sub-categories
 City: list of locations where ads can belong to
 Ad: list of ads
 User: list of users. Has extra functions to support flask-login


Categories and sub categories:
    even though a sub-category with same name can be present in different category, it is
    not the same sub-category. I.e., "houses" in "properties for sale" are not
    same as "houses" in "properties for rent".

    Relation is "one to multiple" - one category can refer to multiple sub-categories.
    From the sub-category side relationship is multiple to one - i.e. , if we know sub-category id - we should be able to
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

Users should be able to provide emails, contact names and phones different from the ones they registered under.

"""
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import exc

import s_catalog_options
import generate_data
Base = declarative_base()


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
    password = Column(String)
    authenticated = Column(Boolean, default=False)
    ads = relationship("Ad", back_populates="user", cascade="delete")

# extra fields to support flask-login
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return self.authenticated

    # no functionality for anonymous users, so always return False.
    def is_anonymous(self):
        return False


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
    price_cents = Column(Integer())
    currency = Column(String(10))
    title = Column(String(250))


def populate_application_initial_data(current_session):
    for category_name in generate_data.get_categories():
        cat = Category(name = category_name)
        print cat
        current_session.add(cat)

        current_session.commit()

    q = current_session.query(Category)
    for cat in q.all():
        subcategories_names  = generate_data.get_sub_categories(cat.name)
        for subcategory_name in subcategories_names:
            sub_cat = SubCategory(name = subcategory_name, category_id = cat.id)
            current_session.add(sub_cat)

    for city_name in s_catalog_options.CITIES_LIST:
        city = City(name=city_name)
        current_session.add(city)

        current_session.commit()


def create_postgres():
    #http://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy
    current_engine = create_engine("postgresql://postgres:postgres@localhost/postgres")
    conn = current_engine.connect()
    conn.execute("commit")
    conn.execute("create database s_classifieds")
    conn.close()

    current_engine=create_engine(s_catalog_options.CREATE_ENGINE_CMD_STRING)
    Base.metadata.create_all(current_engine)

def create(current_engine):
    Base.metadata.create_all(current_engine)


if __name__ == "__main__":
    engine = create_engine(s_catalog_options.CREATE_ENGINE_CMD_STRING)
    if s_catalog_options.DATABASE_TO_USE==s_catalog_options.DATABASE_POSTGRES:
        create_postgres()
    else:
        create(engine)

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    populate_application_initial_data(session)
