
from constants import *
import fix_instructions as fi


def format_address(address):
    return f"{address:<{WIDTH_ADDRESS}}"


def format_instruction(instruction):
    instruction = fi.fix_instruction(instruction)
    return f"{instruction:<{WIDTH_INSTRUCTION}}"