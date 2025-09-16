import random
import string
import secrets


def rand_str(chars=string.ascii_lowercase + string.digits, n=10):
    return ''.join(random.choice(chars) for _ in range(n))


def rand_hex():
    return f'#{secrets.token_hex(3)}'
