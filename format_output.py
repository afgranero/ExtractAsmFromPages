
from constants import *
import fix_instructions as fi
from modal_constants import DISASSEMBLER_MODE, WIDTH_ADDRESS, NO_INLINE_MODE


def format_address(address):
    if DISASSEMBLER_MODE:
        return f"{address:<{WIDTH_ADDRESS}}"
    else:
        if NO_INLINE_MODE:
            return f" ORG {address}\n";
        else:
            return f" ORG {address}: ";


def format_instruction(instruction):
    instruction = fi.fix_instruction(instruction)
    if NO_INLINE_MODE:
        # add space before instruction
        # compensate for the lack of ' ORG nnnnH ' before the instruction that will impact comments alignment
        return f" {instruction:<{WIDTH_INSTRUCTION + 11}}"
    else:
        return f"{instruction:<{WIDTH_INSTRUCTION}}"
