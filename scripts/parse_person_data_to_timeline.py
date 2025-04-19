#!/usr/bin/env python3

import json
import os
import random

# Variable for the value of row 1, column 1
row_1_col_1_value = "Simit-sil-hak"

# Path to the external JSON file
json_file_path = "/home/nanderson/nate_personal/projects/world_building_scripts/output/20250419104538_generated_family_tree.json"

# Read the JSON file
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Function to extract person details
def get_person_details(person):
    name = person["id"]
    birth_year = int(person["birth_year"]) * -1  # BC to negative
    death_year = int(person["death_year"]) * -1 if person["death_year"] is not None else None
    return name, birth_year, death_year

# Extract people
people = {}
death_years = []

for person in data["family"]:
    name, birth_year, death_year = get_person_details(person)
    people[name] = (birth_year, death_year)
    if death_year:
        death_years.append(death_year)

# Set year range
min_year = -2010
max_year = max(death_years)

# Output lines for tab-delimited file
output_lines = []

# First row
first_row = [row_1_col_1_value] + ["" for _ in range(min_year, max_year + 1)]
output_lines.append("\t".join(first_row))

# Process people
for name, (birth_year, death_year) in people.items():
    row = [""] * (len(range(min_year, max_year + 1)) + 1)
    row[0] = name
    birth_index = birth_year - min_year + 1
    death_index = death_year - min_year + 1 if death_year is not None else None

    for i in range(birth_index, (death_index + 1) if death_index is not None else len(row)):
        age = i - birth_index
        row[i] = str(age)
    row[birth_index] = "birth"
    if death_index is not None:
        row[death_index] = "death"

    output_lines.append("\t".join(row))

# Write tab-delimited file
output_file_path = "family_tree_output.txt"
with open(output_file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Tab-delimited output written to {output_file_path}")

### JSON NODES FILE OUTPUT ###

def generate_id():
    return ''.join(random.choices("0123456789abcdef", k=16))

nodes = []
y_position = 0

for name in people.keys():
    node = {
        "id": generate_id(),
        "type": "text",
        "text": f"[[{name}]]",
        "x": 0,
        "y": y_position,
        "width": 350,
        "height": 60
    }
    nodes.append(node)
    y_position += 70

json_output_file_path = "family_tree_nodes.json"
with open(json_output_file_path, "w", encoding="utf-8") as f:
    f.write('{"nodes": [\n')
    f.write(",\n".join(json.dumps(node, separators=(',', ':')) for node in nodes))
    f.write('\n],"edges": []}\n')

print(f"JSON nodes output written to {json_output_file_path}")
