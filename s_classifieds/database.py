"""
This  module provides an extra layer between database interface and the application; it encapsulates
database-related operations to improve modularity, keep non-view related code out of the view module
and to make unit testing easier.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import create_database
import datetime
import options
import flask_bcrypt

engine = create_engine(options.DATABASE_URL_USER)
create_database.Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def set_user_authenticated_status(user, authenticated_status):
    """
    :param user: user object
    :param authenticated_status: boolean indicating if user is  authenticated; will be written into database
    :return: None
    """
    user.authenticated = authenticated_status
    session.add(user)
    session.commit()


def get_user_ads(user):
    """
    Wrapper around database query
    :param user: user object
    :return: list of user's ads or none
    """
    if user is None:
        return None

    user_ads = session.query(create_database.Ad).filter(create_database.Ad.user_id == user.id).all()
    if user_ads.count > 0:
        return user_ads
    return None


def delete_ad(ad):
    """
    Deletes ad from the database
    :param ad: ad object
    :return: None
    """
    session.delete(ad)
    session.commit()


def update_user(user):
    """
    Updates user object in the database
    :param user:user object
    :return: None
    """
    session.add(user)
    session.commit()


def update_ad(ad):
    """
    Updates ad object in the database
    :param ad: ad object
    :return: None
    """
    session.add(ad)
    session.commit()


def update_ads_with_new_user_info(user):
    """
    Updates all ads by current user with new contact information.
    This scenario is possible if a user updated their profile with
    new contact phone or name and now want to apply this information to all of their ads.
    :param user: user object
    :return: none
    """
    ads = get_user_ads(user)
    if ads:
        for ad in ads:
            ad.contact_name = user.name
            ad.contact_phone = user.phone
            session.add(ad)

    session.commit()


def delete_user(user):
    """
    Deletes user from database
    :param user: user object
    :return: None
    """
    session.delete(user)
    session.commit()


def get_user_by_unicode_id(user_id):
    """
    Helper function for flask-login
    :param user_id: user id (can be unicode string)
    :return: user object or none
    """
    user = session.query(create_database.User).filter(create_database.User.id == int(user_id)).first()
    return user


def validate_user_data_string(user_data_string):
    """
    Helper function - checks a data string (example: phone number submitted by user) and
    sets it to default value if it is empty.
    :param user_data_string: input string
    :return: output
    """
    if user_data_string.strip() == "":
        return "Not set"
    return user_data_string.strip()


def get_user_from_email(email):
    """
    Returns user identified by their primary email
    :param email: email
    :return: user object
    """
    user = session.query(create_database.User).filter(create_database.User.email == email).first()
    return user


def get_hashed_password(password):
    """
    :param password: string (password)
    :return: empty string if password is empty or bcrypt - generated hash of the password
    """
    if password == "":
        return password

    bcrypt = flask_bcrypt.Bcrypt()
    return bcrypt.generate_password_hash(password)


def add_new_user(email, name, phone_number, password=""):
    """
    Creates user object from provided data and adds it to the database.
    :param email: user email
    :param name: user name
    :param phone_number: user phone
    :param password: optional password
    :return: None
    """
    new_user = create_database.User(name=validate_user_data_string(name),
                                    email=email,
                                    phone=validate_user_data_string(phone_number),
                                    password=get_hashed_password(password))
    session.add(new_user)
    session.commit()


def add_user_if_does_not_exist(email, name="not set", phone_number="not set"):
    """
    Checks if user exists (via e-mail) and if not - adds user object to database
    :param email: user email
    :param name: optional user name
    :param phone_number: optional phone number
    :return:
    """
    if not get_user_from_email(email):
        add_new_user(email, name, phone_number)


def get_user_specific_categories(user, sub_categories=None):
    """
    :param user: user - user object
    :param sub_categories: - optional list of sub-category ids (in case it is already known)
    :return: list of  categories in which current user has ads
    """
    categories = []
    if not sub_categories:
        sub_categories = get_user_specific_sub_categories(user)
    if sub_categories:
        for sub_category in sub_categories:
            category = session.query(create_database.SubCategory).filter_by(id = sub_category).first().category_id
            categories.append(category)

        categories = list(set(categories))
    return categories


def get_user_specific_cities(user):
    """
    :param user: user object
    :return: list of city objects in which user has ads
    """

    cities_to_include = []
    ads = get_user_ads(user)
    if ads:
        city_ids_to_include = [ad.city_id for ad in ads]
        city_ids_to_include = list(set(city_ids_to_include))
        all_cities = get_cities()
        cities_to_include = [city for city in all_cities if city.id in city_ids_to_include]

    return cities_to_include


def get_ads_by_city(city_id):
    """
    :param city_id: integer id of the city
    :return: list of all ads in this city
    """
    ads = session.query(create_database.Ad).filter_by(city_id=city_id).all()
    return ads


def get_user_specific_sub_categories(user):
    """
    :param user: user object
    :return: list of sub-categories ids in which current user has ads
    """
    sub_categories = []
    ads = get_user_ads(user)
    if ads:
        sub_categories = [ad.sub_category_id for ad in ads]
        sub_categories = list(set(sub_categories))
    return sub_categories


def get_ads_to_display(city_id=-1, category_id=-1, sub_category_id=-1, created_within_days=0, sort_by="",
                       min_idx=0, number_of_records_to_include=10, debug_print=False, user_id=-1):
        """
        Main filtering function - will return paged (by number_of_records_to_include) list of ads
        that meet filtering parameters. Can also be sorted.

        :param city_id: filtering parameter - id of the city. If default (-1) - not taken into account.
        :param category_id: filtering parameter. If default (-1) - not taken into account.
        :param sub_category_id: filtering parameter - sub - category id. If default(-1) - not taken into account.
        :param created_within_days: filtering parameter: number of days within which ad was created.
                                    If default (0) - not taken into account.
        :param sort_by: sorting command string. Can be
                        price_desc
                        price_asc
                        date_desc
                        date_asc
                        If default ("") - output will not be sorted
        :param min_idx: Minimum index of the ad to include. I.e., if it is set 10 - ads from 10 to 10+
                        number_of_records_to_include will be returned
        :param number_of_records_to_include: number of records to include in returned list
        :param debug_print: if set to True, filtering and sorting input parameters will be printed
        :param user_id: filtering parameter - id of the user to include. If default (-1) - will be ignored
        :return: selected_ads - list of ads to be displayed (i.e. limited by  min_idx and number_of_records_to_include)
                 total_number_of_ads - total number of ads filtered in (i.e. not length of selected_ads
                                       but number of all ads that meet filtering criteria)
                 min_idx - updated min_idx (client does not have to know if min idx they request actually exceeds
                          total number number of ads)
                 max_displayed_idx - maximum index of displayed ad in returned list (example: if we are displaying ads by
                                    10 and total number is 25 - max index connot be 10 since last sub-list will contain
                                    only 5 ads)

        """

        if debug_print:
            print "get_ads_to_display inputs : city_id: {0}, sub_category_id: {1}," \
                  "created_within_days :{2},"\
                  " sort_by :{3}, min_idx: {4}, number_of_records_to_include {5}"\
                  "category_id: {6}, user_id :{7} ".format(city_id, sub_category_id,
                                            created_within_days, sort_by,
                                            min_idx,
                                            number_of_records_to_include,
                                            category_id,
                                            user_id)
        filters = dict()
        subcategories_ids_to_filter_by_category=[]
        # there are two possible scenarios for filtering by category/sub-category:
        # a) user selects subcategory. In this case we do not need to check category
        # because all ads in requested sub-category will belong to correct category:
        # it is impossible to have incorrect subcategory->category linkage.
        # b) user selects category without going into subcategories.
        #    Database schema uses sub-categories as foreign keys in ads table. Thus,
        #    we'll need to create a list of applicable sub-categories and filter by that list.

        if city_id > -1:
            filters["city_id"] = city_id

        if sub_category_id > -1:
            filters["sub_category_id"] = sub_category_id
        elif category_id > -1:
            list_of_subcategories_to_filter_by_category = \
                session.query(create_database.SubCategory).filter_by(category_id=category_id).all()
            subcategories_ids_to_filter_by_category = \
                [sub_cat.id for sub_cat in list_of_subcategories_to_filter_by_category]

        if user_id > -1:
            filters["user_id"] = user_id

        if created_within_days > 0:
            oldest_ad_date_to_include = datetime.datetime.now()
            oldest_ad_date_to_include += datetime.timedelta(days=-created_within_days)
            ads_within_date = session.query(create_database.Ad).filter(create_database.Ad.time_created >= oldest_ad_date_to_include)
        else:
            ads_within_date = session.query(create_database.Ad)

        ads_within_date = ads_within_date.filter_by(**filters)

        if subcategories_ids_to_filter_by_category:
            all_ads = \
                ads_within_date.filter(create_database.Ad.sub_category_id.in_(subcategories_ids_to_filter_by_category))
        else:
            all_ads = ads_within_date

        if sort_by == "price_desc":
            all_ads = all_ads.order_by(create_database.Ad.price_cents.desc())
        elif sort_by == "price_asc":
            all_ads = all_ads.order_by(create_database.Ad.price_cents.asc())
        elif sort_by == "date_asc":
            all_ads = all_ads.order_by(create_database.Ad.time_created.asc())
        elif sort_by == "date_desc":
            all_ads = all_ads.order_by(create_database.Ad.time_created.desc())

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


def city_to_dict(city):
    """
    :param city: city object
    :return: city objects converted to dictionary
    """
    d_city = dict()
    d_city["id"] = str(city.id)
    d_city["name"] = city.name
    return d_city


def get_cities():
    """
    :return: list of all cities in the database
    """
    query_cities = session.query(create_database.City)
    all_cities = query_cities.all()
    return all_cities


def get_categories_with_subcategories_for_user(user):
    """
    Same as get_categories_with_subcategories, but filters in categories and sub categories only for a particular user
    :param user: user object
    :return: same data structure as return of get_categories_with_subcategories
    """
    sub_categories_to_include = get_user_specific_sub_categories(user)
    categories_to_include = get_user_specific_categories(user, sub_categories_to_include)
    cats_with_sub_cats = get_categories_with_subcategories(categories_to_include=categories_to_include,
                                                           sub_categories_to_include=sub_categories_to_include)
    return cats_with_sub_cats


def get_categories_with_subcategories(categories_to_include = None, sub_categories_to_include = None):
    """
    :input: categories_to_include - optional list of categories to filter in
            sub_categories_to_include - optionals list of sub-categories to include
            If optional inputs are empty, all categories and sub_categories will be included.
            No checks whatsoever are done on the inputs - i.e. client s/w unig should
            supply a correct combination of categories and sub-categories to include.

    :return:  dictionary of lists of subcategories by category name.
      Data is structured in following way:
      a dictionary by names of categories
      each item in the dictionary above is a dictionary itself and represents category and associated sub-categories.
      It contains following fields:
      "id" - id of the category converted to string
       "value" - list of items, each representing a sub-category
        In turn, each item in the list is a dictionary, representing a subcategory.
        The subcategory dictionaries contain following fields:
        "id" - id of the sub-category converted to string
        "name" - name of the sub-category
    """
    query_sub_categories = session.query(create_database.SubCategory)
    query_categories = session.query(create_database.Category)
    cats_with_sub_cats = dict()

    def category_or_subcategory_should_be_included(item_id, items_to_include):
        if not items_to_include:
            return True

        if item_id in items_to_include:
            return True

        return False

    for category in query_categories.all():
        if category_or_subcategory_should_be_included(category.id, categories_to_include):
            cats_with_sub_cats[category.name] = dict()
            cats_with_sub_cats[category.name]["id"] = str(category.id)
            cats_with_sub_cats[category.name]["value"] = list()

    for sub_category in query_sub_categories.all():
        if category_or_subcategory_should_be_included(sub_category.id, sub_categories_to_include):
            d_sub_category = dict()
            d_sub_category["id"] = str(sub_category.id)
            d_sub_category["name"] = str(sub_category.name)
            cats_with_sub_cats[sub_category.category.name]["value"].append(d_sub_category)

    return cats_with_sub_cats


def get_ad_template(user, initialize_city=False, initialize_category_and_subcategory = False):
    """
    To be  used for new ads: wherever possible, populates ad dictionary fields from user object.
    The idea is to make same similar templates work for edit and new ad pages.
    :param user: user object to be used in ad initialization
    :param initialize_city: if this parameter is True, ad city will be initialized
    to a random city from the list of cities
    :param initialize_category_and_subcategory: if this parameter is True, ad category and subcategory will
    be initialized to some random values
    :return: ad template as a dictionary (similar to ad_to_dict)
    """
    dict_ad = dict()
    dict_ad["user"] = user.id

    dict_ad["city"] = ""
    dict_ad["city_id"] = ""

    if initialize_city:
        city = session.query(create_database.City).first()
        dict_ad["city"] = city.name
        dict_ad["city_id"] = str(city.id)

    dict_ad["category"] = ""
    dict_ad["category_id"] = ""

    dict_ad["sub_category"] = ""
    dict_ad["sub_category_id"] = ""

    if initialize_category_and_subcategory:
        sub_category = session.query(create_database.SubCategory).first()
        dict_ad["category"] = sub_category.category.name
        dict_ad["category_id"] = str(sub_category.category_id)

        dict_ad["sub_category"] = sub_category.name
        dict_ad["sub_category_id"] = str(sub_category.id)

    dict_ad["ad_title"] = "Enter ad title"
    dict_ad["text"] = "Enter description"

    dict_ad["contact_phone"] = user.phone
    dict_ad["contact_email"] = user.email
    dict_ad["contact_name"] = user.name

    dict_ad["date"] = ""
    dict_ad["price"] = "0.0"
    dict_ad["id"] = ""
    dict_ad["formatted_date"] = ""

    return dict_ad


def ad_to_dict(ad, serialize=False):
    """
    converts ad object into dictionary of strings:
    some of the fields (such as category) do not need to be stored in
    database, and others (like sub-category) are represntedby ID, not strings
    which is not convenient for displaying them. Since number of
    ads displayed at any time is small, and all data is already attached
    to ad object via backref it makes no sense to run SQL joins.
    Also can be used to serialize ads.
    :param ad: Ad object
    :param  serialize:  if set to True will include only serialized fields
    :return: dictionary of string fields
    """

    dict_ad = dict()
    if not serialize:
        dict_ad["user"] = session.query(create_database.User).filter(create_database.User.id == int(ad.user_id)).one()

    dict_ad["city"] = ad.city.name
    dict_ad["city_id"] = str(ad.city_id)

    dict_ad["category"] = ad.sub_category.category.name
    dict_ad["category_id"] = str(ad.sub_category.category_id)

    dict_ad["sub_category"] = ad.sub_category.name
    dict_ad["sub_category_id"] = str(ad.sub_category.id)

    dict_ad["ad_title"] = ad.title
    dict_ad["text"] = ad.text

    dict_ad["contact_phone"] = ad.contact_phone
    dict_ad["contact_email"] = ad.contact_email
    dict_ad["contact_name"] = ad.contact_name

    dict_ad["date"] = ad.time_created
    dict_ad["price"] = str(ad.price_cents/100.0)
    dict_ad["id"] = str(ad.id)
    dict_ad["formatted_date"] = ad.time_created.strftime("%d-%b-%Y at %H:%M")

    return dict_ad


def get_ad_by_id(ad_id):
    """

    :param ad_id: id of the ad
    :return: ad from id
    """
    return session.query(create_database.Ad).filter(create_database.Ad.id == ad_id).first()


def print_ad(ad):
    """
    helper function - to be used for debugging and testing: prints ad object to console.
    :param ad: ad object
    :return: none
    """
    print ""
    print ad.id
    print ad.time_created
    print ad.user.name
    print ad.city.name
    print "sub_category:"
    print ad.sub_category_id
    print "price: " + str(ad.price_cents/100.0)
    print ad.title
    print ad.text

if __name__ == "__main__":
    pass
