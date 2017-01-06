"""
This module contains generic library functions that do not fit into any other module.

Functions list_of_int_to_int and int_to_list_of_int
were developed for more efficient storage of user-specific
lists of sub-categories:
we could have a table of users with integers storing user-specific sub-categories (i.e.
sub-categories in which user has ads) in their bits.
However, currently database is small and there are requests to get user-specific ads anyway,
so will not be proceeding with this option for current version of the program.
Nevertheless, will keep the functions and corresponding unit test in the library for future enhancements.
"""

import random
import string
import math
import os
from copy import copy
import sqlalchemy as sa
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy import create_engine
import options


def get_random_string(length=32):
    """
    :param length: lenght of random string
    :return: a random string
    """
    random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(length))
    return random_string


def list_of_int_to_int(list_of_ints):
    """
    This function takes a list of integers and converts it into an integer in such way that
    corresponding bits of output integer are set to 1.
    Indexing starts with 1
    i.e, if input list is [2, 4, 7] output should be
    ob0101001
    :param list_of_ints: list of integers as explained above
    :return: integer value it converts to
    """
    max_int = max(list_of_ints)
    # Max number of bits needed to represent the list is max_int
    # we need same number of bits for the mask wiht left most bit == 1
    mask = int(math.pow(2, max_int-1))
    result = 0

    for i in range(1, max_int+1):
        if i in list_of_ints:
            result = result | mask
        mask >>= 1
    return result

def int_to_list_of_int(max_value, input_int):
    """
    This function takes an integer and checks each bit
    up to the max_value. If bit is set, its index will be included in the output.
    I.e. if input is 5 (101)- output will be
     1, 3 (second bit is not set)
    :param max_value:
    :param input_int:
    :return:
    """
    mask = 1
    int_length = int.bit_length(input_int)
    # always go from left to right

    mask <<= int_length-1

    result = []
    for i in range(1, max_value+1):
        if input_int & mask:
            result.append(i)
        mask >>= 1

    return result


def test_list_of_int_to_int(max_value_to_store=25, print_successful_tests=False):
    """
    Unit test function for list_of_int_to_int and int_to_list_of_int function.
    Will print fail/pass messages to console together with relevant details.
    :param max_value_to_store: max value to be stored
    :param print_successful_tests: if true, output will include  all test results. If False, only failed unit tests will
     be printed
    :return:
    """
    print "testing int_to_list_of_int and list_of_int_to_int"
    test_outcome = "all tests passed"
    for i in range(1, 100000):
        # generate some sample list
        l = int_to_list_of_int(max_value_to_store, i)
        # convert it to integer for storage
        int_from_list = list_of_int_to_int(l)
        # now convert it back to list and see if it matches original list
        l1 = int_to_list_of_int(max_value_to_store, int_from_list)
        if l1 == l:
            if print_successful_tests:
                print "test ok: "
                print l
                print ""
        else:
            print "test failed"
            print "input list:"
            print l
            print "output list:"
            print l1

            print ""
            test_outcome = "test(s) failed"

    print test_outcome


def database_exists(url):
    """
    This function was copied from sqlalchemy-utils
    github: https://github.com/kvesteri/sqlalchemy-utils

    Check if a database exists.

    :param url: A SQLAlchemy engine URL.

    Performs backend-specific testing to quickly determine if a database
    exists on the server. ::

        database_exists('postgres://postgres@localhost/name')  #=> False
        create_database('postgres://postgres@localhost/name')
        database_exists('postgres://postgres@localhost/name')  #=> True

    Supports checking against a constructed URL as well. ::

        engine = create_engine('postgres://postgres@localhost/name')
        database_exists(engine.url)  #=> False
        create_database(engine.url)
        database_exists(engine.url)  #=> True

    """

    url = copy(make_url(url))
    database = url.database
    if url.drivername.startswith('postgresql'):
        url.database = 'template1'
    else:
        url.database = None

    engine = sa.create_engine(url)

    if engine.dialect.name == 'postgresql':
        text = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
        result =  bool(engine.execute(text).scalar())
        engine.dispose()
        return result

    elif engine.dialect.name == 'mysql':
        text = ("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                "WHERE SCHEMA_NAME = '%s'" % database)
        return bool(engine.execute(text).scalar())

    elif engine.dialect.name == 'sqlite':
        if database:
            return database == ':memory:' or os.path.exists(database)
        else:
            # The default SQLAlchemy database is in memory,
            # and :memory is not required, thus we should support that use-case
            return True

    else:
        text = 'SELECT 1'
        try:
            url.database = database
            engine = sa.create_engine(url)
            engine.execute(text)

            return True

        except (ProgrammingError, OperationalError):
            return False


def create_postgres_database(database_name, default_db_url=options.POSTGRES_DEFAULT_URL):
    """
    This function creates a database in Postgres.
    Ref. http://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy
    :param database_name: name of the database to create
    :param default_db_url: URL to  connect to default postgres database.
    :return:
    """

    current_engine = create_engine(default_db_url)
    conn = current_engine.connect()
    conn.execute("commit")
    cmd_string = "create database " + database_name
    conn.execute(cmd_string)
    conn.close()

if __name__ == "__main__":
    pass