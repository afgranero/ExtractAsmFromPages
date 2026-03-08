
from constants import *
import fix_instructions as fi
from modal_constants import DISASSEMBLER_MODE, WIDTH_ADDRESS


def format_address(address):
    if DISASSEMBLER_MODE:
        return f"{address:<{WIDTH_ADDRESS}}"
    else:
        return f" ORG {address}: "


def format_instruction(instruction):
    instruction = fi.fix_instruction(instruction)
    return f"{instruction:<{WIDTH_INSTRUCTION}}"