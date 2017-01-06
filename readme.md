##S-classifieds 
S-classifieds is a personal/demo project: a simple classifieds board.
It allows to post textual ads, filter them by location, category, subcategory and date posted 
and sort by date and price. 
Users can do same kind of filtering and searching on their ads and perform CRUD operations on ads. 
They can also update and delete their profile information. 
Application also meets requirements of Udacity Full Stack Nano - degree project 5.

##Installing and running project 
######1. Ensure you have latest version of Python 2.7 installed
######2. Install Python packages as specified in the file requirements.txt (Refer to https://pip.pypa.io/en/stable/reference/pip_freeze/ for detailes). There are multiple packages to install, so you may want to use a Virtual Environment (http://docs.python-guide.org/en/latest/dev/virtualenvs/)
######3. Application supports two options for databases: postgresql and sqlite. Default configuration is sqlite. For testing and evaluation purposes there is no need to install postgresql.
######4. Create database (see "Creating database" section)
######5. Run module main.py 
######6. In a browser, navigate to http://localhost:5000/
#####Creating database
Step 1: To create an empty database, run module create_database. This is sufficient to run the application.
Step 2:To populate it with fake ads and users for testing (for example, to evaluate how filtering and sorting works) run module populate_database.
populate_database will output list of created user accounts(emails) to console. 
It is not possible to log in to any of these accounts with option 
ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION set to False. However, if desired, enable option (refer to module options.py), restart application and login into any of these accounts with password "s_classifieds" and e-mail that was output to console by populate_database.

####Meeting Udacity project requirements.
#####User account management. 
Application supports oauth2 with Google. 

Additionally, there is an optional e-mail/password based registration and log in system, using bcrypt for password management. 
Since project requirements do not state it can be allowed, it is disabled for project submission (module options.py).
Please refer to https://discussions.udacity.com/t/combining-flask-login-with-oauth2/202877 - added a flag as discussed. As a side note, I think project still should be acceptable even with option enabled: it is implemented not instead of oauth2, but as an addition I decided to have as an extra feature: user should not be needing Google or Facebook account to use classifieds board.
#####Session management and authorization
Session management and authorization is done with flask-login.
####CSRF Protection
All forms in the application inherit from FlaskForm of flask-wtf. Thus, CSRF protection is handled automatically:
https://flask-wtf.readthedocs.io/en/stable/form.html
#####Access to items by category
Ads can be filtered by location, category, subcategory and date posted. This functionality is provided for main page and "My ads" page.

#####CRUD
Users can perform CRUD operations on their ads and update or delete their profiles.

#####JSON endpopints###
There are three JSON endpoints:
1) /list_of_cities/JSON - returns JSON for all cities in the database (fields id and name)
2) /cities/city_id/ads/JSON -returns JSON for list of ads in <city_id> where city_id is an integer
Example: /cities/2/ads/JSON
3)/ads/ad_id/JSON - returns JSON for a particular ad (identified by ad_id)
Example: ads/9/JSON




