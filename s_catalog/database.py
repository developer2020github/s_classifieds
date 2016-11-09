
import generate_data
#real imports, to be kept
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import create_database
import json


cities = generate_data.CITIES_LIST
'''this is a fake DB, used for now to drive the applciation.
to be reaplced with real database interface code
real one is defined in create_database. 
'''

categories_with_sub_categories = generate_data.categories_with_sub_categories

engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")
create_database.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def get_cities():
    query_cities = session.query(create_database.City)
    return query_cities.all()

def get_categories_with_subcategories():
    #returns dictionary of lists of subcategories by category name
    query_sub_categories = session.query(create_database.SubCategory)
    query_categories = session.query(create_database.Category)
    cats_with_sub_cats = dict()
    for category in query_categories.all():
        cats_with_sub_cats[category.name] = list()
        print category.name

    for sub_category in query_sub_categories.all():
        cats_with_sub_cats[sub_category.category.name].append(sub_category.name)

    return cats_with_sub_cats


def get_ad_by_id(ad_id):
    print(ad_id)
    return generate_data.get_ad_by_id(ad_id)

def get_total_number_of_ads():
    return 500


def get_categories():
    return generate_data.categories_with_sub_categories.keys()


def get_sub_categories(category):
    return generate_data.categories_with_sub_categories[category]




'''
'''
if __name__ == "__main__":
    d = get_categories_with_subcategories()
    print d