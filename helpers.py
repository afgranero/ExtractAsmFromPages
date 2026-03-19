import hashlib
import os
import sys


# attributes in funtions are only initialized the first time tunction is called...
# ... using a decorator that is run at definition I can use them,
def error_and_exit(message):
        print(message, file=sys.stderr)
        sys.exit(1)


def compute_file_hash(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    try:
        # Read in 64KB chunks to handle large files
        with open(file_path, 'rb') as file:
            while chunk := file.read(65536):
                hash_func.update(chunk)
    except FileNotFoundError:
        error_and_exit(f"Error: The file '{file_path}' was not found.")
    except IOError as e:
        error_and_exit(f"Error reading file '{file_path}': {e.strerror}")

    return hash_func.hexdigest()


def output_to_file_and_stdio(file_path):
    try:
        log = open(file_path, "w", buffering=1)
    except IOError as e:
        error_and_exit(f"Error writing file '{file_path}': {e.strerror}")

    sys.stdout = type('', (), {
        'write': lambda self, x: (sys.__stdout__.write(x), log.write(x)),
        'flush': lambda self: (sys.__stdout__.flush(), log.flush())
    })()
