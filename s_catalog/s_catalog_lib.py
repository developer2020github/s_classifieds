import random, string


def get_random_string(length=32):
    random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(length))
    return random_string

if __name__ == "__main__":
    for i in xrange(9):
        print(get_random_string(10))

