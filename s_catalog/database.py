import json

cities = ["Johannesburg", "Dongguan", "Tokyo", "Surat", "Yokohama", "Beijing"]

categories_with_sub_categories = {
    "Motors": ["cars", "boats", "motorcycles"],
    "Electronics": ["computers", "laptops", "tablets"],
    "rentals": ["houses", "apartments", "rooms"],
    "real estate for sale": ["houses", "apartments"]
}


def get_categories():
    return categories_with_sub_categories.keys()


def get_sub_categories(category):
    return categories_with_sub_categories[category]


def get_categories_json():
    return json.dumps(categories_with_sub_categories)

if __name__ == "__main__":
    print get_categories()
    print get_sub_categories("electronics")

    print json.dumps(categories_with_sub_categories)