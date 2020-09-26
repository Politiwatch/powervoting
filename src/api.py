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


def get_all_scores():
    """Not frequently used"""
    scores = {}
    for state in set([election["state"] for election in ELECTIONS]):
        for district in set([election["district"] for election in filter(lambda k: k["state"] == state, ELECTIONS)]):
            elections = get_elections(state, district)
            try:
                scores[(state, district)] = compute_scores(elections)
            except Exception as e:
                print(f"{state}, {district} failed: {e}")
    return scores


def get_elections(state, district):
    return list(filter(lambda k: k["state"] == state and k["district"] in [None, "statewide", district, "0"], ELECTIONS))


def _vs(election):
    """Vote slice"""

    if election["office"] == "US President":
        return _electors(election["state"], election["year"]) / max(1, election["totalvotes"])
    else:
        return 1 / max(1, election["totalvotes"])

def _current_vs(elections):
    processed_elections = sorted(filter(lambda k: k["totalvotes"] > 1, elections), key=lambda k: k["year"])
    return (sum([_vs(elec) for elec in processed_elections[-2:]]) / len(processed_elections[-2:]))

def _compound_score(closeness, vs):
    return closeness * vs * 10000000


def _scores(election) -> dict:
    votes = list(sorted([candidate["votes"]
                         for candidate in election["candidates"]], reverse=True)) + [0, 0]
    totalvotes = election['totalvotes']

    closeness = 1 - ((votes[0] - votes[1]) / max(1, totalvotes))
    vs = _vs(election)

    return {
        "closeness": closeness,
        "vs": vs,
        "compound": _compound_score(closeness, vs)
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
        lambda k: k["office"] == "US Senate" and k["county"] == None, elections), key=lambda k: k["year"]))
    house = list(sorted(filter(
        lambda k: k["office"] == "US House", elections), key=lambda k: k["year"]))
    president = list(sorted(filter(
        lambda k: k["office"] == "US President" and k["county"] == None, elections), key=lambda k: k["year"]))

    senate_score = _compound_score(
        _weighted_closeness_score(senate), _current_vs(senate))
    house_score = _compound_score(
        _weighted_closeness_score(house), _current_vs(house))
    president_score = _compound_score(
        _weighted_closeness_score(president), _current_vs(president))

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
        "closeness_total": (_weighted_closeness_score(senate) + _weighted_closeness_score(house) + _weighted_closeness_score(president)) / 3,
        "vs_total": (_current_vs(senate) + _current_vs(house) + _current_vs(president)) / 3,
        "vs_senate": _current_vs(senate),
        "vs_house": _current_vs(house),
        "vs_president": _current_vs(president),
    }
