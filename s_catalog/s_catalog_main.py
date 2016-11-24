from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
import json

app = Flask(__name__)


@app.route('/')
def main_browse_page():
    categories_with_sub_categories = database.get_categories_with_subcategories()
    categories_json = json.dumps(categories_with_sub_categories)
    cities = database.get_cities()
    return render_template("index.html", categories=categories_with_sub_categories, categories_json=categories_json,
                           cities=cities)


@app.route('/update_ads_list')
def show_more_ads():
    #current_max_ad_idx = request.args.get('current_max_ad_idx', 0, type=int)
    r= request.args.get('show_next', False, type=bool)
    #query.(Model).filter(something).limit(5).all()

    min_idx = request.args.get('min_idx', 0, type=int)

    ads_html = list()
    # need to replace city name with city id, currently getting city name from fornt end

    selected_category_id = request.args.get('selected_category_id', -1, type=int)
    selected_sub_category_id = request.args.get('selected_sub_category_id', -1, type=int)
    select_ads_within_days = request.args.get('select_ads_within_days', -1, type=int)
    min_idx = request.args.get('min_idx', -1, type=int)
    sort_by = request.args.get('sort_by', "", type=str)
    print "request debug data"
    print selected_sub_category_id, select_ads_within_days, min_idx
    ads, total_number_of_ads, min_ad_idx_displayed, max_ad_idx_displayed =\
        database.get_ads_to_display(min_idx=min_idx,
                                    number_of_records_to_include=10,
                                    sub_category_id=selected_sub_category_id,
                                    created_within_days = select_ads_within_days,
                                    sort_by=sort_by)
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


@app.route("/signin")
def sign_in_page():
    return render_template("signin.html")

if __name__ == '__main__':
    app.debug = True
    app.secret_key = "secret key"
    app.run(port=5000)