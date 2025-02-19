import json
import os
import random

# Variable for the value of row 1, column 1 (this can be updated later via a config)
row_1_col_1_value = "Simit-sil-hak"

# Path to the external JSON file
json_file_path = os.path.join("..", "raw", "sen-duga-dynasty.json")

# Read the JSON file
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Function to extract person details (name, birth year, and death year)
def get_person_details(person):
    name = person['name']
    birth_year = int(person['birth'].split()[0]) * -1  # Convert BC to negative
    death_year = int(person['death'].split()[0]) * -1  # Convert BC to negative
    return name, birth_year, death_year

# Extract all people (including spouses and children) from the family tree
people = {}
death_years = []

def add_person(family):
    name, birth_year, death_year = get_person_details(family)
    if name not in people:
        people[name] = (birth_year, death_year)
        death_years.append(death_year)

# Add top-level family members
for family in data['familyTree']:
    add_person(family)

    # Add spouses
    for spouse in family.get('spouses', []):
        add_person(spouse)

    # Add children
    for child in family.get('children', []):
        add_person(child)

# Set minimum year to -2000 and find the latest death year dynamically
min_year = -2000
max_year = max(death_years)

# Generate the range of years from -2000 to the latest death year
years = list(range(min_year, max_year + 1))

# Prepare the output lines for the tab-delimited file
output_lines = []

# First row: Place the variable in the first column, without adding the year columns
first_row = [row_1_col_1_value] + [""] * len(years)
output_lines.append("\t".join(first_row))

# Process each person
for name, (birth_year, death_year) in people.items():
    row = [""] * (len(years) + 1)  # Empty row with first column blank
    row[0] = name  # Set the name in the first column

    # Find the index in the years list and mark "birth" and "death"
    birth_index = years.index(birth_year) + 1  # Offset by 1 for first blank field
    death_index = years.index(death_year) + 1  # Offset by 1 for first blank field

    row[birth_index] = "birth"
    row[death_index] = "death"

    # Add the row to output
    output_lines.append("\t".join(row))

# Define the output file name for the tab-delimited file
output_file_path = "family_tree_output.txt"

# Write the tab-delimited output to a file
with open(output_file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Tab-delimited output written to {output_file_path}")

### JSON NODES FILE OUTPUT ###

# Function to generate a random 16-character hexadecimal string
def generate_id():
    return ''.join(random.choices("0123456789abcdef", k=16))

# Create nodes array
nodes = []
y_position = 0  # Start y at 0, increment by 70 for each record

for name in people.keys():
    nodes.append({
        "id": generate_id(),
        "type": "text",
        "text": f"[[{name}]]",
        "x": 0,
        "y": y_position,
        "width": 350,
        "height": 60
    })
    y_position += 70  # Increment y for the next record

# Create the final JSON structure
json_output = {
    "nodes": nodes,
    "edges": []  # No edges specified yet
}

# Define the output file name for the JSON file
json_output_file_path = "family_tree_nodes.json"

# Write the JSON output to a file
with open(json_output_file_path, "w", encoding="utf-8") as f:
    json.dump(json_output, f, indent=4)

print(f"JSON nodes output written to {json_output_file_path}")
