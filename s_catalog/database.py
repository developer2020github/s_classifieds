import json
import generate_data
cities = generate_data.CITIES_LIST
'''this is a fake DB, used for now to drive the applciation.
real one is defined in create_database. 
'''

categories_with_sub_categories = generate_data.categories_with_sub_categories

def get_ad_by_id(ad_id):
    print(ad_id)
    return generate_data.get_ad_by_id(ad_id)

def get_total_number_of_ads():
    return 500


def get_categories():
    return generate_data.categories_with_sub_categories.keys()


def get_sub_categories(category):
    return generate_data.categories_with_sub_categories[category]


def get_categories_json():
    return json.dumps(categories_with_sub_categories)

if __name__ == "__main__":
    print get_categories()
    print get_sub_categories("electronics")

    print json.dumps(categories_with_sub_categories)