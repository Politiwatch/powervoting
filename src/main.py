from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

data = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/results")
def results():
    print(request.args)
    return render_template("results.html")

if __name__ == '__main__':
   app.run(debug = True)