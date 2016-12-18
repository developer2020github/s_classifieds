from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
from forms import LoginForm
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

current_email = ""
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



@app.route("/login_simple", methods=["GET", "POST"])
def login_simple():
    """For GET requests, display the login form. For POSTS, login the current user
    by processing the form."""

    form = LoginForm()
    if form.validate_on_submit():
        print "processing post request"
        #return redirect("/")
        #pass

        user = database.get_user_from_email(form.email.data)
        if user:
            print  form.password.data
            print user.password
            if bcrypt.check_password_hash(user.password, form.password.data):
                database.set_user_authenticated_status(user, True)
                flask_login.login_user(user, remember=True)
                print "user " + user.email + " successfully logged in "
                return redirect("/")

    return render_template("login_simple.html", form=form)


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
                           cities=cities, user=user)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/login_simple")

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


    return redirect("/")


@app.route('/')
def main_browse_page():
    categories_with_sub_categories = database.get_categories_with_subcategories()
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_cities()
    #print categories_json
    #print cities
    return render_template("index.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities)


@app.route("/user_profile")
def user_profile_page():
    if "email" not in login_session:
        return redirect("/login")

    user = database.get_user_from_email(login_session["email"])
    if not user:
        return redirect("/login")

    return render_template("user_profile.html", message_text="Your profile: ", user_name=user.name,
                           user_email=user.email, user_phone = user.phone )


@app.route('/update_my_ads_list')
def show_more_of_my_ads():
    user_id = flask_login.current_user.id
    #current_max_ad_idx = request.args.get('current_max_ad_idx', 0, type=int)
    r= request.args.get('show_next', False, type=bool)
    #query.(Model).filter(something).limit(5).all()

    min_idx = request.args.get('min_idx', 0, type=int)

    ads_html = list()
    city_id = request.args.get('selected_city_id', -1, type=int)
    selected_category_id = request.args.get('selected_category_id', -1, type=int)
    selected_sub_category_id = request.args.get('selected_sub_category_id', -1, type=int)
    select_ads_within_days = request.args.get('select_ads_within_days', -1, type=int)
    min_idx = request.args.get('min_idx', -1, type=int)
    sort_by = request.args.get('sort_by', "", type=str)

    ads, total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed =\
        database.get_ads_to_display(city_id=city_id,
                                    min_idx=min_idx,
                                    number_of_records_to_include=10,
                                    sub_category_id=selected_sub_category_id,
                                    created_within_days = select_ads_within_days,
                                    sort_by=sort_by,
                                    user_id = user_id,
                                    debug_print=True)

    if total_number_of_ads>0:
        for ad in ads:
            ads_html.append(render_template("displayed_my_ad.html", ad=database.ad_to_dict(ad)))

    print total_number_of_ads

    ads_data = dict()
    ads_data["ads_html"] = ads_html
    ads_data["total_number_of_ads"] = str(total_number_of_ads)
    ads_data["min_ad_idx_displayed"] = str(min_ad_idx_displayed)
    ads_data["max_ad_idx_displayed"] = str(max_ad_idx_displayed)

    return jsonify(ads_data)

@app.route('/update_ads_list')
def show_more_ads():
    #current_max_ad_idx = request.args.get('current_max_ad_idx', 0, type=int)
    r= request.args.get('show_next', False, type=bool)
    #query.(Model).filter(something).limit(5).all()

    min_idx = request.args.get('min_idx', 0, type=int)

    ads_html = list()
    city_id = request.args.get('selected_city_id', -1, type=int)
    selected_category_id = request.args.get('selected_category_id', -1, type=int)
    selected_sub_category_id = request.args.get('selected_sub_category_id', -1, type=int)
    select_ads_within_days = request.args.get('select_ads_within_days', -1, type=int)
    min_idx = request.args.get('min_idx', -1, type=int)
    sort_by = request.args.get('sort_by', "", type=str)

    ads, total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed =\
        database.get_ads_to_display(city_id=city_id,
                                    min_idx=min_idx,
                                    number_of_records_to_include=10,
                                    sub_category_id=selected_sub_category_id,
                                    created_within_days = select_ads_within_days,
                                    sort_by=sort_by, debug_print=True)

    if total_number_of_ads>0:
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
    print selected_ad
    categories_with_sub_categories = database.get_categories_with_subcategories()
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_cities()
    return render_template("ad.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities, selected_ad=selected_ad)


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
    ad.primary_contact  = ad.contact_email
    ad.contact_name = str(form["contact_name"])
    ad.contact_phone = str(form["contact_phone"])
    ad.city_id = int(form["select_city"])
    ad.sub_category_id = int(form["sub-category-selected"])
    ad.title = form["ad_title"]
    database.update_ad(ad)


@app.route("/new_ad",  methods=["GET", "POST"])
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
                           cities=cities)





@app.route("/ads/<int:ad_id>/delete_ad",  methods=["GET", "POST"])
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

    return render_template("delete_ad.html", ad=ad_dict)


@app.route("/ads/<int:ad_id>/edit_ad",  methods=["GET", "POST"])
def edit_ad(ad_id):
    print "calling edit_ad"

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
                           cities=cities)


@app.route("/login")
def sign_in_page():
    state = s_catalog_lib.get_random_string()
    login_session["state"] = state
    print "current_email :"
    print current_email
    return render_template("login.html", session_state = login_session["state"], user_email=current_email)


#Initially, this was used as an URL as
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
        output += '<h1>Welcome, '
        output += user.name
        output += user.email
        output += '!</h1>'
        flash("you are now logged in as %s" % user.email)

    print "done!"
    return output



if __name__ == '__main__':
    app.debug = True
    app.secret_key = "secret key" #used to sign sessions, need to change it to a properly generated key
    app.run(port=5000)