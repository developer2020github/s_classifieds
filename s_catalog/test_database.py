import database
import json


def test_get_ads_to_display():
    ads = database.get_ads_to_display(min_idx=5, number_of_records_to_include=2,
                                      sort_by_price="asc", created_within_days=10)
    for ad in ads:
        database.print_ad(ad)


def test_categories_with_subcategories():
    print json.dumps(database.get_categories_with_subcategories())

#test_get_ads_to_display()

test_categories_with_subcategories()