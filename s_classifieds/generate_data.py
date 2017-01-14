"""
this module is to be used to generate data for testing purposes
(to populate database with randomly generated ads).
List of user names comes from file names.txt (this file is required for moduel to work)
and ad categories, sub-categories and
list of locations (cities) come from options module.
"""

import random
import string
import datetime
import os
import options

EMAIL_DOMAINS = ["yahoo.com", "gmail.com", "hotmail.com", "outlook.com"]
LIST_OF_NAMES = list()
LIST_OF_USERS = list()
NAMES_FILE = os.path.join(options.APPLICATION_FOLDER, "names.txt")


def get_list_of_users():
    return LIST_OF_USERS


def init_user_data():
    """
    Initializes list of user daata structures (LIST_OF_USERS)
    Names are loded from file namex.txt, emails and phone numbers are randomly generated.
    :return: none
    """
    global LIST_OF_USERS

    if not LIST_OF_USERS:

        if not LIST_OF_NAMES:
            load_list_of_names_from_file()
        for name in LIST_OF_NAMES:
            user = dict()
            user["name"] = name
            user["email"] = get_random_email(name)
            user["phone"] = get_random_phone_number()
            LIST_OF_USERS.append(user)


def get_sub_categories(category):
    """
    Wrapper function
    :param category: category
    :return:  list of cub categories in the category
    """
    return options.CATEGORIES_WITH_SUB_CATEGORIES[category]


def get_categories():
    """
    Wrapper function
    :return: list of ctagories
    """
    return options.CATEGORIES_WITH_SUB_CATEGORIES.keys()


def get_random_date(within_days_from_now=365):
    """
    :param within_days_from_now: number of days to go back from current date to define range from which random date will
     be selected
    :return: random date within  within_days_from_now days from current date
    """
    random_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, within_days_from_now))
    random_date = random_date - datetime.timedelta(hours=random.randint(0, 12))
    random_date = random_date - datetime.timedelta(minutes=random.randint(0, 59))
    random_date = random_date - datetime.timedelta(seconds=random.randint(0, 59))
    return random_date


def load_list_of_names_from_file(file_name=NAMES_FILE):
    """
    Loads list of names from a file (to be used to generate data to populate database for testing purposes)
    and assigns it to module global LIST_OF_NAMES
    :param file_name: file name to load data from
    :return: None
    """
    global LIST_OF_NAMES
    with open(file_name) as f:
        LIST_OF_NAMES = f.read().splitlines()


def get_random_name():
    """
    :return: randomly selected name form list of names
    """
    if not LIST_OF_NAMES:
        load_list_of_names_from_file()

    return random.choice(LIST_OF_NAMES)


def get_random_email(name=""):
    """
    :param name: optinal user name
    :return: randomly generated email. Email domain is picked from module globla list EMAIL_DOMAINS
    """
    if name == "":
        name = get_random_name()
    random_email = name.replace(" ", ".").lower() + "@" + random.choice(EMAIL_DOMAINS)
    return random_email


def get_random_sentence(min_words, max_words):
    """
    :param min_words: min number of words to  be in the return string
    :param max_words: max number of words to be in the return string
    :return: a string consisting of randomly generated "words" with comma at the end.
            First word starts with a capital letter.
    """
    line = get_random_line(min_words, max_words).lower()
    random_sentence = line[:2].upper() + line[2:] + "."
    return random_sentence


def get_random_line(min_words, max_words):
    """
    :param min_words: min_words: min number of words to  be in the return string
    :param max_words: max number of words to be in the return string
    :return: a string consisting of randomly generated "words"
    """

    number_of_words = random.randint(min_words, max_words)
    line = ""
    for i in range(0, number_of_words):
        word_length = random.randint(2, 8)
        word = ''.join(random.sample(string.letters, word_length))
        line += " " + word
    return line


def get_random_text(min_number_of_words, max_number_of_words, min_words_in_line_allowed=9,
                    max_words_in_line_allowed=12):
    """
    Returns a paragraph of randomly generated lines.
    :param min_number_of_words: min number of words to be in the paragraph
    :param max_number_of_words: max number of words to be in the paragraph
    :param min_words_in_line_allowed: min number of words per line
    :param max_words_in_line_allowed: mas number of words per line
    :return: a paragraph of randomly generated lines.
    """
    number_of_words = random.randint(min_number_of_words, max_number_of_words)
    random_text = ""
    max_words_in_line = random.randint(min_words_in_line_allowed, max_words_in_line_allowed)
    line = ""
    words_in_line = 0
    for i in range(1, number_of_words):
        word_length = random.randint(2, 8)
        word = ''.join(random.sample(string.letters, word_length))
        if words_in_line > max_words_in_line:
            words_in_line = 0
            random_text += os.linesep + line.lower()
            max_words_in_line = random.randint(min_words_in_line_allowed, max_words_in_line_allowed)
            line = ""
        else:
            line += " " + word
            words_in_line+=1

    if line != "":
        random_text += " " + os.linesep + line.lower()

    return random_text


def get_random_phone_number(max_after_code=9999999, min_after_code=1111111, max_code=999, min_code=101):
    """
    Generates random phone number as string. Number consits of a code in parenthesis, followed by a number.
    Example: (+112) 477-9331
    :param max_after_code:  maximum possible value of the number (after  code)
    :param min_after_code:  minimum possible value of the number (after  code)
    :param max_code: maximum possible value of the code
    :param min_code: minimum possible value of the code
    :return:
    """
    str_code = "(+" + str(random.randint(min_code, max_code)) + ")"
    str_number = str(random.randint(min_after_code, max_after_code))
    str_number = str_number[:3] + "-" + str_number[3:]
    return str_code + " " + str_number


def format_key_value(key, ad_item):
    """
    helper function
    :param key: key into ad item_dictionary
    :param ad_item:  ad_item - dictionary of items
    :return: key: value string
    """
    return key + ": " + str(ad_item[key])


def print_ad(ad):
    """
    Helper function. Prints ad data structure(dictionary) to console
    :param ad: ad to print
    :return: None
    """
    print format_key_value("city", ad)
    print format_key_value("category", ad)
    print format_key_value("sub_category", ad)
    print format_key_value("date", ad)
    print format_key_value("user_name", ad)
    print format_key_value("contact_phone", ad)
    print format_key_value("contact_email", ad)
    print format_key_value("ad_title", ad)
    print format_key_value("price", ad)
    print format_key_value("ad_id", ad)
    print "ad text: "
    print str(ad["text"])


def generate_random_ads(number_of_ads):
    """

    :param number_of_ads: number of ads to generate
    :return: list of randomly generated ad data structures (dictionaries)
    """
    ads = list()

    for i in range(0, number_of_ads):
        ad = dict()
        ad["city"] = random.choice(options.CITIES_LIST)
        ad["category"] = random.choice(get_categories())
        ad["sub_category"] = random.choice(get_sub_categories(ad["category"]))
        ad["user_name"] = get_random_name()
        ad["date"] = get_random_date()
        ad["contact_phone"] = get_random_phone_number()
        ad["ad_title"] = get_random_sentence(2, 7)
        ad["contact_email"] = get_random_email(ad["user_name"])
        ad["text"] = get_random_text(50, 70)
        ad["price_cents"] = random.randint(5000, 1000000)
        ad["ad_id"] = i+1

        ads.append(ad)
    return ads


if __name__ == "__main__":
    init_user_data()
else:
    init_user_data()

