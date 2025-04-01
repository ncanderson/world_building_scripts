import json
import os
import random

# Variable for the value of row 1, column 1
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
min_year = -2010
max_year = max(death_years)

# Prepare the output lines for the tab-delimited file
output_lines = []

# First row: Place the variable in the first column, without adding the year columns
first_row = [row_1_col_1_value] + ["" for _ in range(min_year, max_year + 1)]
output_lines.append("\t".join(first_row))

# Process each person
for name, (birth_year, death_year) in people.items():
    row = [""] * (len(range(min_year, max_year + 1)) + 1)  # Empty row with first column blank
    row[0] = name  # Set the name in the first column

    # Find the index in the years list
    birth_index = birth_year - min_year + 1
    death_index = death_year - min_year + 1

    # Populate the row with age progression
    for i in range(birth_index, death_index + 1):
        age = i - birth_index  # Calculate age
        row[i] = str(age)

    row[birth_index] = "birth"  # Mark birth
    row[death_index] = "death"  # Mark death

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
y_position = 0  # Start y at 0, increment by 70 for each record
nodes = []

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
    y_position += 70  # Increment y for the next record

# Define the output file name for the JSON file
json_output_file_path = "family_tree_nodes.json"

# Write the JSON output with each node on a single line
with open(json_output_file_path, "w", encoding="utf-8") as f:
    f.write('{"nodes": [\n')
    f.write(",\n".join(json.dumps(node, separators=(',', ':')) for node in nodes))
    f.write('\n],"edges": []}\n')

print(f"JSON nodes output written to {json_output_file_path}")
