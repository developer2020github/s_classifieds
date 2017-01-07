##S-classifieds
S-classifieds is a personal/demo project: a simple classifieds board.
It allows to post textual ads, filter them by location, category, subcategory and date posted 
and sort by date and price.
Users can do same kind of filtering and searching on their ads and perform CRUD operations on ads. 
They can also update and delete their profile information.
Application also meets requirements of Udacity Full Stack Nano - degree project 5.

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

####Meeting Udacity project requirements.
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
Application supports oauth2 with Google.

Authorization is implemented with flask-login: all views that are user-specific will be shown only 
to logged in user. Advantage of using flask-login vs new implementation is that it is a proven
solution and actually requires less code.

Login button is shown to new users, and sign out button - after user has logged in.

Additionally, there is an optional e-mail/password based registration and log in system, using bcrypt for password management: as I explained in the forum link below, I intend to use this project in my portfolio and I think this is a good option to have. Since project requirements do not state it can be allowed, I made it optional. It is disabled for project submission (options.py, option ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION ). Please refer to https://discussions.udacity.com/t/combining-flask-login-with-oauth2/202877 - added an option flag as discussed.

Since this option is implemented not instead but in addition to third-party option, and is disabled in submitted version of the project I believe project meets the requirements.

#####CSRF Protection
All forms in the application inherit from FlaskForm of flask-wtf. Thus, CSRF protection is handled automatically:
https://flask-wtf.readthedocs.io/en/stable/form.html
The advantage of using flask-wtf is it is a proven solution and requires notably less code and testing.










