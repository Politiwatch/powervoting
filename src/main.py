#!/usr/bin/env python3

from flask import Flask, render_template, redirect, url_for, request
import api

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", locations=[])

@app.route("/results")
def results():
    addresses = list(zip(request.args.getlist("address"), request.args.getlist("zipcode")))
    locations = [api.get_address_info(address, zipcode) for (address, zipcode) in addresses]
    elections = [api.get_elections(loc["state"], loc["district"]) for loc in locations]
    scores = [api.compute_scores(elecs) for elecs in elections]
    info = list(zip(locations, scores))
    #everything is included in 'info', since it zips locations (which includes input) and scores (which includes history)
    print(info)
    return render_template("results.html", locations=locations, scores=scores, info=info)

if __name__ == '__main__':
   app.run(debug = True)