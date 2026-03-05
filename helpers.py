import hashlib
import sys


# attributes in funtions are only initialized the first time tunction is called...
# ... using a decorator that is run at definition I can use them,
def error_and_exit(message):
        print(message, file=sys.stderr)
        sys.exit(1)


def compute_file_hash(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    # Read in 64KB chunks to handle large files
    with open(file_path, 'rb') as file:
        while chunk := file.read(65536):
            hash_func.update(chunk)
    return hash_func.hexdigest()