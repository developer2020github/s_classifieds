from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)


@app.route('/')
def mainBrowsePage():
    return render_template("index.html")

if __name__ == '__main__':
    app.debug = True
    app.secret_key = "secret key"
    app.run(port=5000)