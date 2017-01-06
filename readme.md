###JSON endpopints###
There are three JSON endpoints:
1) /list_of_cities/JSON - returns JSON for all cities in the database (fields id and name)
2) /cities/city_id/ads/JSON -returns JSON for list of ads in <city_id> where city_id is an intgere
Example: /cities/2/ads/JSON
3)/ads/ad_id/JSON - returns JSON for a particular ad (identified by ad_id)
Example: ads/9/JSON

####CSRF Protection
All forms in the approcation inherit from FlaskForm of flask-wtf. Thus, CSRF protection is handled automatically:
https://flask-wtf.readthedocs.io/en/stable/form.html

####Creating database
Step1: To create an empty database, run module create_database.
Step 2:To populate it with fake ads and users for testing (for example, to evaluate how filtering and sorting works) run module populate_database.
populate_database will output lsit of cretted user accounts to console. 
It is not possible to log in to any of these accounts with option 
ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION set to False. However, if desired, enable option, reatart application and login into any of these accounts with password "s_classifieds" and e-mail that was output to console by populate_databse.
