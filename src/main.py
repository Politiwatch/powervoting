#!/usr/bin/env python3

from flask import Flask, render_template, redirect, url_for, request
import api

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/results")
def results():
    addresses = list(zip(request.args.getlist("address"), request.args.getlist("zipcode")))
    print(addresses)
    address_info = [api.get_address_info(address, zipcode) for (address, zipcode) in addresses]
    return render_template("results.html")

if __name__ == '__main__':
   app.run(debug = True)