#this module is to be used to generate data for testing purposes

import database
import random


def generate_random_ads(number_of_ads):
    for i in range(1, number_of_ads):

        print random.choice(database.get_categories())


if __name__ == "__main__":
    generate_random_ads(27)
