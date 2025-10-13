import random
import string

def generate_random_string(length, html_safe=True):
    characters = string.ascii_letters + string.digits + string.punctuation
    safe_characters = string.ascii_letters + string.digits
    
    if not html_safe:
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string
    
    random_string = ''.join(random.choice(safe_characters) for _ in range(length))
    return random_string