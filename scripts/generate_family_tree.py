#!/usr/bin/env python3

import random
import math
import json
import uuid
from enum import Enum

# TODO Make this work with BTR/TR. probably start at zero, then use abs(negative numbers)
# to determine correct year

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
        roll = random.random()
        return roll <= tragedy_probability


###############################################################################


"""
# TODO how to implement intersex people that have the 'wrong' GAB
# TODO figure out how to handle marriage and children for ace people

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

    DEFAULTS = {}

    @classmethod
    def load_defaults(cls, default_config):
        """!
        @brief Load any defaults needed by this class
        """
        cls.DEFAULTS = default_config

    ###########################################################################

    class PrimaryAttraction(Enum):
        GENDER = "gender"
        REPRO = "repro"

    class Orientation(Enum):
        STRAIGHT = "straight"
        GAY = "gay"
        BI = "bi"
        ACE = "ace"

    class GenderExpression(Enum):
        MAN = "man"
        WOMAN = "woman"
        NONBINARY = "nonbinary"

    class GenderAlignment(Enum):
        CIS = "cis"
        TRANS = "trans"

    ###########################################################################

    def __init__(self, birth_year):

        # The fertility modifer needs some defaults
        self.__dict__.update(Person.DEFAULTS)

        # Other attrs
        self.id = str(uuid.uuid4())
        self.created_as = None
        self.age = 0
        self.birth_year = birth_year
        self.death_year = None
        self.death_age = None
        self.cause_of_death = None
        self.fertility_modifier = Helpers.generate_weighted_float(
            self.min_fert, self.max_fert, self.bebe_mean, self.bebe_std_deviation
        )
        self.pregnant = False
        self.children = []
        self.spouses = []

        # Gender assigned at birth, 50/50 chance
        self.gab = Person.equal_chance(
            Person.GenderExpression.MAN, Person.GenderExpression.WOMAN
        )

        # Reproduction abilities
        self.can_bear_children = None
        self.can_sire_children = None
        self.infertile = None
        self.init_repro(self.gab)

        # Generate Orientation
        self.orientation = Person.get_orientation()

        # Generate attraction
        self.primary_attraction = Person.equal_chance(
            Person.PrimaryAttraction.GENDER, Person.PrimaryAttraction.REPRO
        )

        # Generate the gender identity
        self.gender_expression = self.get_gender_expression()

        # Generate gender alignment
        self.gender_alignment = self.set_gender_alignment()

        # Check queerness
        self.queer = self.is_queer()

    ###########################################################################

    def to_dict(self):
        return {
            "id": self.id,
            "created_as": self.created_as,
            "age": self.age,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "death_age": self.death_age,
            "cause_of_death": self.cause_of_death,
            "fertility_modifier": self.fertility_modifier,
            "pregnant": self.pregnant,
            "children": [child for child in self.children],
            "spouses": [spouse for spouse in self.spouses],
            "gab": self.gab.value,
            "can_bear_children": self.can_bear_children,
            "can_sire_children": self.can_sire_children,
            "infertile": self.infertile,
            "orientation": self.orientation.value,
            "primary_attraction": self.primary_attraction.value,
            "gender_expression": self.gender_expression.value,
            "gender_alignment": self.gender_alignment.value,
            "queer": self.queer,
        }

    ###########################################################################

    def create_compat_spouse(self, spouse):

        # I am primarily attracted to a person's gender
        if self.primary_attraction == Person.PrimaryAttraction.GENDER:

            # Spouse gender expression, based on my orientation
            if self.orientation == Person.Orientation.STRAIGHT:
                if self.gender_expression == Person.GenderExpression.NONBINARY:
                    spouse.gender_expression = Person.binary_swap(self.gab)
                else:
                    spouse.gender_expression = Person.binary_swap(self.gab)
            elif self.orientation == Person.Orientation.GAY:
                spouse.gender_expression = self.gab
            elif (
                self.orientation == Person.Orientation.BI
                or self.orientation == Person.Orientation.ACE
            ):
                spouse.gender_expression = Person.equal_chance(
                    Person.GenderExpression.WOMAN, Person.GenderExpression.MAN
                )

            # Spouse gender alignment, which is less important since I am attracted to gender
            spouse_identity_prefix = Person.get_gender_alignment()
            if spouse_identity_prefix == Person.GenderAlignment.CIS:
                spouse.gab = spouse.gender_expression
            elif spouse_identity_prefix == Person.GenderAlignment.TRANS:
                if spouse.gender_expression == Person.GenderExpression.NONBINARY:
                    spouse.gab = Person.binary_swap(spouse.gab)
                else:
                    spouse.gab = Person.binary_swap(spouse.gender_expression)

            # Spouse reproduction abilities, which is less important since I am attracted to gender
            spouse.init_repro(spouse.gab)

            # Spouse primary attraction
            spouse.primary_attraction = Person.equal_chance(
                Person.PrimaryAttraction.GENDER, Person.PrimaryAttraction.REPRO
            )

            # Spouse orientation
            # First check for bi or ace, as those will override gay/straight
            temp_orientation = Person.get_orientation()
            if (
                temp_orientation == Person.Orientation.BI
                or temp_orientation == Person.Orientation.ACE
            ):
                spouse.orientation = temp_orientation
            else:
                if spouse.gender_expression == self.gender_expression:
                    spouse.orientation = Person.Orientation.GAY
                else:
                    spouse.orientation = Person.Orientation.STRAIGHT

        # I am primarily attracted to a person's equipment
        elif self.primary_attraction == Person.PrimaryAttraction.REPRO:

            if self.orientation == Person.Orientation.STRAIGHT:
                if self.gender_expression == Person.GenderExpression.NONBINARY:
                    spouse.gab = Person.binary_swap(self.gab)
                else:
                    spouse.gab = Person.binary_swap(self.gender_expression)

            elif self.orientation == Person.Orientation.GAY:
                if self.gender_expression == Person.GenderExpression.NONBINARY:
                    spouse.gab = Person.binary_swap(self.gab)
                else:
                    spouse.gab = Person.binary_swap(self.gender_expression)

            elif (
                self.orientation == Person.Orientation.BI
                or self.orientation == Person.Orientation.ACE
            ):
                spouse.gab = Person.equal_chance(
                    Person.GenderExpression.WOMAN, Person.GenderExpression.MAN
                )

            # Spouse reproduction abilities
            spouse.init_repro(spouse.gab)

            # Spouse primary attraction
            spouse.primary_attraction = Person.equal_chance(
                Person.PrimaryAttraction.GENDER, Person.PrimaryAttraction.REPRO
            )

            # Don't really care, I am attracted to equipment
            spouse.gender_expression = spouse.get_gender_expression()

            # Spouse orientation
            # First check for bi or ace, as those will override gay/straight
            temp_orientation = Person.get_orientation()
            if (
                temp_orientation == Person.Orientation.BI
                or temp_orientation == Person.Orientation.ACE
            ):
                spouse.orientation = temp_orientation
            else:
                if spouse.gender_expression == self.gender_expression:
                    spouse.orientation = Person.Orientation.GAY
                else:
                    spouse.orientation = Person.Orientation.STRAIGHT

        # Finally, make a roll to see if their ident is actually NB. This means that we're
        # assuming attraction based on binary expression, but that there is always the
        # chance that this person is actually nonbinary.
        spouse.am_i_enby()
        # Set gender alignment based on all that nonsense
        spouse.gender_alignment = spouse.set_gender_alignment()

    ###########################################################################

    @staticmethod
    def equal_chance(first_arg, second_arg):
        """!
        @brief 50/50 chance of returning either arg
        """
        return first_arg if random.random() < 0.5 else second_arg

    ###########################################################################

    @staticmethod
    def get_orientation() -> str:
        """!
        @brief Get attraction string for use elsewhere
        """
        attraction_weights = {
            Person.Orientation.STRAIGHT: 0.8,
            Person.Orientation.GAY: 0.08,
            Person.Orientation.BI: 0.08,
            Person.Orientation.ACE: 0.04,
        }

        return random.choices(
            list(attraction_weights.keys()), weights=attraction_weights.values(), k=1
        )[0]

    ###########################################################################

    @staticmethod
    def get_gender_alignment() -> str:
        """!
        @brief Get an enum representation of gender identity
        """
        ident_chance = {
            Person.GenderAlignment.CIS: 0.8,
            Person.GenderAlignment.TRANS: 0.2,
        }

        return random.choices(
            list(ident_chance.keys()), weights=ident_chance.values(), k=1
        )[0]

    ###########################################################################

    @staticmethod
    def binary_swap(expression):
        """!
        @brief Help function to return man/woman binary opposite
        """
        allowed_expression = [
            Person.GenderExpression.MAN,
            Person.GenderExpression.WOMAN,
        ]
        # Raise error if this is being used wrong
        if expression not in allowed_expression:
            raise ValueError(
                f"Invalid argument: {expression}. Allowed: {allowed_expression}"
            )

        if expression == Person.GenderExpression.MAN:
            return Person.GenderExpression.WOMAN
        if expression == Person.GenderExpression.WOMAN:
            return Person.GenderExpression.MAN

    ###########################################################################

    def am_i_enby(self, enby_probability=0.1):
        """!
        @brief Since being nonbinary isn't necessarily tied to reproduction and
        can arise for anyone, use a roll to determine if a person's expression
        is non-binary
        """
        if random.random() < enby_probability:
            self.gender_expression = Person.GenderExpression.NONBINARY
            return True
        else:
            return False

    ###########################################################################

    def get_gender_expression(self, ident_prefix=None) -> str:
        """
        @brief Returns gender identity based on probabilities.
        @returns Identity
        """
        # First check for enby, which will override the other choices
        if self.am_i_enby() == True:
            return Person.GenderExpression.NONBINARY

        # Otherwise, check if we've been given an argument
        if ident_prefix is None:
            rand_identity = Person.get_gender_alignment()
        else:
            rand_identity = ident_prefix

        # Finally, parse the alignment result
        if rand_identity == Person.GenderAlignment.CIS:
            return self.gab
        elif rand_identity == Person.GenderAlignment.TRANS:
            if self.gab == Person.GenderExpression.MAN:
                return Person.GenderExpression.WOMAN
            elif self.gab == Person.GenderExpression.WOMAN:
                return Person.GenderExpression.MAN

    ###########################################################################

    def set_gender_alignment(self):

        if self.gender_expression == Person.GenderExpression.NONBINARY:
            return Person.GenderExpression.NONBINARY
        elif self.gender_expression == self.gab:
            return Person.GenderAlignment.CIS
        elif self.gender_expression != self.gab:
            return Person.GenderAlignment.TRANS
        else:
            return None

    ###########################################################################

    def init_repro(self, gab, infert_probability=0.05):
        """!
        @brief Randomly decide whether both can bear or sire children are False (5% chance)
        """
        if random.random() < infert_probability:
            self.infertile = True
        else:
            self.infertile = False

        if gab == Person.GenderExpression.MAN:
            self.can_bear_children = False
            self.can_sire_children = True
        else:
            self.can_bear_children = True
            self.can_sire_children = False
        # todo intersex people

    ###########################################################################

    def determine_attraction(self) -> None:
        """!
        @brief Set attraction preferences based on identity and gender.
        @details This has to be executed after identity()
        """
        self.attraction = self.get_attraction_string()

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

    def is_queer(self, probability=0.1):
        """Returns True with a given probability."""
        return (
            self.gender_expression != self.gab
            or self.orientation != Person.Orientation.STRAIGHT
        )

    ###########################################################################

    def check_marriage(self, marriage_config, current_year, living_people):
        """!
        @brief Check config and marry 'em off.
        @details This only supports one spouse per year
        """
        #
        average_marriage_age = marriage_config["average_marriage_age"]
        # Extend the min and max
        marriage_low_tail = marriage_config["marriage_low_tail"]
        marriage_high_tail = marriage_config["marriage_high_tail"]
        marriage_std_deviation = marriage_config["marriage_std_deviation"]
        marriage_chance = marriage_config["marriage_chance"]
        max_spouses = marriage_config["max_spouses"]
        marriage_respects_queerness = marriage_config["marriage_respects_queerness"]

        # Check current living spouse number
        spouse_count = 0
        for spouse_id in self.spouses:
            if spouse_id is not None and living_people[spouse_id].death_age is None:
                spouse_count += 1

        if spouse_count >= max_spouses:
            return

        # Dynamically generate a marriage age
        age_check = Helpers.generate_weighted_float(
            average_marriage_age - marriage_low_tail,
            average_marriage_age + marriage_high_tail,
            average_marriage_age,
            marriage_std_deviation,
        )
        if age_check <= self.age:
            # too young, try next year
            # In theory, a person could have one young marriage and then no more
            # for years.
            return

        # Otherwise, valid for marriage
        if random.random() <= marriage_chance:
            # Use random age we generate earlier
            # TODO Make this work with BTR/TR
            new_spouse = self.create_new_spouse(
                current_year + age_check, marriage_respects_queerness
            )

            self.spouses.append(new_spouse.id)
            new_spouse.spouses.append(self.id)
            new_spouse.created_as = "generated spouse"
            return new_spouse

    ###########################################################################

    def create_new_spouse(self, birth_year, marriage_respects_queerness):
        """!
        @brief Create a new spouse that `self` will like/tolerate
        """
        spouse = Person(birth_year)

        # ie I'm the king/queen and I don't give a fuck who you say you are
        # you're going to carry on my family name
        if not marriage_respects_queerness:
            spouse.gab = (
                Person.GenderExpression.MAN
                if self.gab == Person.GenderExpression.WOMAN
                else Person.GenderExpression.MAN
            )
            spouse.init_repro()
            spouse.gender_identity = spouse.identity()
            spouse.determine_attraction()
            spouse.queer = spouse.is_queer()
        else:
            self.create_compat_spouse(spouse)

        return spouse

    ###########################################################################

    def you_have_died(self, death_config, current_year):
        """
        @brief Returns True if the person dies this year based on age.
        @param age Current age
        @param mid_age The age at which risk is ~50% of max_prob
        @param steepness How sharply risk increases with age
        @param max_prob The highest possible death chance per year (never reaches 100%)
        """
        average_death_age = death_config["average_death_age"]
        death_chance_accel = death_config["death_chance_accel"]
        max_death_chance = death_config["max_death_chance"]

        logistic = 1 / (
            1 + math.exp(-death_chance_accel * (self.age - average_death_age))
        )
        death_chance = min(max_death_chance, logistic * max_death_chance)
        return random.random() < death_chance

    ###########################################################################

    def you_are_pregnant(self, living_people, new_people):
        """!
        @brief Check for pregnancy. This will set the 'self' attr, but
        also returns a boolean if that is relevant to anyone.
        @returns True if person is pregnant
        """
        if not self.can_bear_children or self.infertile is True:
            return False
        else:
            #print(json.dumps([p.to_dict() for p in living_people.values()], indent=4))
            for spouse in self.spouses:

                if spouse in living_people:
                    this_spouse = living_people[spouse]
                elif spouse in new_people:
                    this_spouse = new_people[spouse]
                else:
                    raise KeyError("Spouse not found in either dictionary")

                if not this_spouse.can_sire_children:
                    return False

                average_fertility = (self.fertility_modifier + this_spouse.fertility_modifier) / 2

                if random.random() < average_fertility:
                    self.pregnant = True
                    return True

    ###########################################################################


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

    # Bebe
    bebe_config = app_config["bebe"]

    # Death
    death_config = app_config["death_config"]
    tragedy_probability = death_config["tragedy_probability"]

    # Set Person defaults
    Person.load_defaults(bebe_config)

    # Check for invalid BTR range: End year cannot be greater than start year in BTR
    if is_btr and abs(generation_end_year) > abs(generation_start_year):
        print("Error: In BTR, the end year cannot be greater than the start year.")
        sys.exit(1)  # Exit the script with an error code

    ###########################################################################
    # Run Loop

    current_year = generation_start_year
    living_people = {}

    # The first person
    the_first = Person(current_year)
    the_first.created_as = "The First"
    living_people[the_first.id] = the_first

    # Run through each year
    while current_year is not None:
        print(f"Simulating year: {current_year}")
        # print(f"living_people: {len(living_people)}")

        new_people = {}

        # Check each living person
        for person in (p for p in living_people.values() if p.death_age is None):

            # Tragedy?
            if Helpers.tragedy_strikes(tragedy_probability):
                person.death_year = current_year
                person.age_at_death = abs(person.death_year - person.birth_year)
                person.cause_of_death = "tragedy"
                continue
            # Normal Death?
            elif person.you_have_died(death_config, current_year):
                continue

            # Age up
            person.age += 1

            # Marriage?
            new_spouse = person.check_marriage(
                marriage_confg, current_year, living_people
            )
            # Add the new spouse, if found
            if new_spouse is not None:
                new_people[new_spouse.id] = new_spouse

            # New baby?
            if person.pregnant is True:
                bebe = Person(current_year)
                bebe.created_as = "bebe"
                new_people[bebe.id] = bebe
                person.pregnant = False

            # Gets pregnant?
            person.you_are_pregnant(living_people, new_people)

        # Slop the new people into the dict
        living_people = new_people | living_people

        # Update year, ensure we can exit the while loop
        current_year = update_year(
            current_year, year_steps, is_btr, generation_end_year
        )

    # End of main loop
    json_living = json.dumps([p.to_dict() for p in living_people.values()], indent=4)
    print(json_living)

    # for person in living_people:
    #     for attr, value in vars(person).items():
    #         print(f"{attr}: {value}")
    # print("======================================================")
    # for spouse in person.spouses:
    #    for attr, value in vars(person).items():
    #        print(f"{attr}: {value}")


# End of main()
###########################################################################


if __name__ == "__main__":
    main()
