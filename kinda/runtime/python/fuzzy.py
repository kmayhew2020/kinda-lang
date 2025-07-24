# Auto-generated fuzzy runtime for Python
import random
env = {}

# (not needed for now — handled in interpreter)

def kinda_int(val):
    fuzz = random.randint(-1, 1)
    return val + fuzz

env["kinda_int"] = kinda_int

def sometimes():
    return random.random() < 0.5

env["sometimes"] = sometimes

def sorta_print(*args):
    if random.random() < 0.8:
        print('[print]', *args)
    else:
        print('[shrug]', *args)

env["sorta_print"] = sorta_print

