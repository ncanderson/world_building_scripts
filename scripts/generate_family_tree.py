#!/usr/bin/env python3

import random
import json


###############################################################################

"""
# TODO make allowances for closeted
# TODO this doesn't actually allow straight trans people, needs a re-think
do this for all percentages, load from config
import json

class Person:
    DEFAULTS = {}

    @classmethod
    def load_defaults(cls, config_file="config.json"):
        with open(config_file, "r") as f:
            cls.DEFAULTS = json.load(f)

    def __init__(self):
        self.__dict__.update(Person.DEFAULTS)

# Load defaults before creating instances
Person.load_defaults()

p1 = Person()
print(p1.name)  # Output: Unknown
"""

class Person:
    def __init__(self, birth_year):

        self.age = 0
        self.birth_year = birth_year
        self.death_year = None
        self.fertility_modifier = self.generate_weighted_float()
        self.pregnant = False
        self.children = []
        self.spouses = []

        # Gender assigned at birth, 50/50 chance
        self.gab = "male" if random.random() < 0.5 else "female"
        self.init_repro()

        # Generate the gender identity
        self.gender_identity = self.identity()
        self.determine_attraction()


    ###########################################################################


    def identity(self) -> str:
        """
        @brief Returns gender identity based on probabilities.
        @returns Identity
        """
        identity_weights = {
            "cis": .8,
            "nonbinary": .1,
            "trans": .1
        }

        identity = random.choices(list(identity_weights.keys()),
                                  weights=identity_weights.values(),
                                  k=1)[0]
        if identity == "trans":
            return identity + " " + "man" if self.gab == "female" else "woman"
        else:
            return identity


    ###########################################################################


    def determine_attraction(self) -> None:
        """!
        @brief Set attraction preferences based on identity and gender.
        @details This has to be executed after identity()
        """

        attraction_weights = {
            "straight": .8,
            "gay": .08,
            "bi": .08,
            "ace": .04
        }

        self.attraction = random.choices(list(attraction_weights.keys()),
                                         weights=attraction_weights.values(),
                                         k=1)[0]

        if self.attraction == "bi":
            self.attraction_to_can_bear = True
            self.attraction_to_can_sire = True
            return
        if self.attraction == "ace":
            self.attraction_to_can_bear = False
            self.attraction_to_can_sire = False
            return
        # Gayness or straightness depends on identity
        if self.attraction == "straight":
            self.attraction_to_can_bear = self.can_sire_children
            self.attraction_to_can_sire = self.can_bear_children
        elif self.attraction == "gay":
            self.attraction_to_can_bear = self.can_sire_children
            self.attraction_to_can_sire = self.can_bear_children

        # If trans, invert
        if self.gender_identity.startswith("trans"):
            self.attraction_to_can_bear = not self.attraction_to_can_bear
            self.attraction_to_can_sire = not self.attraction_to_can_sire

        return


    ###########################################################################


    def init_repro(self, infert_probability=0.05):
        # Randomly decide whether both can bear or sire children are False (5% chance)
        if random.random() < infert_probability:
            self.can_bear_children = False
            self.can_sire_children = False
        else:
            # Otherwise use the gender-assigned-at-birth
            if self.gab == "male":
                self.can_bear_children = False
                self.can_sire_children = True
            else:
                self.can_bear_children = True
                self.can_sire_children = False


    ###########################################################################


    def is_queer(self, probability=0.1):
        """Returns True with a given probability."""
        return self.gender_identity != "cis" or self.attraction != "straight"


    ###########################################################################


    @staticmethod
    def generate_weighted_float():
        """Generate a float between 0 and 2 with a normal distribution around 1."""
        return max(0, min(2, random.gauss(mu=1, sigma=0.5)))


# End of Person
###############################################################################


def load_json_data(file_path: str) -> dict:
    """Loads general config from a JSON file and returns it as a dictionary."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return {}


###############################################################################


def update_year(current_year, year_steps, is_btr, generation_end_year):
    """Updates the current year based on BTR/TR mode and checks the stopping condition."""
    if is_btr:
        return current_year - year_steps if current_year > generation_end_year else None
    else:
        return current_year + year_steps if current_year < generation_end_year else None


###############################################################################


def main():

    ###########################################################################
    # Setup

    path_to_fert_config = "/home/nanderson/nate_personal/projects/world_building_scripts/config/human_fertility_by_age.json"
    fertility_rates = load_json_data(path_to_fert_config)

    path_to_app_config = "/home/nanderson/nate_personal/projects/world_building_scripts/config/generate_famlily_tree_config.json"
    app_config = load_json_data(path_to_app_config)

    # Load some defaults
    is_btr = app_config["is_btr"]
    generation_start_year = app_config["generation_start_year"]
    generation_end_year = app_config["generation_end_year"]
    year_steps = app_config["year_steps"]

    # Check for invalid BTR range: End year cannot be greater than start year in BTR
    if is_btr and abs(generation_end_year) > abs(generation_start_year):
        print("Error: In BTR, the end year cannot be greater than the start year.")
        sys.exit(1)  # Exit the script with an error code

    ###########################################################################
    # Run Loop

    current_year = generation_start_year
    living_people = []
    dead_people = []

    living_people.append(Person(current_year))

    while current_year is not None:
        print(f"Simulating year: {current_year}")




        current_year = update_year(current_year, year_steps, is_btr, generation_end_year)

    for person in living_people:
        for attr, value in vars(person).items():
            print(f"{attr}: {value}")

if __name__ == "__main__":
    main()
