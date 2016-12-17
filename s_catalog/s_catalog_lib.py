import random, string
import math

'''
Functions list_of_int_to_int and int_to_list_of_int
were developed for more efficient storage of user-specific
lists of sub-categories:
we could have a table of users with integers storing user-specific sub-categories (i.e.
sub-categories in which user has ads) in their bits.
However, currently database is small and there are requests to get user-specific ads anyway,
so will not be proceeding with this option for current version of the program.
Nevertheless, will keep the functions and corresponding unit test in the library for future enhancements.

'''


def get_random_string(length=32):
    random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(length))
    return random_string


def test_int_to_list_of_int():
    for i in range(1, 25):
        print ""
        print i
        print bin(i)
        print int_to_list_of_int(25, i)


def list_of_int_to_int(list_of_ints):
    """
    This takes a list of integers and converts it into an integer in such way that
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


def test_list_of_int_to_int(max_value_to_store=25, print_successful_tests=False):
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

if __name__ == "__main__":
    test_list_of_int_to_int()

    #print int_to_list_of_int(25, 12)
    #print bin(12)