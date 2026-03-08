import check_strings as cs
from decorators import *


def fix_instruction(instruction):
    if fix_missing_defb.condition(instruction):
        instruction = fix_missing_defb(instruction)
    elif fix_defb_instead_of_defw.condition(instruction):
        instruction = fix_defb_instead_of_defw(instruction)
    elif fix_missing_defm.condition(instruction):
        instruction = fix_missing_defm(instruction)
    elif fix_plus_instead_of_coma.condition(instruction):
        instruction = fix_plus_instead_of_coma(instruction)
    elif fix_defb_parameter_without_coma.condition(instruction):
        instruction = fix_defb_parameter_without_coma(instruction)

    return instruction


@call_count
@with_condition(lambda instruction: cs.is_hex(instruction[:-1]) and instruction[-1] == "H" and len(instruction[:-1]) == 2)
def fix_missing_defb(instruction):
    # example:
    #
    # 28H
    #

    # hexadecimal value without DEFB (return DEFB 28H)
    instruction = f"DEFB {instruction}"
    return instruction


@call_count
@with_condition(lambda instruction: instruction[0:4] == "DEFB" and cs.is_hex(instruction[5:-1]) and instruction[-1] == "H" and len(instruction[5:-1]) > 2)
def fix_defb_instead_of_defw(instruction):
    # example:
    #
    # DEFB 84C4H
    #

    # defb instead of defw what is wrong because addresses must be little endian (return DEFW 84C4H)
    instruction = f"DEFW {instruction[5:-1]}H"
    return instruction


@call_count
@with_condition(lambda instruction: cs.is_quoted_string(instruction))
def fix_missing_defm(instruction):
    # example:
    #
    # "BREAK AT"
    #

    # literal without DEFM (return DEFM "BREAK AT")
    instruction = f"DEFM {instruction}"
    return instruction


@call_count
@with_condition(lambda instruction: cs.is_quoted_string_with_cr(instruction))
def fix_plus_instead_of_coma(instruction):
    # example:
    #
    # "HOW?" + 0DH
    #

    # string literal followed by CR (used for error messages: return DEFB "HOW?", 0DH)
    instructions = instruction.split("+")
    instruction = f"DEFB {instructions[0].strip()}, {instructions[1].strip()}"
    return instruction


@call_count
@with_condition(lambda instruction: instruction[:5] == "DEFB " and len(instruction[5:].split(" ")) > 1 and all(map(cs.is_hex, map(lambda s: s[:-1], instruction[5:].split(" ")))))
def fix_defb_parameter_without_coma(instruction):
    # example:
    #
    # DEFB 40H E7H 4DH
    #

    # DEFB of several bytes without commas (creturn DEFB 40H, E7H, 4DH)
    instruction = instruction[:5] + instruction[5:].replace(" ", ", ")
    return instruction
