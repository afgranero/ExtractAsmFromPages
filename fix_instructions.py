import check_strings as cs
from decorators import *


def fix_instruction(instruction):
    instruction = normalize_hex(instruction)
    
    if fix_missing_defb.condition(instruction):
        instruction = fix_missing_defb(instruction)
    elif fix_defb_xxxxh_to_defb_xxh_coma_xxh.condition(instruction):
        instruction = fix_defb_xxxxh_to_defb_xxh_coma_xxh(instruction)
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
def fix_defb_xxxxh_to_defb_xxh_coma_xxh(instruction):
    # example:
    #
    # DEFB 84C4H
    #

    # defb instead of defw what is wrong because addresses must be little endian (return DEFB 84h, C4H)
    instruction = f"DEFB {instruction[5:7]}H, {instruction[7:-1]}H"
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


def normalize_hex(instruction):
    # assemblers need a leading 0 on addresses or values that start with A, B, C, D, and F ...
    # ... so they can distinguish immediate values from labels

    # I know full well that this could be done in an much easier way ...
    # ... with a regex but I find regex native lib in Python awful ...
    # ... consider it a challenge: can you make a smaller one withou using a regex?

    # assembler do not accept hex values in IX and IY registers offsets ...
    # ... and the offeset can be negative too
    instruction = normalize_index_offsets(instruction, "IX")
    instruction = normalize_index_offsets(instruction, "IY")

    relevant = instruction[3:]
    # all hexadecimal values end in H and have at least a two hexadecimal digits before it
    h_indexes = [i for i, h in enumerate(relevant) if h == "H" and i > 1]
    values = set()
    for h_index in h_indexes:
        if h_index > 3:
            candidate_4_digits = relevant[h_index - 4: h_index]
            if cs.is_hex(candidate_4_digits):
                if candidate_4_digits > "9FFF":
                    values.add(candidate_4_digits)
            else:
                candidate_2_digits = relevant[h_index - 2: h_index]
                if cs.is_hex(candidate_2_digits) and candidate_2_digits > "9F":
                    values.add(candidate_2_digits)
        elif h_index > 1:
            candidate_2_digits = relevant[h_index - 2: h_index]
            if cs.is_hex(candidate_2_digits) and candidate_2_digits > "9F":
                values.add(candidate_2_digits)
    

    new_instruction = instruction
    for value in values:
        new_instruction = new_instruction.replace(value, f"0{value}")
    
    return new_instruction


def normalize_index_offsets(instruction, register):
    # transform index offsets to integer values ...
    # ... and the offeset can be negative too
    prefix = f"({register}+"
    suffix = ")"

    if prefix not in instruction:
        return instruction

    start_index = instruction.index(prefix) + len(prefix)
    end_index = instruction.index(suffix) - 1 # - 1 to ignore the final H
    hex_value = instruction[start_index:end_index]

    # values above 7F are negative
    value, _ = cs.hex2dec(hex_value)
    if value > 127:
        value -= 256

    replace_value = ""
    if value > 0:
        replace_value = f"+{value}"
    elif value < 0:
        replace_value = f"{value}"
    else:
        pass

    new_instruction = instruction.replace(f"+{hex_value}H", replace_value)

    return new_instruction

        






