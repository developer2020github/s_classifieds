from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import create_database
'''
this module populates database
'''

import create_database
import generate_data

# from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random

engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")

create_database.Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Add ads

#first, need to populate categoirs, then sub-categoirs, then cities, then users,
# and finally ads.
# there are two pasrt to it - first, initialising data that must be present
# in any case (like cities, categories and sub-categories)
# second is populating data that simulates user entries (fake ads)

#helper function to get id f object has name field
def get_id(list_of_objects_with_names, name):
    for o in list_of_objects_with_names:
        if o.name == name:
            return o.id


def populate_application_initial_data():
    for category_name in generate_data.get_categories():
        cat = create_database.Category(name = category_name)
        print cat
        session.add(cat)

    session.commit()

    q = session.query(create_database.Category)
    for cat in q.all():
        subcategories_names  = generate_data.get_sub_categories(cat.name)
        for subcategory_name in subcategories_names:
            sub_cat = create_database.SubCategory(name = subcategory_name, category_id = cat.id)
            session.add(sub_cat)

    for city_name in generate_data.CITIES_LIST:
        city = create_database.City(name=city_name)
        session.add(city)

    session.commit()


def populate_user_data():
    users = generate_data.get_list_of_users()

    for user in users:
        new_user = create_database.User(name=user['name'], email=user['email'], phone=user['phone'])
        session.add(new_user)

    session.commit()


def populate_ads_data():
    ads = generate_data.generate_random_ads(900)
    sub_categories = session.query(create_database.SubCategory).all()
    cities = session.query(create_database.City).all()
    users = session.query(create_database.User).all()

    for ad in ads:
        new_ad = create_database.Ad(sub_category_id = get_id(sub_categories, ad["sub_category"]),
                                    city_id=get_id(cities, ad["city"]),
                                    time_created=ad["date"],
                                    user_id=get_id(users, ad["user_name"]),
                                    contact_name=ad["user_name"],
                                    primary_contact=ad["contact_email"],
                                    contact_email=ad["contact_email"],
                                    contact_phone=ad["contact_phone"],
                                    text=ad["text"],
                                    price=ad["price"],
                                    currency="USD")
        session.add(new_ad)

    session.commit()


def populate_application_test_data():
    populate_user_data()
    populate_ads_data()


def drop_application_tables():
    tables_to_drop = [create_database.Ad, create_database.SubCategory, create_database.Category,
                      create_database.City, create_database.User]
    drop_tables(tables_to_drop)


def drop_tables(tables):
    for table in tables:
        table.__table__.drop(engine, checkfirst=True)


def repopulate_all_tables():
    drop_application_tables()
    create_database.create()
    populate_application_initial_data()
    populate_application_test_data()


if __name__ == "__main__":
     repopulate_all_tables()
