

categories_with_sub_categories = {
    "motors": ["cars", "boats", "motorcycles"],
    "electronics": ["computers", "laptops", "tablets"],
    "rentals": ["houses", "apartments", "rooms"],
    "real estate for sale": ["houses", "apartments"]
}


def get_categories():
    return categories_with_sub_categories.keys()


def get_sub_categories(category):
    return categories_with_sub_categories[category]

if __name__ == "__main__":
    print get_categories()
    print get_sub_categories("electronics")