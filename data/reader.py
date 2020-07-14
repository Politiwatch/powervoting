import unicodecsv as ucsv

def _intify(val):
    try:
        return int(val)
    except:
        return None

def _election_id(election):
    return str(election.get("year")) + \
        str(election.get("state")) + \
        str(election.get("state_fips")) + \
        str(election.get("FIPS")) + \
        str(election.get("office")) + \
        str(election.get("district"))

def read_mit_election_archive(csvfile):
    elections = {}

    reader = ucsv.DictReader(csvfile)
    for row in reader:
        eid = _election_id(row)
        election = {
            "year": _intify(row.get("year")),
            "state": row.get("state_po").lower(),
            "fips": row.get("state_fips") or row.get("FIPS"),
            "office": row.get("office"),
            "county": row.get("county"),
            "district": row.get("district"),
            "totalvotes": _intify(row.get("totalvotes")),
            "special": row.get("special"),
            "candidates": [],
        }

        if eid in elections:
            election = elections[eid]

        candidate = next(filter(lambda k: k["name"] == row["candidate"], election["candidates"]), None)

        if candidate:
            election.get("candidates").remove(candidate)
            candidate["party"].append(row.get("party"))
            candidate["votes"] +=  _intify(row.get("candidatevotes"))
        else:
            candidate = {
                "name": row.get("candidate"),
                "party": [row.get("party")],
                "votes": _intify(row.get("candidatevotes")),
                "mode": row.get("mode"),
                "writein": row.get("writein"),
            }

        election.get("candidates").append(candidate)
        
        elections[eid] = election
    
    return list(elections.values())

if __name__ == "__main__":

    all_elections = []

    with open('sources/senate.csv', "rb") as csvfile:
        all_elections.extend(read_mit_election_archive(csvfile))

    print(all_elections[-1])

    with open('sources/house.csv', "rb") as csvfile:
        all_elections.extend(read_mit_election_archive(csvfile))

    print(all_elections[-5])

    with open('sources/president.csv', "rb") as csvfile:
        all_elections.extend(read_mit_election_archive(csvfile))

    print(all_elections[-1])

    print(list(filter(lambda k: "Nadler" in str(k), all_elections)))

    print(f"Total elections: {len(all_elections)}")