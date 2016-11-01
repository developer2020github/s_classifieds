#this module is to be used to generate data for testing purposes

import database
import random
import string
import datetime
import os

EMAIL_DOMAINS = ["yahoo.com", "gmail.com", "hotmail.com", "outlook.com"]
LIST_OF_NAMES = list()
CITIES_LIST = ["Johannesburg", "Dongguan", "Tokyo", "Surat", "Yokohama", "Beijing"]


def get_random_date(within_days_from_now=365):

    random_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, within_days_from_now))
    random_date = random_date - datetime.timedelta(hours=random.randint(0, 12))
    random_date = random_date - datetime.timedelta(minutes=random.randint(0, 59))
    random_date = random_date - datetime.timedelta(seconds=random.randint(0, 59))
    return random_date


def load_list_of_names_from_file(file_name="names.txt"):
    global LIST_OF_NAMES
    with open(file_name) as f:
        LIST_OF_NAMES = f.read().splitlines()


def get_random_name():
    if not LIST_OF_NAMES:
        load_list_of_names_from_file()

    return random.choice(LIST_OF_NAMES)


def get_random_email(name=""):
    if name == "":
        name = get_random_name()
    random_email = name.replace(" ", ".").lower() + "@" + random.choice(EMAIL_DOMAINS)
    return random_email


def get_random_sentence(min_words, max_words):
    line = get_random_line(min_words, max_words).lower()
    random_sentence = line[:2].upper() + line[2:] + "."
    return random_sentence


def get_random_line(min_words, max_words):
    number_of_words = random.randint(min_words, max_words)
    line = ""
    for i in range(0, number_of_words):
        word_length = random.randint(2, 8)
        word = ''.join(random.sample(string.letters, word_length))
        line += " " + word
    return line


def get_random_text(min_number_of_words, max_number_of_words, min_words_in_line_allowed=9, max_words_in_line_allowed=12):
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
    str_code = "(+" + str(random.randint(min_code, max_code)) + ")"
    str_number = str(random.randint(min_after_code, max_after_code))
    str_number = str_number[:3] + "-" + str_number[3:]
    return str_code + " " + str_number


def format_key_value(key, ad_item):
    return key + ": " + str(ad_item[key])


def print_ad(ad):
    print format_key_value("city", ad)
    print format_key_value("category", ad)
    print format_key_value("sub_category", ad)
    print format_key_value("date", ad)
    print format_key_value("user_name", ad)
    print format_key_value("contact_phone", ad)
    print format_key_value("contact_email", ad)
    print format_key_value("ad_title", ad)
    print format_key_value("price", ad)

    print "ad text: "
    print str(ad["text"])


def generate_random_ads(number_of_ads):

    ads = list()

    for i in range(0, number_of_ads):
        ad = dict()
        ad["city"] = random.choice(CITIES_LIST)
        ad["category"] = random.choice(database.get_categories())
        ad["sub_category"] = random.choice(database.get_sub_categories(ad["category"]))
        ad["user_name"] = get_random_name()
        ad["date"] = get_random_date()
        ad["contact_phone"] = get_random_phone_number()
        ad["ad_title"] = get_random_sentence(2, 7)
        ad["contact_email"] = get_random_email(ad["user_name"])
        ad["text"] = get_random_text(10, 45)
        ad["price"] = random.randint(50, 10000)

        ads.append(ad)
    return ads

if __name__ == "__main__":
    random_ads = generate_random_ads(54)
    for current_ad in random_ads:
        print ""
        print ""
        print_ad(current_ad)


