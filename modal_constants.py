from helpers import error_and_exit

# this module allows import cvalues that will remain constant for all the life of the program run ...
# ... but are defined from a parameter that coems from command line ...
# ... this avoids a lote of parameters for a thing that in practice is a global constant

# internal storage for all modal constants
_GLOBALS = {}


def set(name, value):
    if name in _GLOBALS:
        error_and_exit(f"Constant of mode {name} already initialized")

    _GLOBALS[name] = value

def get(name):
    if name not in _GLOBALS:
        error_and_exit(f"Constant of mode {name} not set yet")
        
    return _GLOBALS[name]

def __getattr__(name):
    if name == "__path__":
        return
    
    if name in _GLOBALS:
        return _GLOBALS[name]
    
    error_and_exit(f"Constant of mode {name} not set yet")
