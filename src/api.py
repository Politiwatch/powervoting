import requests
import random
import os
import json
import re

GOOGLE_API_KEYS = os.getenv("GOOGLE_API_KEYS").split(",")

def get_address_info(address, zipcode):
    print(zipcode)
    repdata = requests.get(
        "https://www.googleapis.com/civicinfo/v2/representatives",
        params={"address": f"{address} {zipcode}", "key": random.choice(GOOGLE_API_KEYS)},
    ).json()

    division_ids = "\n".join(repdata["divisions"].keys())

    state = re.search(r"^ocd-division\/country:us\/state:(..)$", division_ids, flags=re.MULTILINE)
    if state:
        state = state.group(1)

    county = re.search(r"^ocd-division\/country:us\/state:..\/county:(.+)$", division_ids, flags=re.MULTILINE)
    if county:
        county = county.group(1)

    cd = re.search(r"^ocd-division\/country:us\/state:..\/cd:(.+)$", division_ids, flags=re.MULTILINE)
    if cd:
        cd = cd.group(1)

    return {
        "state": state,
        "county": county,
        "cd": cd
    }