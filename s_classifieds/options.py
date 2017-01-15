"""
This module contains configuration options settings
for s_catalog application
"""
import sys
import os
APPLICATION_FOLDER = os.path.dirname(os.path.realpath(__file__))
# constants, please do not modify
DATABASE_POSTGRES = 1
DATABASE_SQLITE = 2
LOCAL_HOST_VM = 1
LOCAL_HOST_WINDOWS = 2

# if set to LOCAL_HOST_WINDOWS  - will run on default host and port 5000
# if set to LOCAL_HOST_VM - we need to start application on port host='0.0.0.0' so that it is available outside
LOCAL_HOST = LOCAL_HOST_VM
if "win" in sys.platform.lower():
    LOCAL_HOST = LOCAL_HOST_WINDOWS
elif "linux" in sys.platform.lower():
    LOCAL_HOST = LOCAL_HOST_VM

# set to true to see various intermediate printouts for debugging purposes.
DEBUG_PRINT_ON = False

# if it is desired to use only third party user authentication (currently Google is supported)
# this option should be set to FALSE
ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION = True

# Should be set either to DATABASE_POSTGRES or DATABASE_SQLITE (which is currently a default database as well)
# Configure database urls as required.
DATABASE_TO_USE = DATABASE_POSTGRES


DATABASE_NAME = "s_classifieds"
POSTGRES_DEFAULT_URL = "postgresql://postgres:postgres@localhost/postgres"
if DATABASE_TO_USE == DATABASE_POSTGRES:
    DATABASE_URL = "postgresql://postgres:postgres@localhost/" + DATABASE_NAME
    DATABASE_URL_USER = "postgresql://catalog:catalog@localhost/" + DATABASE_NAME
else:
    if "win" in sys.platform.lower():
        DATABASE_URL = "sqlite:///" + DATABASE_NAME + ".db"
    elif "linux" in sys.platform.lower():
        DATABASE_URL = "sqlite:///" + os.path.join(APPLICATION_FOLDER, DATABASE_NAME)+".db"
    else:
        DATABASE_URL = "sqlite:////" + DATABASE_NAME + ".db"
    # production database is postgres, so no need to create special user account for sqlite
    DATABASE_URL_USER=DATABASE_URL

# Application configuration: defines cities (can be any city) and subcategories by category)
CITIES_LIST = ["Johannesburg", "Dongguan", "Tokyo", "Surat", "Yokohama", "Beijing"]
CATEGORIES_WITH_SUB_CATEGORIES = {
    "Motors": ["Cars", "Boats", "Motorcycles"],
    "Electronics": ["Computers", "Laptops", "Tablets"],
    "Rentals": ["Houses", "Apartments", "Rooms"],
    "Real estate for sale": ["Houses", "Apartments"]
}

#

