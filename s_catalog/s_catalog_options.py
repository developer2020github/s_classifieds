"""
This module contains configuration options settings
for s_catalog application
"""
# constants
DATABASE_POSTGRES = 1
DATABASE_SQLITE = 2

# if it is desired to use only third party user authentication (currently Google is supported)
# this option should be set to FALSE
ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION = True

# should be set either to DATABASE_POSTGRES or DATABASE_SQLITE (which is currently a default database as well)
# confgure database urls as required.
DATABASE_TO_USE = DATABASE_SQLITE

DATABASE_NAME = "s_classifieds"
POSTGRES_DEFAULT_URL = "postgresql://postgres:postgres@localhost/postgres"
if DATABASE_TO_USE == DATABASE_POSTGRES:
    DATABASE_URL = "postgresql://postgres:postgres@localhost/" + DATABASE_NAME
else:
    DATABASE_URL = "sqlite:///" + DATABASE_NAME + ".db"

# application configuration: defines cities (can be any city) and subcategories by category)
CITIES_LIST = ["Johannesburg", "Dongguan", "Tokyo", "Surat", "Yokohama", "Beijing"]
CATEGORIES_WITH_SUB_CATEGORIES = {
    "Motors": ["Cars", "Boats", "Motorcycles"],
    "Electronics": ["Computers", "Laptops", "Tablets"],
    "Rentals": ["Houses", "Apartments", "Rooms"],
    "Real estate for sale": ["Houses", "Apartments"]
}