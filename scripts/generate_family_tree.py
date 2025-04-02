#!/usr/bin/env python3

import random
import json


###############################################################################


class Helpers:

    @staticmethod
    def generate_weighted_float(
        min_val=0, max_val=2, mean=1, std_deviation=0.5
    ) -> float:
        """!
        @brief Generate a float between 0 and 2 with a normal distribution around 1.
        """
        return max(min_val, min(max_val, random.gauss(mu=mean, sigma=std_deviation)))


    ###########################################################################


    @staticmethod
    def tragedy_strikes(tragedy_probability) -> bool:
        """!
        @brief Check the tragedy probability and return a boolean if a random
        number is less that the probability.
        """
        return random.random() <= tragedy_probability



###############################################################################


"""
# TODO make allowances for closeted

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
        self.age_at_death = None
        self.fertility_modifier = Helpers.generate_weighted_float()
        self.pregnant = False
        self.children = []
        self.spouses = []

        # Gender assigned at birth, 50/50 chance
        self.gab = "male" if random.random() < 0.5 else "female"
        self.init_repro()

        # Generate the gender identity
        self.gender_identity = self.identity()
        self.determine_attraction()
        self.queer = self.is_queer()

    ###########################################################################

    def identity(self) -> str:
        """
        @brief Returns gender identity based on probabilities.
        @returns Identity
        """
        identity_weights = {"cis": 0.8, "nonbinary": 0.1, "trans": 0.1}

        identity = random.choices(
            list(identity_weights.keys()), weights=identity_weights.values(), k=1
        )[0]
        if identity == "trans":
            return identity + " " + ("man" if self.gab == "female" else "woman")
        else:
            return identity

    ###########################################################################

    def determine_attraction(self) -> None:
        """!
        @brief Set attraction preferences based on identity and gender.
        @details This has to be executed after identity()
        """

        attraction_weights = {"straight": 0.8, "gay": 0.08, "bi": 0.08, "ace": 0.04}

        self.attraction = random.choices(
            list(attraction_weights.keys()), weights=attraction_weights.values(), k=1
        )[0]

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
            self.attraction_to_can_bear = self.can_bear_children
            self.attraction_to_can_sire = self.can_sire_children

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


    def check_marriage(self, marriage_config) -> None:
        """!
        @brief Check config and marry 'em off.
        """
        #
        average_marriage_age = marriage_config["average_marriage_age"]
        # Extend the min and max
        marriage_tail = marriage_config["marriage_tail"]
        marriage_modifier = marriage_config["marriage_modifier"]
        max_spouses = marriage_config["max_spouses"]

        # Check current spouse number
        if len(self.spouses) >= max_spouses:
            return

        # Dynamically generate a marriage age
        age_check = Helpers.generate_weighted_float(
            average_marriage_age - marriage_tail,
            average_marriage_age + marriage_tail,
            average_marriage_age
        )
        print(age_check)
        if age_check <= self.age:
            # too young, try next year
            return



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
    # TODO Organize the config into sub-maps
    time_config = app_config["time_config"]
    is_btr = time_config["is_btr"]
    generation_start_year = time_config["generation_start_year"]
    generation_end_year = time_config["generation_end_year"]
    year_steps = time_config["year_steps"]

    # Marriage
    marriage_confg = app_config["marriage_config"]

    # Death
    death_confg = app_config["death_config"]
    average_death_age = death_confg["average_death_age"]
    death_tail = death_confg["death_tail"]
    tragedy_probability = death_confg["tragedy_probability"]

    # Check for invalid BTR range: End year cannot be greater than start year in BTR
    if is_btr and abs(generation_end_year) > abs(generation_start_year):
        print("Error: In BTR, the end year cannot be greater than the start year.")
        sys.exit(1)  # Exit the script with an error code

    ###########################################################################
    # Run Loop

    current_year = generation_start_year
    living_people = []
    dead_people = []

    # The first person
    living_people.append(Person(current_year))

    # Run through each year
    while current_year is not None:
        print(f"Simulating year: {current_year}")

        # Check each living person
        for person in living_people[:]:

            # Tragedy?
            if Helpers.tragedy_strikes(tragedy_probability):
                living_people.remove(person)
                person.death_year = current_year
                person.age_at_death = abs(person.death_year - person.birth_year)
                dead_people.append(person)
                continue

            # Normal Death?

            # Age up
            person.age += 1

            # Marriage?
            person.check_marriage(marriage_confg)

            # Gets pregnant?


            # New baby?
            if person.pregnant:
                living_people.append(Person(current_year))
                person.pregnant = False

    for person in living_people:
        for attr, value in vars(person).items():
            print(f"{attr}: {value}")


# End of main()
###########################################################################


if __name__ == "__main__":
    main()
