import database


def test_get_ads_to_display():
    ads = database.get_ads_to_display(min_idx=5, number_of_records_to_include=5)
    for ad in ads:
        database.print_ad(ad)

test_get_ads_to_display()