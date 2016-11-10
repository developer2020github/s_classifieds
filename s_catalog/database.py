
import generate_data
#real imports, to be kept
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import create_database




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

def ad_to_dict(ad):
    dict_ad  = dict()
    dict_ad["city"] =""
    #STOPPED_HERE

def get_ad_by_id(ad_id):
    #print(ad_id)
    #return generate_data.get_ad_by_id(ad_id)
    return session.query(create_database.Ad).filter(create_database.Ad.id == ad_id).first()

def get_total_number_of_ads():
    return 500


def print_ad(ad):
    print ""
    print ad.id
    print ad.user.name
    print ad.title
    print ad.text


def test_get_ad_by_id():
    for i in range(1, 10):
        print_ad (get_ad_by_id(i))


'''
'''
if __name__ == "__main__":
    #d = get_categories_with_subcategories()
    #print d
    test_get_ad_by_id()