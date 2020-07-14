from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/compare", methods=['POST'])
def compare():
    info = request.form
    data['address1'] = info['address']
    data['zipcode1'] = info['zipcode']
    return render_template("compare.html", address = data['address1'], zipcode = data['zipcode1'])

@app.route("/results", methods=['POST'])
def results():
    info = request.form
    data['address2'] = info['address2']
    data['zipcode2'] = info['zipcode2']
    return render_template("results.html", address1 = data['address1'], zipcode1 = data['zipcode1'], address2 = data['address2'], zipcode2 = data['zipcode2'])

if __name__ == '__main__':
   app.run(debug = True)