from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask import session as login_session

import database
import json
import s_catalog_lib


from apiclient import discovery
import httplib2
from oauth2client import client
import requests

app = Flask(__name__)
current_email = ""
# path to the Web application client_secret_*.json file downloaded from the
# Google API Console: https://console.developers.google.com/apis/credentials
GOOGLE_SIGN_IN_CLIENT_SECRET_FILE = "client_secret.json"
CLIENT_ID = json.loads(
    open(GOOGLE_SIGN_IN_CLIENT_SECRET_FILE, 'r').read())['web']['client_id']

@app.route('/')
def main_browse_page():
    categories_with_sub_categories = database.get_categories_with_subcategories()
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_cities()
    print categories_json
    print cities
    return render_template("index.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities)


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

@app.route("/myads")
def my_ads_page():
    return render_template("myads.html")


@app.route("/login")
def sign_in_page():
    state = s_catalog_lib.get_random_string()
    login_session["state"] = state
    print "current_email :"
    print current_email
    return render_template("login.html", session_state = login_session["state"], user_email=current_email)


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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route("/google_sign_in_old", methods = ["POST"])
def google_sign_in():
    global current_email
    print "google_sign_in"
    # ref https://developers.google.com/identity/sign-in/web/server-side-flow


    # Exchange auth code for access token, refresh token, and ID token
    auth_code = request.data
    print "auth_code"
    print auth_code
    credentials = client.credentials_from_clientsecrets_and_code(
        GOOGLE_SIGN_IN_CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/plus.login', 'profile', 'email'],
        auth_code)

    # Call Google API
    '''
    http_auth = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http_auth)
    appfolder = drive_service.files().get(fileId='appfolder').execute()
    '''

    # Get profile info from ID token
    userid = credentials.id_token['sub']
    email = credentials.id_token['email']
    #name = credentials.id_token["name"]
    for k in credentials.id_token.keys():
        print k
    print userid
    #print name
    print email

    current_email = email
    return "ok"


if __name__ == '__main__':
    app.debug = True
    app.secret_key = "secret key"
    app.run(port=5000)