
from constants import *
import column_processing as cp


def format_address(address):
    return f"{address:<{WIDTH_ADDRESS}}"


def format_instruction(instruction):
    instruction = cp.fix_instruction(instruction)
    return f"{instruction:<{WIDTH_INSTRUCTION}}"