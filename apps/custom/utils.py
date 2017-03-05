import random
import string


def get_random_string(length):
    prefix = ''.join(random.choice(string.ascii_lowercase) for _ in range(1))
    suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length - 1))
    return prefix + suffix


def remove_quotes(string):
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return string
