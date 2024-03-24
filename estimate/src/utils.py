import string
import random

characters = string.ascii_letters + string.digits


def random_str(length: int):
    output = ''
    for _ in range(length):
        output += random.choice(characters)
    return output
