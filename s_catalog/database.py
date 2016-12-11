
import generate_data
#real imports, to be kept
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import create_database
import datetime


engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")
create_database.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def set_user_authenticated_status(user, authenticated_status):
    user.authenticated = authenticated_status
    session.add(user)
    session.commit()

def get_user_ads(user):
    print "get_user_ads"
    print user
    if user is None:
        return None
    print user.id
    print user.email

    user_ads = session.query(create_database.Ad).filter(create_database.Ad.user_id == user.id).all()
    return user_ads


def get_user_by_unicode_id(user_id):
    user = session.query(create_database.User).filter(create_database.User.id == int(user_id)).first()
    return user


def validate_user_data_string(user_data_string):
    if user_data_string.strip()=="":
        return "Not set"
    return user_data_string.strip()


def get_user_from_email(email):
    user = session.query(create_database.User).filter(create_database.User.email == email).first()
    return user


def add_new_user(email, name, phone_number):
    print "add_new_user"
    print name
    new_user = create_database.User(name=validate_user_data_string(name),
                                    email=email,
                                    phone=validate_user_data_string(phone_number))
    session.add(new_user)
    session.commit()


def add_user_if_does_not_exist(email, name="not set", phone_number="not set"):
    print "add_user_if_does_not_exist"
    print name
    if not get_user_from_email(email):
        add_new_user(email, name, phone_number)


def get_ads_to_display(city_id=-1, sub_category_id=-1, created_within_days=0, sort_by="",
                       min_idx=0, number_of_records_to_include=10, debug_print = False, user_id = -1):

        if debug_print:
            print "get_ads_to_display inputs : city_id: {0}, sub_category_id: {1}," \
                  "created_within_days :{2},"\
                  " sort_by :{3}, min_idx: {4}, number_of_records_to_include {5}".format(city_id, sub_category_id,
                                                                                         created_within_days, sort_by,
                                                                                         min_idx,
                                                                                         number_of_records_to_include)
        filters = dict()
        if city_id > -1:
            filters["city_id"] = city_id

        if sub_category_id > -1:
            filters["sub_category_id"] = sub_category_id

        if user_id > -1:
            filters["user_id"] = user_id

        if created_within_days > 0:
            oldest_ad_date_to_include = datetime.datetime.now()
            oldest_ad_date_to_include += datetime.timedelta(days=-created_within_days)
            ads_within_date = session.query(create_database.Ad).filter(create_database.Ad.time_created >= oldest_ad_date_to_include)
        else:
            ads_within_date = session.query(create_database.Ad)

        ads_within_date = ads_within_date.filter_by(**filters)

        if sort_by=="price_desc":
            all_ads = ads_within_date.order_by(create_database.Ad.price_cents.desc())
        elif sort_by == "price_asc":
            all_ads = ads_within_date.order_by(create_database.Ad.price_cents.asc())
        elif sort_by == "date_asc":
            all_ads = ads_within_date.order_by(create_database.Ad.time_created.asc())
        elif sort_by == "date_desc":
            all_ads = ads_within_date.order_by(create_database.Ad.time_created.desc())
        else:
            all_ads = ads_within_date

        total_number_of_ads = all_ads.count()
        min_idx = max(min_idx, 0)

        if (min_idx+number_of_records_to_include) >= total_number_of_ads > 0:

            if total_number_of_ads % number_of_records_to_include > 0:
                min_idx = total_number_of_ads - total_number_of_ads % number_of_records_to_include
            else:
                min_idx = total_number_of_ads - number_of_records_to_include

        selected_ads = all_ads.offset(min_idx).limit(number_of_records_to_include)
        max_displayed_idx = min(total_number_of_ads,  min_idx + number_of_records_to_include)

        return selected_ads, total_number_of_ads, min_idx, max_displayed_idx


def get_cities():
    query_cities = session.query(create_database.City)
    all_cities = query_cities.all()
    for city in all_cities:
        print city.name
        print city.id
    return all_cities


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
        d_sub_category["name"] = str(sub_category.name)
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
    dict_ad["user"] = session.query(create_database.User).filter(create_database.User.id == int(ad.user_id)).one()
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
    dict_ad["formatted_date"] = ad.time_created.strftime("%d-%B-%Y at %H:%M")

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


def test_get_user_id_by_email():
    existing_user_email = "deanne.pittenger@gmail.com"
    non_existing_user_email = "does.notexits@nomail.com"
    print get_user_from_email(existing_user_email)
    print get_user_from_email(non_existing_user_email)

if __name__ == "__main__":
    #d = get_categories_with_subcategories()
    #print d
    #test_get_ad_by_id()
    test_get_user_id_by_email()