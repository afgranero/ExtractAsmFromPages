import check_strings as cs
from decorators import *


def fix_instruction(instruction):
    if fix_missing_defb.condition(instruction):
        instruction = fix_missing_defb(instruction)
    elif fix_defb_instead_of_defw.condition(instruction):
        instruction = fix_defb_instead_of_defw(instruction)
    return instruction


@call_count
@with_condition(lambda instruction: cs.is_hex(instruction[:-1]) and instruction[-1] == "H" and len(instruction[:-1]) == 2)
def fix_missing_defb(instruction):
    instruction = f"DEFB {instruction}"
    return instruction


@call_count
@with_condition(lambda instruction: instruction[0:4] == "DEFB" and cs.is_hex(instruction[5:-1]) and instruction[-1] == "H" and len(instruction[5:-1]) > 2)
def fix_defb_instead_of_defw(instruction):
    instruction = f"DEFW {instruction[5:-1]}H"
    return instruction