import create_database
import database
import json


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

#test_empty_query()

print str(455).decode("utf-8")



