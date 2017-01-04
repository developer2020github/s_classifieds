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
DATABASE_TO_USE = DATABASE_SQLITE

if DATABASE_TO_USE == DATABASE_POSTGRES:
    CREATE_ENGINE_CMD_STRING = "postgresql://postgres:postgres@localhost/s_classifieds"
else:
    CREATE_ENGINE_CMD_STRING = "sqlite:///s_classifieds.db"

