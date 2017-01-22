"""
Main module of s-classifieds application.
S-classifieds is a demo/personal project of a simple classifieds board.

This module handles:
#User management: login/logout/registration/settings for flask-login
     Supports following options:
     1) google - based OAuth2 authentication and authorization
     2) as an option (can be enabled/disabled with ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION flag)
        - email/password based registration and authentication and authorization. Uses bcrypt

     Once user is authenticated by any method, authorization for views and other relevant logic is
     handled by flask-login.

#main  view - main page of the application
    Supports filtering of ads by location, category, sub-category and date posted
    and sorting by date and price

#User profile view:
     user can update name and contact phone
     If desired, user can apply their updated profile settings to all their ads.
     User can also delete their profile. This action will delete all  their ads as well.

#User's  ads views and handling (CRUD)
    Users can view, update, and delete their ads.
    Filtering by location, category, sub-category and date posted is supported as well as sorting
    by date posted and price.

#JSON end points
    3 JSON end points are supported:
     1) individual ad by id
     2) list of cities (locations) with their ids
     3) list of ads in a particular location (by location id)


CSRF protection handling
    Implemented via using flask_wtf which chave it enabled by default.
    Some forms are custom-built but still utilize flask_wtf csrf token field.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
from forms import LoginForm, RegisterForm, UpdateUserInfoForm
import database
import create_database
import populate_database
import json
import lib
import os


import httplib2
from oauth2client import client
import requests
import flask_login
import flask_bcrypt
import options
from flask_wtf import FlaskForm
from pprint import pprint

# required for optional email-based login and registration.
bcrypt = flask_bcrypt.Bcrypt()
app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# path to the Web application client_secret_*.json file downloaded from the
# Google API Console: https://console.developers.google.com/apis/credentials
GOOGLE_SIGN_IN_CLIENT_SECRET_FILE = os.path.join(options.APPLICATION_FOLDER, "client_secret.json")
CLIENT_ID = json.loads(
    open(GOOGLE_SIGN_IN_CLIENT_SECRET_FILE, 'r').read())['web']['client_id']

# -------------------------------------------------------------------------
# #####User management: login/logout/registration/settings for flask-login
# #####and user authorization helper functions
# -------------------------------------------------------------------------


def user_is_authorized_to_update_item(user_id_to_check):
    """
    Function checks if user in current session is allowed to update an item associated with a user_id_to_check
    :param user_id_to_check: id associated with the item (for example, user_id field of an ad)
    :return: True if user should be allowed to update the item, False otherwise
    """

    if "authorized_user_id" in login_session:
        if int(user_id_to_check) == int(login_session["authorized_user_id"]):
            lib.debug_print("authorized")
            return True
    lib.debug_print("not authorized")
    return False


def authorize_user(user_id):
    """
    Adds user_id to login_session to be used by user_is_authorized_to_update_item for authorization checks
    :param user_id: user id
    :return: None
    """
    lib.debug_print("authorizing user")
    lib.debug_print(user_id)
    login_session["authorized_user_id"] = user_id


def de_authorize_current_user():
    """
    Cleans up login session user_id field
    :return: None
    """
    if "authorized_user_id" in login_session:
        login_session["authorized_user_id"] = None


@login_manager.user_loader
def user_loader(user_id):
    """
    requred for flask-login
    Given *user_id*, return the associated User object.
    :param unicode user_id: user_id (email) user to retrieve
    """
    return database.get_user_by_unicode_id(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    """
    :return: redirects to login page if user is trying to access a page that requires log in.
    """
    return redirect(url_for("login_or_register"))


def get_errors_in_registration_data(email, password, confirmed_password):
    """
    :param email: email of new user trying to register
    :param password:  his new password
    :param confirmed_password: confirmed value of password
    :return: empty string if everything is all right and user can be added. Error message to
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
    """
    combines all  login and registration methods:
    1) google (third-party)
    2) (optional) email - password combination: available when  ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION
    option is set to True
    """

    simple_login_form = LoginForm()
    simple_register_form = RegisterForm()
    state = lib.get_random_string()
    login_session["state"] = state
    login_error_message = ""
    registration_error_message = ""
    if options.ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION:
        if request.method == 'POST':
            if request.form["action"] == "simple_login" and simple_login_form.validate_on_submit():
                lib.debug_print("processing login")

                login_error_message, user = get_errors_in_login_data(email=simple_login_form.email.data,
                                                                     password=simple_login_form.password.data)
                if login_error_message == "":
                        database.set_user_authenticated_status(user, True)
                        flask_login.login_user(user, remember=True)
                        authorize_user(user.id)

                        # no need to flash as user will be shown "logged in as" message any way
                        return redirect(url_for("index"))

            elif request.form["action"] == "simple_register" and simple_register_form.validate_on_submit():
                lib.debug_print("processing register")
                registration_error_message = \
                    get_errors_in_registration_data(email=simple_register_form.email.data,
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
                           google_session_state=login_session["state"],
                           simple_login_error_message=login_error_message,
                           simple_register_error_message=registration_error_message,
                           page_info=get_page_info(),
                           ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION=
                           options.ENABLE_EMAIL_AND_PASSWORD_LOGIN_AND_REGISTRATION)


def response_to_string(response_input):
    """
    Converts http response into string: gdisonnec returns normal response, but application uses it as a flash message,
    so need to conveert to simple string.
    :param response_input: response
    :return: response message string
    """
    response_str = ""

    def strip_quotes(input_str):
        lib.debug_print("strip_quotes")
        lib.debug_print(input_str)
        if input_str.startswith('"') and input_str.endswith('"'):
            input_str = input_str[1:-1]

        return input_str

    for s in response_input.response:
        response_str += " " + strip_quotes(s)

    lib.debug_print(response_str)
    return response_str


@app.route("/logout_simple")
@flask_login.login_required
def logout():
    """
    Logs out the current user.
    """

    user = flask_login.current_user
    logout_msg = "user " + user.email + " successfully logged out "

    # pprint(vars(user))
    database.set_user_authenticated_status(user, False)
    flask_login.logout_user()
    de_authorize_current_user()

    # if user was connected via google - we need to disconnect
    if 'access_token' in login_session:
        gdi_disconnect_response = gdisconnect()
        lib.debug_print("gdi_disconnect_response")
        logout_msg=response_to_string(gdi_disconnect_response)

    flash(logout_msg)
    return redirect(url_for("index"))


@app.route('/google_sign_out')
def gdisconnect():
    """
    disconnect current user from Google account
    :return: status response
    """
    access_token = login_session['access_token']
    lib.debug_print('In gdisconnect access token is' + str(access_token))
    lib.debug_print('User name is: ')
    lib.debug_print(login_session['username'])
    if access_token is None:
        lib.debug_print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    lib.debug_print('result is ')
    lib.debug_print (result)
    if result['status'] == '200':

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
    lib.debug_print("gconnect")
    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        lib.debug_print("request.args.get('state') != login_session['state']")
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
        lib.debug_print("except client.FlowExchangeError")
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
        lib.debug_print("result.get('error') is not None:")
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        lib.debug_print("result['user_id'] != gplus_id:")
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        lib.debug_print("result['issued_to'] != CLIENT_ID:")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        add_user_from_login_session(login_session)
        lib.debug_print("stored_credentials is not None and gplus_id == stored_gplus_id:")
        return response

    # Store the access token in the session for later use.
    lib.debug_print(" login_session['access_token'] = credentials.access_token")
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    lib.debug_print("assign user data")
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    add_user_from_login_session(login_session)

    # now we can login user and actully disconnect from google, relying on Flask Login from now onwards

    user = database.get_user_from_email(data['email'])
    output = ''
    if user:
        lib.debug_print("flask login from Google")
        lib.debug_print(user.email)
        database.set_user_authenticated_status(user, True)
        flask_login.login_user(user, remember=True)
        authorize_user(user.id)
        print flask_login.current_user.is_authenticated

        # theoretically can disconnect here as flask login will take care of the rest
        #gdisconnect()

        output += 'Welcome, '
        output += user.email
        output += '!'

    lib.debug_print("done!")
    return output


# -------------------------------------------------------------------------
# #####main  view and ad view
# -------------------------------------------------------------------------
def get_page_info():
    """
    :return: dictionary of standard page info items for page nav bar
    """
    page_info = dict()
    page_info["user_logged_in"] = False
    page_info["left_text"] = "S-classifieds"
    page_info["right_text"] = ""
    lib.debug_print("get_page_info")
    lib.debug_print(flask_login.current_user.get_id())
    # first need to check if user is set to AnonymousUserMixin object
    if flask_login.current_user.get_id():
        if flask_login.current_user.is_authenticated():
            page_info["user_logged_in"] = True
            page_info["right_text"] = "Logged in as " + flask_login.current_user.email
    return page_info


@app.route('/')
def index():
    """
    :return: main page of the application
    """
    print_current_session()
    categories_with_sub_categories = database.get_categories_with_subcategories()
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_cities()
    return render_template("index.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities, page_info=get_page_info())


@app.route('/about')
def about():
    """
    :return: about page
    """
    return render_template("about.html",  page_info=get_page_info())


@app.route('/update_ads_list')
def show_more_ads():
    """
    :return: rendered list of ads
    """
    return show_ads(template_name="displayed_ad.html")


@app.route("/ads/<int:ad_id>/current_ad")
def ad_page(ad_id):
    """

    :param ad_id: id of the ad
    :return: rendered view for an ad
    """
    selected_ad = database.ad_to_dict(database.get_ad_by_id(ad_id))
    return render_template("ad.html", ad=selected_ad, page_info=get_page_info())

# -------------------------------------------------------------------------
# #####User profile view
# -------------------------------------------------------------------------


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
    update_user_info_form = UpdateUserInfoForm(obj=user)
    apply_new_profile_settings_to_user_ads_form = FlaskForm()
    if request.method == 'POST':
        if not user_is_authorized_to_update_item(user.id):
            flash("You are not authorized to update this page")
            return redirect(url_for("index"))
        if request.form["action"] == "update_profile":
            if update_user_info_form.validate_on_submit():
                user.name = update_user_info_form.name.data
                user.phone = update_user_info_form.phone.data
                database.update_user(user)
                flask_login.current_user.name = user.name
                flask_login.current_user.phone = user.phone
                apply_new_profile_settings_class = ""

                flash("Your profile info has been updated. If you wish to apply your name and/"
                       "or phone number to be applied"
                       "to all your ads as contact info please click "
                       "Apply new profile settings to all my ads button")

        elif request.form["action"] == "apply_new_profile_settings_to_user_ads":
            if apply_new_profile_settings_to_user_ads_form.validate_on_submit():
                database.update_ads_with_new_user_info(user)
                apply_new_profile_settings_class = "style='display: none';"
                # this post request is empty, so we need to force main form to show user name and phone
                update_user_info_form.name.data = user.name
                update_user_info_form.phone.data = user.phone

                flash("All ads have been updated with new user data.")

    return render_template("user_profile.html",
                           user=user,
                           update_user_info_form=update_user_info_form,
                           apply_new_profile_settings_to_user_ads_form=apply_new_profile_settings_to_user_ads_form,
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
    delete_user_profile_form = FlaskForm()
    if request.method == 'POST' and delete_user_profile_form.validate_on_submit():
        if not user_is_authorized_to_update_item(user.id):
            flash("You are not authorized to update this page")
            return redirect(url_for("index"))

        user_email = user.email
        user_id = user.id
        database.set_user_authenticated_status(user, False)
        flask_login.logout_user()
        database.delete_user(database.get_user_by_unicode_id(user_id))

        flash("User account for " + user_email + "and all ads for this account were deleted.")
        return redirect(url_for("index"))

    return render_template("delete_user_profile.html",
                           user=user,
                           delete_user_profile_form=delete_user_profile_form,
                           page_info=get_page_info())


# -------------------------------------------------------------------------
# #####User's  ads views and handling (CRUD)
# -------------------------------------------------------------------------


@app.route("/myads", methods=["GET"])
@flask_login.login_required
def my_ads():
    """
    :return: user's ads page
    """
    user = flask_login.current_user
    categories_with_sub_categories = database.get_categories_with_subcategories_for_user(user)
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_user_specific_cities(user)
    return render_template("myads.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities, page_info=get_page_info())


@app.route('/update_my_ads_list')
def show_more_of_my_ads():
    """
    :return: rendered list of user-specific ads
    """
    user_id = flask_login.current_user.id
    return show_ads(template_name="displayed_my_ad.html", user_id=user_id)


@app.route("/new_ad",  methods=["GET", "POST"])
@flask_login.login_required
def new_ad():
    """
    Creates new ad from user inputs
    :return: on get add page; on post add  and redirects to my ads page ; on get  returns partly filled in template
    """

    # using FlaskForm for csrf protection, rest is custom - built
    new_ad_form = FlaskForm()
    if request.method == "POST" and new_ad_form.validate_on_submit():
        ad_new = create_database.Ad(user_id=flask_login.current_user.id)
        update_ad_from_form_info(ad_new, request.form)
        database.update_ad(ad_new)
        flash("New ad was successfully added")
        return redirect(url_for("my_ads"))

    user = database.get_user_by_unicode_id(flask_login.current_user.id)
    new_ad_template = database.get_ad_template(user, initialize_city=True, initialize_category_and_subcategory=True)
    categories_with_sub_categories = database.get_categories_with_subcategories()
    cities = database.get_cities()
    categories_json = json.dumps(categories_with_sub_categories)

    selected_sub_categories = categories_with_sub_categories[new_ad_template["category"]]["value"]

    return render_template("new_ad.html", ad=new_ad_template,
                           categories_json=categories_json,
                           categories=categories_with_sub_categories,
                           new_ad_form=new_ad_form,
                           selected_sub_categories=selected_sub_categories,
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

    if not user_is_authorized_to_update_item(selected_ad.user_id):
        flash("You are not authorized to update this page")
        return redirect(url_for("login"))

    # Use FlaskForm for csrf protection
    delete_ad_form = FlaskForm()
    if request.method == "POST" and delete_ad_form.validate_on_submit():
        ad_deleted_msg = "Your ad #" + str(selected_ad.id) + " was deleted"
        database.delete_ad(selected_ad)
        flash(ad_deleted_msg)
        return redirect(url_for("my_ads"))

    ad_dict = database.ad_to_dict(selected_ad)

    return render_template("delete_ad.html", ad=ad_dict, page_info=get_page_info(), delete_ad_form=delete_ad_form)


@app.route("/ads/<int:ad_id>/edit_ad",  methods=["GET", "POST"])
@flask_login.login_required
def edit_ad(ad_id):
    """
    Updates specific ad with user edited information.
    :param ad_id: id of the ad
    :return: either current ad info (on GET) or updated ad (on POST)
    """
    selected_ad = database.get_ad_by_id(int(ad_id))
    if not user_is_authorized_to_update_item(selected_ad.user_id):
        flash("You are not authorized to update this page")
        return redirect(url_for("index"))

    edit_ad_form = FlaskForm()
    if request.method == "POST" and edit_ad_form.validate_on_submit():
        # using FlaskForm only for csrf protection in this case, rest is custom-built
        update_ad_from_form_info(selected_ad, request.form)
        flash("Ad was updated")

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
                           edit_ad_form=edit_ad_form,
                           page_info=get_page_info())

# -------------------------------------------------------------------------
# #####JSON end points
# -------------------------------------------------------------------------
@app.route("/ads/<int:ad_id>/JSON")
def get_ad_json(ad_id):
    """
    Returns JSON for a single ad
    :param ad_id: itn id of the ad
    :return: JSON for the requested ad
    """
    ad = database.get_ad_by_id(ad_id)
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

# -------------------------------------------------------------------------
# #####common helper functions
# -------------------------------------------------------------------------


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
    filtering_parameters["debug_print"] = False
    return filtering_parameters


def show_ads(template_name, user_id=None):
    """
    get ads_data data structure to be displayed in the list of ads.
    Filtering parameters are extracted from request.
    :param user_id: if None - ignored. Otherwise, user id will be used to filter in only user-specific ads
    :param template_name: template to use to render an ad
    :return: rendered list of ads
    """
    ads_html = list()
    search_filtering_parameters = get_search_filtering_parameters_from_request(request)
    if user_id:
        search_filtering_parameters["user_id"] = user_id

    ads, total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed = \
        database.get_ads_to_display(**search_filtering_parameters)

    if total_number_of_ads > 0:
        for ad in ads:
            ads_html.append(render_template(template_name, ad=database.ad_to_dict(ad)))

    ads_data = dict()
    ads_data["ads_html"] = ads_html
    ads_data["total_number_of_ads"] = str(total_number_of_ads)
    ads_data["min_ad_idx_displayed"] = str(min_ad_idx_displayed)
    ads_data["max_ad_idx_displayed"] = str(max_ad_idx_displayed)

    return jsonify(ads_data)


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
    ad.primary_contact = ad.contact_email
    ad.contact_name = str(form["contact_name"])
    ad.contact_phone = str(form["contact_phone"])
    ad.city_id = int(form["select_city"])
    ad.sub_category_id = int(form["sub-category-selected"])
    ad.title = form["ad_title"]
    database.update_ad(ad)


def print_current_session(printing_on = options.DEBUG_PRINT_ON):
    """
    Debug helper function - prints all fields of current login_session
    :return: None
    """
    if not printing_on:
        return

    print "current login_session: "
    for i in login_session:
        print str(i) + " : " + str(login_session[i])


def run_heroku():
    """
    Runs application in deployed configuration on Heroku
    :return:
    """
    app.secret_key = "secret key"  # used to sign sessions, need to change it to a properly generated key in production

    create_database.connect_to_db_and_populate_initial_data()
    populate_database.repopulate_all_tables()
    #app.debug = True
    #app.run(port=5000)
    app.run(host='0.0.0.0')


def run_debug():
    """
    Runs application with debug on, normally to be used for local debugging and development
    :return:
    """
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # debug option to be sure updates are applied right away
    app.debug = True
    app.secret_key = "secret key"  # used to sign sessions, need to change it to a properly generated key in production

    if options.LOCAL_HOST == options.LOCAL_HOST_WINDOWS:
        app.run(port=5000)
    elif options.LOCAL_HOST == options.LOCAL_HOST_VM:
        app.run(host='0.0.0.0', port=5000)
    else:
        app.run(port=5000)

if __name__ == '__main__':
    if options.DEPLOYED_TO_HEROKU:
        run_heroku()
    else:
        run_debug()

else:
    app.secret_key = "secret key"
