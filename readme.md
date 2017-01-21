##S-classifieds
[S-classifieds](http://35.166.234.43/)
is a personal/demo project: a simple classifieds board.
It allows to post textual ads, filter them by location, category, subcategory and date posted
and sort by date and price.
Users can do same kind of filtering and searching on their ads and perform CRUD operations on ads.
They can also update and delete their profile information.

##Technologies used
1. JavaScript, HTML, CSS: jQuery, Bootstrap
2. Python: Flask, SQLAlchemy
3. Database: PostgreSQL

##Installing and running project
######1. Ensure you have latest version of Python 2.7.* installed. Note application was dveloped with Python 2.7.8 but should work with later versions of Python 2.7.
######2. Install Python packages as specified in the file requirements.txt (Refer to https://pip.pypa.io/en/stable/reference/pip_freeze/ for installation procedure). There are multiple packages to install, so you may want to use a Virtual Environment (http://docs.python-guide.org/en/latest/dev/virtualenvs/).
######3. Application supports two options for databases: postgresql and sqlite. Default configuration is sqlite. For testing and evaluation purposes there is no need to install postgresql.
######4. Create database (see "Creating database" section)
######5. Run module main.py
######6. In a browser, navigate to http://localhost:5000/
#####Creating database
Step 1: To create an empty database, run module create_database. This is sufficient to run the application.
Step 2: To populate it with fake ads and users for testing (for example, to evaluate how filtering and sorting works) run module populate_database.
populate_database will output list of created user accounts(emails) to console.
It is not possible to log in to any of these accounts with option
ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION set to False. However, if desired, enable option (refer to module options.py), restart application and login into any of these accounts with password "s_classifieds" and e-mail that was output to console by populate_database.


#####API endpoints###
There are three JSON endpoints:
1) /list_of_cities/JSON - returns JSON for all cities in the database (fields id and name)
2) /cities/city_id/ads/JSON -returns JSON for list of ads in <city_id> where city_id is an integer
Example: /cities/2/ads/JSON
3)/ads/ad_id/JSON - returns JSON for a particular ad (identified by ad_id)
Example: ads/9/JSON
Note to test ads-related end points database needs to be populated. 

#####CRUD
Users can perform CRUD operations on their ads and update or delete their profiles.
All ads, categories, sub-categories and locations are read from the database. 
Please note that selecting a category in search panel will populate sub-categories list with
relevant items (i.e. only sub-categories that belong to selected category).

Ads can be filtered by location, category, subcategory and date posted. This functionality is provided for main page and "My ads" page.

#####Authentication and authorization.
Application supports oauth2 with Google. For it to work file client_secret.json needs to be populated with proper application credentials from Google.

There is also e-mail/password based registration and log in system, using bcrypt for password management.

Authorization is implemented for ad and profile update and delete functionality, so that users can only change database records they own.



#####CSRF Protection
All forms in the application inherit from FlaskForm of flask-wtf. Thus, CSRF protection is handled automatically:
https://flask-wtf.readthedocs.io/en/stable/form.html










