import requests
import random
import os
import json
import re

with open("data/gen/elections.json", "r") as infile:
    ELECTIONS = json.load(infile)

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
        #we did this in WAMR, not sure if it's necessary here as well

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

def _score(election):
    votes = list(sorted([candidate["votes"]
                         for candidate in election["candidates"]], reverse=True)) + [0, 0]
    totalvotes = election['totalvotes']
    return 1 - ((votes[0] - votes[1]) / totalvotes)

def _weighted_score(elections):
    total_weight = 0
    total_scores = 0

    for election in elections:
        weight = election["year"] - 1975
        total_weight += weight
        total_scores += _score(election) * weight

    return total_scores / total_weight

def compute_scores(elections):
    senate = list(filter(lambda k: k["office"] == "US Senate", elections))
    house = list(filter(lambda k: k["office"] == "US House", elections))
    president = list(filter(lambda k: k["office"] == "US President", elections))

    senate_score = _weighted_score(senate) 
    house_score = _weighted_score(house)
    president_score = _weighted_score(president)

    senate_history = list(senate)
    for election in senate_history:
        election['score'] = _score(election)

    house_history = list(house)
    for election in house_history:
        election['score'] = _score(election)

    president_history = list(president)
    for election in president_history:
        election['score'] = _score(election)

    return {
        "senate": senate_score,   
        "senate_history": senate_history,    
        "house": house_score,
        "house_history": house_history,
        "president": president_score,
        "president_history": president_history,
        "total": (senate_score + house_score + president_score) / 3
    }

    pass
