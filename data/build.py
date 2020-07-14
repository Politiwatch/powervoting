#!/usr/bin/env python3

import json
import reader

print("Loading elections...")

all_elections = []
for filename in ["sources/senate.csv", "sources/house.csv", "sources/president.csv"]:
    with open(filename, "rb") as csvfile:
        all_elections.extend(reader.read_mit_election_archive(csvfile))

print(f"Loaded {len(all_elections)} elections! Writing to `gen/elections.json`...")

with open("gen/elections.json", "w") as outfile:
    json.dump(all_elections, outfile)

print("Generation complete!")