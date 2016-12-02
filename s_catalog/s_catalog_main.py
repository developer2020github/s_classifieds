from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as login_session

import database
import json
import s_catalog_lib


from apiclient import discovery
import httplib2
from oauth2client import client

app = Flask(__name__)
current_email = ""
# path to the Web application client_secret_*.json file downloaded from the
# Google API Console: https://console.developers.google.com/apis/credentials
GOOGLE_SIGN_IN_CLIENT_SECRET_FILE = "client_secret.json"

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


@app.route("/google_sign_in", methods = ["POST"])
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