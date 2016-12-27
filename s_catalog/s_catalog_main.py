from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
from forms import LoginForm, RegisterForm
import database
import create_database
import json
import s_catalog_lib
from pprint import pprint

# references for login management
#https://flask-bcrypt.readthedocs.io/en/latest/
#https://flask-login.readthedocs.io/en/latest/

from apiclient import discovery
import httplib2
from oauth2client import client
import requests
import flask_login
import flask_bcrypt

bcrypt = flask_bcrypt.Bcrypt()

app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# path to the Web application client_secret_*.json file downloaded from the
# Google API Console: https://console.developers.google.com/apis/credentials
GOOGLE_SIGN_IN_CLIENT_SECRET_FILE = "client_secret.json"
CLIENT_ID = json.loads(
    open(GOOGLE_SIGN_IN_CLIENT_SECRET_FILE, 'r').read())['web']['client_id']

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return database.get_user_by_unicode_id(user_id)


def get_errors_in_registration_data(email, password, confirmed_password):
    """
    :param email: email of new user trying to register
    :param password:  his new password
    :param confirmed_password: confirmed value of password
    :return: empty string if everyting is all right and user can eb added. Error message to
            be displayed to user otherwise.
    """
    error_message = ""

    user = database.get_user_from_email(email)
    if user:
        error_message = "Error: user " + email + " already exists"
        return error_message

    if password != confirmed_password:
        error_message = "Error: please ensure passwords match"
        return error_message

    return error_message


def get_errors_in_login_data(email, password):
    """
    :param email: user email
    :param password: user password
    :return: error message and user object. If error message is emtpy, user can be logged in
    """
    error_message = ""

    user = database.get_user_from_email(email)
    if not user:
        error_message = "Error: user " + email + " does not exist"
        return error_message, None

    if not bcrypt.check_password_hash(user.password, password):
        error_message = "Error: incorrect password for user " + email
        return error_message, None

    return error_message, user


@app.route("/login_or_register", methods=["GET", "POST"])
def login_or_register():
    """combines all  login and registration methods"""

    simple_login_form = LoginForm()
    simple_register_form = RegisterForm()
    state = s_catalog_lib.get_random_string()
    login_session["state"] = state
    login_error_message = ""
    registration_error_message = ""
    #print_request_form(request)
    if request.method == 'POST':
        if request.form["action"] == "simple_login" and simple_login_form.validate_on_submit():
            print "processing login"
            login_error_message, user = get_errors_in_login_data(email=simple_login_form.email.data,
                                                                 password=simple_login_form.password.data)
            if login_error_message == "":
                    database.set_user_authenticated_status(user, True)
                    flask_login.login_user(user, remember=True)
                    #flash('Successfully logged in as ' + simple_login_form.email.data)
                    # no need to flash as user will be shown "logged in as" message any way
                    return redirect(url_for("index"))

        elif request.form["action"] == "simple_register" and simple_register_form.validate_on_submit():
            print "processing register"
            registration_error_message = get_errors_in_registration_data(email=simple_register_form.email.data,
                                                                 password=simple_register_form.password.data,
                                                                 confirmed_password=simple_register_form.confirm_password.data)

            if registration_error_message == "":
                database.add_new_user(name=simple_register_form.name.data,
                                      email=simple_register_form.email.data,
                                      phone_number=simple_register_form.phone.data,
                                      password=simple_register_form.password.data)

                flash('Successfully created new user ' + simple_register_form.email.data + ". Please log in.")

    return render_template("login_or_register.html", simple_login_form=simple_login_form,
                           simple_register_form=simple_register_form,
                           google_session_state = login_session["state"],
                           simple_login_error_message=login_error_message,
                           simple_register_error_message=registration_error_message,
                           page_info=get_page_info())


@app.route("/myads", methods=["GET"])
@flask_login.login_required
def my_ads():
    user = flask_login.current_user
    categories_with_sub_categories = database.get_categories_with_subcategories_for_user(user)
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_user_specific_cities(user)
    # print categories_json
    # print cities
    return render_template("myads.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities, page_info=get_page_info())


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("login_or_register"))


@app.route("/logout_simple", methods=["GET", "POST"])
@flask_login.login_required
def logout():
    """Logout the current user."""
    user = flask_login.current_user
    print "logout"
    print user
    print "user " + user.email + " successfully logged out "

    pprint(vars(user))
    database.set_user_authenticated_status(user, False)
    flask_login.logout_user()

    #if user was connected via google - we need to disconnect


    return redirect(url_for("index"))


def get_page_info():
    page_info = dict()
    page_info["user_logged_in"] = False
    page_info["left_text"] = "S-classifieds"
    page_info["right_text"] = ""
    if flask_login.current_user.is_authenticated:
        page_info["user_logged_in"] = True
        page_info["right_text"] = "Logged in as " + flask_login.current_user.email
    return page_info

@app.route('/')
def index():
    categories_with_sub_categories = database.get_categories_with_subcategories()
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_cities()
    #print categories_json
    #print cities
    return render_template("index.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities, page_info = get_page_info())


@app.route("/user_profile", methods=["GET", "POST"])
@flask_login.login_required
def user_profile():
    """
    Displays user profile data and handles two kinds of POST requests:
     1) update to user profile itself (i.e. if user wishes to change their name or phone number)
     2) application of these new settings to all user ads: user has a choice for specifying ad-
     specific contact phone and name. So they have to explicitly indicate if they want for their new defaults
     to be automatically applied to all of their ads.
    :return:
    """
    user = flask_login.current_user
    apply_new_profile_settings_class = "style='display: none';"
    if request.method == 'POST':
        if request.form["action"]=="update_profile":
            user.name = request.form["user_name"]
            user.phone = request.form["user_phone"]
            database.update_user(user)
            flask_login.current_user.name = user.name
            flask_login.current_user.phone = user.phone
            apply_new_profile_settings_class = ""
            flash("Your profile info has been updated. If you wish to apply your name and/"
                  " or phone number to be applied"
                  " to all your ads as contact info please click Apply new profile settings to all my ads button")
        elif request.form["action"]=="apply_new_profile_settings_to_user_ads":
            database.update_ads_with_new_user_info(user)
            apply_new_profile_settings_class = "style='display: none';"
            flash("All ads have been updated with new user data.")

    return render_template("user_profile.html",
                           user=user,
                           page_info=get_page_info(),
                           apply_new_profile_settings_class=apply_new_profile_settings_class)


@app.route("/delete_user_profile", methods=["GET", "POST"])
@flask_login.login_required
def delete_user_profile():
    """
    On get returns "delete profile" page to confirm if user really wants to delete their profile.
    On post deletes user profile. Note all user's ads will be automatically deleted as well because this
    is how database is setup (there is an automatic delete cascade for user->ad objects).
    :return:
    """
    user = flask_login.current_user

    if request.method == 'POST':
        user_email = user.email
        user_id = user.id
        database.set_user_authenticated_status(user, False)
        flask_login.logout_user()
        database.delete_user(database.get_user_by_unicode_id(user_id))

        flash("User account for " + user_email + " was deleted.")
        return redirect(url_for("index"))

    return render_template("delete_user_profile.html",
                           user=user,
                           page_info=get_page_info())


@app.route("/ads/<int:ad_id>/JSON")
def get_ad_json(ad_id):
    """
    Returns JSON for a single ad
    :param ad_id: itn id of the ad
    :return: JSON for the requested ad
    """
    ad  = database.get_ad_by_id(ad_id)
    if ad:
        return jsonify(database.ad_to_dict(ad, serialize=True))
    return jsonify({})


@app.route("/cities/<int:city_id>/ads/JSON")
def get_city_ads_json(city_id):
    """
    Returns JSON for all ads in a city (as per city_id)
    :param city_id: int id of the city
    :return: JSON for all ads in a city
    """
    ads = database.get_ads_by_city(city_id)
    list_of_ads_dictionaries = [database.ad_to_dict(ad, serialize=True) for ad in ads]
    return jsonify(list_of_ads_dictionaries)


@app.route("/list_of_cities/JSON")
def get_list_of_cities():
    """
    Returns JSON for list of cities with ids
    :return: JSON for all cities
    """
    cities = database.get_cities()
    list_of_city_dictionaries = [database.city_to_dict(city) for city in cities]
    return jsonify(list_of_city_dictionaries)


def get_search_filtering_parameters_from_request(input_request):
    """
    Helper function - will take request arguments coming from Search panel
    and convert them into a dictionary of arguments for
    database.get_ads_to_display function. The advantage is this can be used in more than one place
    :param input_request: request
    :return: dictionary of arguments for database.get_ads_to_display function
    """
    filtering_parameters = dict()

    filtering_parameters["city_id"] = input_request.args.get('selected_city_id', -1, type=int)
    filtering_parameters["category_id"] = input_request.args.get('selected_category_id', -1, type=int)
    filtering_parameters["number_of_records_to_include"] = 10
    filtering_parameters["sub_category_id"] = input_request.args.get('selected_sub_category_id', -1, type=int)
    filtering_parameters["created_within_days"] = input_request.args.get('select_ads_within_days', -1, type=int)
    filtering_parameters["min_idx"] = input_request.args.get('min_idx', -1, type=int)
    filtering_parameters["sort_by"] = input_request.args.get('sort_by', "", type=str)
    filtering_parameters["debug_print"] = True
    return filtering_parameters


@app.route('/update_my_ads_list')
def show_more_of_my_ads():
    user_id = flask_login.current_user.id

    ads_html = list()
    search_filtering_parameters = get_search_filtering_parameters_from_request(request)
    search_filtering_parameters["user_id"] = user_id

    ads, total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed =\
        database.get_ads_to_display(**search_filtering_parameters)

    if total_number_of_ads > 0:
        for ad in ads:
            ads_html.append(render_template("displayed_my_ad.html", ad=database.ad_to_dict(ad)))

    ads_data = dict()
    ads_data["ads_html"] = ads_html
    ads_data["total_number_of_ads"] = str(total_number_of_ads)
    ads_data["min_ad_idx_displayed"] = str(min_ad_idx_displayed)
    ads_data["max_ad_idx_displayed"] = str(max_ad_idx_displayed)

    return jsonify(ads_data)


@app.route('/update_ads_list')
def show_more_ads():

    ads_html = list()
    search_filtering_parameters = get_search_filtering_parameters_from_request(request)

    ads, total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed =\
        database.get_ads_to_display(**search_filtering_parameters)

    if total_number_of_ads > 0:
        for ad in ads:
            ads_html.append(render_template("displayed_ad.html", ad=database.ad_to_dict(ad)))

    print total_number_of_ads

    ads_data = dict()
    ads_data["ads_html"] = ads_html
    ads_data["total_number_of_ads"] = str(total_number_of_ads)
    ads_data["min_ad_idx_displayed"] = str(min_ad_idx_displayed)
    ads_data["max_ad_idx_displayed"] = str(max_ad_idx_displayed)

    return jsonify(ads_data)


@app.route("/ads/<int:ad_id>/current_ad")
def ad_page(ad_id):
    selected_ad = database.ad_to_dict(database.get_ad_by_id(ad_id))
    return render_template("ad.html", ad=selected_ad, page_info=get_page_info())


def print_request_form(input_request):
    """"
    Debug  helper function  - prints fields and values of request form
    :param input_request: request to print form from
    :return: none
    """
    f = input_request.form
    for key in f.keys():
        for value in f.getlist(key):
            print key, ":", value


def update_ad_from_form_info(ad, form):
    """
    Updates ad object from passed form and saves it to the database
    :param ad: ad to be updated
    :param form: forms to use as a source
    :return: none
    """
    ad.text = form["ad_text"]
    ad.price_cents = int((float(form["ad_price"]) * 100))
    ad.contact_email = form["contact_email"]
    # default to email for now
    ad.primary_contact  = ad.contact_email
    ad.contact_name = str(form["contact_name"])
    ad.contact_phone = str(form["contact_phone"])
    ad.city_id = int(form["select_city"])
    ad.sub_category_id = int(form["sub-category-selected"])
    ad.title = form["ad_title"]
    database.update_ad(ad)


@app.route("/new_ad",  methods=["GET", "POST"])
@flask_login.login_required
def new_ad():
    """
    Creates new ad from user inputs
    :return: on get add page; on post add  and redirects to my ads page ; on get  returns partly filled in template
    """

    if request.method == "POST":
        ad_new = create_database.Ad(user_id=flask_login.current_user.id)
        update_ad_from_form_info(ad_new, request.form)
        database.update_ad(ad_new)
        return redirect(url_for("my_ads"))

    user = database.get_user_by_unicode_id(flask_login.current_user.id)
    new_ad_template = database.get_ad_template(user)
    categories_with_sub_categories = database.get_categories_with_subcategories()
    cities = database.get_cities()
    categories_json = json.dumps(categories_with_sub_categories)

    selected_sub_categories = categories_with_sub_categories["Electronics"]["value"]
    return render_template("new_ad.html", ad=new_ad_template,
                           categories_json=categories_json,
                           categories=categories_with_sub_categories,
                           selected_sub_categories = selected_sub_categories,
                           cities=cities,
                           page_info = get_page_info())


@app.route("/ads/<int:ad_id>/delete_ad",  methods=["GET", "POST"])
@flask_login.login_required
def delete_ad(ad_id):
    """
    :param ad_id: ad to be deleted
    :return: on get add page; on post deletes ad and redirects to my ads page
    """
    selected_ad = database.get_ad_by_id(int(ad_id))

    if request.method == "POST":
        database.delete_ad(selected_ad)
        return redirect(url_for("my_ads"))

    ad_dict = database.ad_to_dict(selected_ad)

    return render_template("delete_ad.html", ad=ad_dict, page_info=get_page_info())


@app.route("/ads/<int:ad_id>/edit_ad",  methods=["GET", "POST"])
def edit_ad(ad_id):

    selected_ad = database.get_ad_by_id(int(ad_id))

    if request.method == "POST":
        update_ad_from_form_info(selected_ad, request.form)

    categories_with_sub_categories = database.get_categories_with_subcategories()

    cities = database.get_cities()
    categories_json = json.dumps(categories_with_sub_categories)
    ad_dict = database.ad_to_dict(selected_ad)
    selected_sub_categories = categories_with_sub_categories[ad_dict["category"]]["value"]
    return render_template("edit_my_ad.html", ad=ad_dict,
                           categories_json=categories_json,
                           categories=categories_with_sub_categories,
                           selected_sub_categories = selected_sub_categories,
                           cities=cities,
                           page_info=get_page_info())


#Initially, this was used as an URL , but do not need to be URL anymore
@app.route('/google_sign_out')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':

        # dels should probably be replaces with "pop" function
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def add_user_from_login_session(session):
    database.add_user_if_does_not_exist(session["email"], session["username"])


@app.route('/google_sign_in', methods=['POST'])
def gconnect():
    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = client.flow_from_clientsecrets(GOOGLE_SIGN_IN_CLIENT_SECRET_FILE, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except client.FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        add_user_from_login_session(login_session)
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    add_user_from_login_session(login_session)

    # now we can login user and actully disconnect from google, relying on Flask Login from now onwards

    user = database.get_user_from_email(data['email'])
    if user:
        print "flask login from Google"
        print user.email
        database.set_user_authenticated_status(user, True)
        flask_login.login_user(user, remember=True)
        gdisconnect()

        output = ''
        output += 'Welcome, '
        output += user.email
        output += '!'

    print "done!"
    return output



if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.secret_key = "secret key" #used to sign sessions, need to change it to a properly generated key
    app.run(port=5000)