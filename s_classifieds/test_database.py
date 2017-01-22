"""
This module contains various test and helper functions.
It does not have to be in production version of the application.
Function names are self-explanatory.
"""

import create_database
import database
import json
from flask import jsonify
import options
import os
import generate_data

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


def test_random_category_and_subcategory():
    sub_category = database.session.query(create_database.SubCategory).first()
    print sub_category.name
    category = database.session.query(create_database.Category).filter_by(id=sub_category.category_id).first()
    print category.name


def test_get_ad_by_id():
    for i in range(1, 10):
        database.print_ad (database.get_ad_by_id(i))


def test_get_user_id_by_email():
    existing_user_email = "deanne.pittenger@gmail.com"
    non_existing_user_email = "does.notexits@nomail.com"
    print database.get_user_from_email(existing_user_email)
    print database.get_user_from_email(non_existing_user_email)
