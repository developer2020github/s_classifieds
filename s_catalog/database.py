
import generate_data
#real imports, to be kept
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import create_database
import datetime



'''this is a fake DB, used for now to drive the applciation.
to be reaplced with real database interface code
real one is defined in create_database. 
'''


engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")
create_database.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def get_ads_to_display(city_id=-1, sub_category_id=-1, created_within_days=0, sort_by_date="", sort_by_price="",
                       min_idx=0, number_of_records_to_include=10):
        filters = dict()
        if city_id > -1:
            filters["city_id"] = city_id

        if sub_category_id > -1:
            filters["sub_category_id"] = sub_category_id

        if created_within_days> 0:
            oldest_ad_date_to_include = datetime.datetime.now()
            oldest_ad_date_to_include += datetime.timedelta(days=-created_within_days)
            ads_within_date = session.query(create_database.Ad).filter(create_database.Ad.time_created >= oldest_ad_date_to_include)
        else:
            ads_within_date = session.query(create_database.Ad)

        ads_within_date = ads_within_date.filter_by(**filters)

        if sort_by_price == "desc":
            all_ads = ads_within_date.order_by(create_database.Ad.price_cents.desc())
        elif sort_by_price == "asc":
            all_ads = ads_within_date.order_by(create_database.Ad.price_cents.asc())
        elif sort_by_price == "desc":
            all_ads = ads_within_date.order_by(create_database.Ad.price_cents.desc())
        elif sort_by_date == "asc":
            print " sort asc"
            all_ads = ads_within_date.order_by(create_database.Ad.time_created.asc())
        elif sort_by_date == "desc":
            all_ads = ads_within_date.order_by(create_database.Ad.time_created.desc())

        total_number_of_ads = all_ads.count()
        selected_ads = all_ads.offset(min_idx).limit(number_of_records_to_include)

        return selected_ads, total_number_of_ads


def get_cities():
    query_cities = session.query(create_database.City)
    return query_cities.all()


def get_categories_with_subcategories():
    #returns dictionary of lists of subcategories by category name
    query_sub_categories = session.query(create_database.SubCategory)
    query_categories = session.query(create_database.Category)
    cats_with_sub_cats = dict()
    for category in query_categories.all():
        cats_with_sub_cats[category.name] = dict()
        cats_with_sub_cats[category.name]["id"] = str(category.id)
        cats_with_sub_cats[category.name]["value"] = list()
        #print category.name

    for sub_category in query_sub_categories.all():
        d_sub_category = dict()
        d_sub_category["id"] = str(sub_category.id)
        d_sub_category["name"]= str(sub_category.name)
        cats_with_sub_cats[sub_category.category.name]["value"].append(d_sub_category)

    return cats_with_sub_cats


def ad_to_dict(ad):
    '''
    converts ad object into dictionary of strings:
    some of the fields (such as category) do not need to be stored in
    database, and others (like sub-category) are represntedby ID, not strings
    which is not convenient for displaying them. Since number of
    ads displayed at any time is small, and all data is already attached
    to ad object via backref it makes no sense to run SQL joins.
    :param ad: Ad object
    :return: dictionayr of string fileds
    '''

    dict_ad = dict()
    dict_ad["city"] = ad.city.name
    dict_ad["category"] = ad.sub_category.category.name
    dict_ad["sub_category"] = ad.sub_category.name
    dict_ad["ad_title"] = ad.title
    dict_ad["text"] = ad.text
    dict_ad["contact_phone"] = ad.contact_phone
    dict_ad["contact_email"] = ad.contact_email
    dict_ad["contact_name"] = ad.contact_name
    dict_ad["date"] = ad.time_created
    dict_ad["price"] = str(ad.price_cents/100.0)
    dict_ad["id"] = str(ad.id)

    return dict_ad

def get_ad_by_id(ad_id):
    #print(ad_id)
    #return generate_data.get_ad_by_id(ad_id)
    return session.query(create_database.Ad).filter(create_database.Ad.id == ad_id).first()

def get_total_number_of_ads():
    return 500


def print_ad(ad):
    print ""
    print ad.id
    print ad.time_created
    print ad.user.name
    print ad.city.name
    print "price: " + str(ad.price_cents/100.0)
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