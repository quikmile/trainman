import random
import string


def get_random_string(length):
    return ''.join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def remove_quotes(string):
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return string
