from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
import alchemy_db

app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "postresql://postgres:postgres@localhost/s_classifieds"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/s_classifieds"
db = alchemy_db.create_db(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return "<User %r>" % self.username
'''
# temporarily commented out  - getting DB to work
@app.route('/')
def main_browse_page():
    categories = database.categories_with_sub_categories
    return render_template("index.html", categories=categories, categories_json=database.get_categories_json(),
                           cities=database.cities, number_of_ads_selected="500")
'''
#temporary example method - working on DB integration
@app.route('/')
def index():
    myUser = User.query.all()
    return render_template("add_user.html", myUser=myUser)

#temporary example method - working on DB integration
@app.route("/post_user", methods=["POST"])
def post_user():
    #create user objaect based on the data entered into form and submitted as POST
    user = User(request.form["username"], request.form["email"])
    #add it to database
    db.session.add(user)
    #and save changes to daatabase
    db.session.commit()
    # now need to return something - view that will be displayed after post request is done
    # pass a view function name
    return redirect(url_for("index"))



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