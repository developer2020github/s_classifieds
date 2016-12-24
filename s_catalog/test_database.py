import create_database
import database
import json
from flask import jsonify


def test_jsonify_ads():
    city_id = 2
    ads = database.get_ads_by_city(city_id)
    print ads
    list_of_ads = [database.ad_to_dict(ad) for ad in ads]
    print list_of_ads
    print jsonify(list_of_ads)


def test_get_ads_to_display():
    ads = database.get_ads_to_display(min_idx=5, number_of_records_to_include=2,
                                      sort_by_price="asc", created_within_days=10)
    for ad in ads:
        database.print_ad(ad)


def test_categories_with_subcategories():
    print json.dumps(database.get_categories_with_subcategories())


def test_one():
    print "test_one"
    ads_html = list()
    ads, total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed = \
        database.get_ads_to_display(city_id=1,
                                    min_idx=0,
                                    number_of_records_to_include=10,
                                    sub_category_id=9,
                                    created_within_days=-1,
                                    sort_by="", debug_print=True)
    print total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed
    print ads
    if total_number_of_ads>0:
        for ad in ads:
            ads_html.append(database.ad_to_dict(ad))
#test_#test_categories_with_subcategories()


def test_empty_query():
    ads =  database.session.query(create_database.Ad).filter(create_database.Ad.user_id == 1234546)
    print ads.all()
    print ads.count()


def test_query():
    ads =  database.session.query(create_database.Ad).filter(create_database.Ad.user_id == 9)
    print ads.all()
    print ads.count()


def test_filtering_by_user():
    print "testing get_user_specific_sub_categories and get_user_specific_categories"
    users = database.session.query(create_database.User).all()
    test_outcome = "all tests passed"

    for user in users:
        ads = database.get_user_ads(user)

        sub_categories_to_check = []
        categories_to_check = []
        for ad in ads:
            #print ad.sub_category_id
            sub_categories_to_check.append(ad.sub_category_id)
            sub_category = database.session.query(create_database.SubCategory).get(ad.sub_category_id)
            category = database.session.query(create_database.Category).get(sub_category.category_id).id
            categories_to_check.append(category)

        sub_categories_to_check = list(set(sub_categories_to_check))
        categories_to_check = list(set(categories_to_check))
        user_ads_sub_categories = database.get_user_specific_sub_categories(user)
        user_ads_categories = database.get_user_specific_categories(user)

        if sub_categories_to_check.sort()==user_ads_sub_categories.sort() and \
           categories_to_check.sort() == user_ads_categories.sort():
            print "test ok"
        else:
            print "test failed"
            test_outcome = "some test(s) failed"

        print sub_categories_to_check
        print user_ads_sub_categories

        print categories_to_check
        print user_ads_categories
        print ""
        print ""
    print "tested get_user_specific_sub_categories and get_user_specific_categories:"
    print test_outcome


def print_all_ads():
    ads = database.session.query(create_database.Ad).all()
    for ad in ads:
        database.print_ad(ad)


print_all_ads()

