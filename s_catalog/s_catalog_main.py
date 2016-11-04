from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database

app = Flask(__name__)


@app.route('/')
def main_browse_page():
    categories = database.categories_with_sub_categories
    return render_template("index.html", categories=categories, categories_json=database.get_categories_json(),
                           cities=database.cities, number_of_ads_selected="500")


@app.route("/ads/<int:ad_id>/current_ad")
def ad_page(ad_id):
    selected_ad = database.get_ad_by_id(ad_id)
    print selected_ad
    categories = database.categories_with_sub_categories
    return render_template("ad.html", categories=categories, categories_json=database.get_categories_json(),
                           cities=database.cities, selected_ad=selected_ad)

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