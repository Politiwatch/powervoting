import requests
import random
import os
import json
import re

with open("data/gen/elections.json", "r") as infile:
    ELECTIONS = json.load(infile)


def _electors(state, year):
    districts = set()
    for election in ELECTIONS:
        if election["office"] == "US House" and election["state"] == state and election["year"] == year:
            districts.add(election["district"])
    return len(districts) + 2


API_KEYS = os.getenv("API_KEYS").split(",")


def get_address_info(address, zipcode):
    print(zipcode)
    repdata = requests.get(
        "https://www.googleapis.com/civicinfo/v2/representatives",
        params={"address": f"{address} {zipcode}",
                "key": random.choice(API_KEYS)},
    ).json()

    if "normalizedInput" not in repdata:
        return None
        # we did this in WAMR, not sure if it's necessary here as well

    division_ids = "\n".join(repdata["divisions"].keys())

    state = re.search(r"^ocd-division\/country:us\/state:(..)$",
                      division_ids, flags=re.MULTILINE)
    if state:
        state = state.group(1)

    district = re.search(
        r"^ocd-division\/country:us\/state:..\/cd:(.+)$", division_ids, flags=re.MULTILINE)
    if district:
        district = district.group(1)

    return {
        "state": state,
        "district": district,
        "input": repdata["normalizedInput"]
    }


def get_elections(state, district):
    return list(filter(lambda k: k["state"] == state and k["district"] in [None, "statewide", district], ELECTIONS))


def _ppv(election):
    """Power per vote"""

    if election["office"] == "US President":
        return _electors(election["state"], election["year"]) / election["totalvotes"]
    else:
        return 1 / election["totalvotes"]


def _compound_score(closeness, ppv):
    return closeness * ppv * 1000000


def _scores(election) -> dict:
    votes = list(sorted([candidate["votes"]
                         for candidate in election["candidates"]], reverse=True)) + [0, 0]
    totalvotes = election['totalvotes']

    closeness = 1 - ((votes[0] - votes[1]) / totalvotes)
    ppv = _ppv(election)

    return {
        "closeness": closeness,
        "ppv": ppv,
        "compound": _compound_score(closeness, ppv)
    }


def _weighted_closeness_score(elections):
    total_weight = 0
    total_scores = 0

    for election in elections:
        weight = (election["year"] - 1975) ** 2
        total_weight += weight
        total_scores += _scores(election)["closeness"] * weight

    return total_scores / total_weight


def compute_scores(elections):
    senate = list(sorted(filter(
        lambda k: k["office"] == "US Senate", elections), key=lambda k: k["year"]))
    house = list(sorted(filter(
        lambda k: k["office"] == "US House", elections), key=lambda k: k["year"]))
    president = list(sorted(filter(
        lambda k: k["office"] == "US President", elections), key=lambda k: k["year"]))

    senate_score = _compound_score(
        _weighted_closeness_score(senate), _ppv(senate[-1]))
    house_score = _compound_score(
        _weighted_closeness_score(house), _ppv(house[-1]))
    president_score = _compound_score(
        _weighted_closeness_score(president), _ppv(president[-1]))

    senate_history = list(senate)
    for election in senate_history:
        election['scores'] = _scores(election)

    house_history = list(house)
    for election in house_history:
        election['scores'] = _scores(election)

    president_history = list(president)
    for election in president_history:
        election['scores'] = _scores(election)

    return {
        "senate": senate_score,
        "senate_history": senate_history,
        "house": house_score,
        "house_history": house_history,
        "president": president_score,
        "president_history": president_history,
        "total": (senate_score + house_score + president_score) / 3,
        "ppv_total": (_ppv(senate[-1]) + _ppv(house[-1]) + _ppv(president[-1])) / 3,
        "ppv_senate": _ppv(senate[-1]),
        "ppv_house": _ppv(house[-1]),
        "ppv_president": _ppv(president[-1]),
    }
