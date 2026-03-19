from constants import *
import check_strings as cs
from fix_constants import *
import format_output as fo
from modal_constants import WIDTH_ADDRESS
from modal_constants import DISASSEMBLER_MODE


# expected sizes and texts for disassembly code
DIS_TITLE_DASHES_COUNT = WIDTH_ADDRESS_DISASSEMBLY_MODE + WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
DIS_TITLE_BOX = f"{DELIMITER_COMMENT}{'-'*(DIS_TITLE_DASHES_COUNT)}{DELIMITER_COMMENT}"
DIS_TITLE_BOX_SPACE = f"{DELIMITER_COMMENT}{' '*(DIS_TITLE_DASHES_COUNT)}{DELIMITER_COMMENT}"

DIS_MAIN_NOTES_DASHES_COUNT = WIDTH_ADDRESS_DISASSEMBLY_MODE + WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
DIS_MAIN_NOTES_BOX = f"{DELIMITER_COMMENT}{'-'*(DIS_MAIN_NOTES_DASHES_COUNT)}{DELIMITER_COMMENT}"

DIS_DEBUG_NOTE_DASHES_COUNT = WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
DIS_DEBUG_NOTE_SPACES_COUNT = WIDTH_ADDRESS_DISASSEMBLY_MODE
DIS_DEBUG_NOTE_SPACES = f"{' '*DIS_DEBUG_NOTE_SPACES_COUNT}"
DIS_DEBUG_NOTE_BOX = f"{DIS_DEBUG_NOTE_SPACES}{DELIMITER_COMMENT}{'-'*(DIS_DEBUG_NOTE_DASHES_COUNT)}{DELIMITER_COMMENT}"

# current mode sizes and texts
TITLE_DASHES_COUNT = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
TITLE_BOX = f"{DELIMITER_COMMENT}{'-'*(TITLE_DASHES_COUNT)}{DELIMITER_COMMENT}"
TITLE_BOX_SPACE = f"{DELIMITER_COMMENT}{' '*(TITLE_DASHES_COUNT)}{DELIMITER_COMMENT}"
TITLE_DELIMITERS_WIDTH = len(DELIMITER_LEFT) + len(DELIMITER_RIGHT)
TITLE_TEXT_WIDTH = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - TITLE_DELIMITERS_WIDTH

MAIN_NOTES_DASHES_COUNT = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
MAIN_NOTES_BOX = f"{DELIMITER_COMMENT}{'-'*(MAIN_NOTES_DASHES_COUNT)}{DELIMITER_COMMENT}"

DEBUG_NOTE_DASHES_COUNT = WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
DEBUG_NOTE_SPACES_COUNT = WIDTH_ADDRESS
DEBUG_NOTE_SPACES = f"{' '*DEBUG_NOTE_SPACES_COUNT}"
DEBUG_NOTE_BOX = f"{DEBUG_NOTE_SPACES}{DELIMITER_COMMENT}{'-'*(DEBUG_NOTE_DASHES_COUNT)}{DELIMITER_COMMENT}"
DEBUG_NOTE_BOX_SPACES = f"{DEBUG_NOTE_SPACES}{DELIMITER_COMMENT}{' '*(DEBUG_NOTE_DASHES_COUNT)}{DELIMITER_COMMENT}"


def fix_missing_code(address, hash):
    # TODO instead of returning None give an errror if the call will be kept in fix address
    # TODO check if this is needed in fix_address too

    # this is not one of the expected files: do nothing
    if hash not in MISSING_CODE:
        return None, address

    fix_elements = MISSING_CODE[hash]
    if address not in fix_elements:
        return None, address
    
    # can only reach this point if it is an address of interest

    missing_code = fix_elements[address]
    missing_code = normalize_code(missing_code)
    return missing_code

def normalize_code(code):
    if DISASSEMBLER_MODE:
        return code
    
    # change format for non disassembler mode

    # split code in lines for normalization
    missing_code = []
    for missing_code_line in iter(code.splitlines()):
        if len(missing_code_line) > 5 and cs.is_hex(missing_code_line[0:4]):
            address = fo.format_address(missing_code_line[0:5])
            parts = missing_code_line[8:].split(DELIMITER_COMMENT)
            if len(parts) == 2:
                instruction, comment = parts
                missing_code.append(f"{address}{instruction:<{WIDTH_INSTRUCTION}}{DELIMITER_COMMENT}{comment}")
            else:
                instruction = parts[0]
                missing_code.append(f"{address}{instruction:<{WIDTH_INSTRUCTION}}")
                                    
            continue

        if len(missing_code_line) == 0:
            missing_code.append("")
            continue

        count_dashes = missing_code_line.count('-')
        if count_dashes == DIS_TITLE_DASHES_COUNT:
            # normalize title box
            missing_code.append(TITLE_BOX)
            continue
        elif count_dashes == DIS_MAIN_NOTES_DASHES_COUNT:
            # normalize main note box
            missing_code.append(MAIN_NOTES_BOX)
            continue
        elif count_dashes == DIS_DEBUG_NOTE_DASHES_COUNT:
            # normalize debug note box
            missing_code.append(DEBUG_NOTE_BOX)
            continue

        count_spaces = missing_code_line.strip().count(' ')
        if count_spaces == DIS_TITLE_DASHES_COUNT:
            # normalize title box spaces
            missing_code.append(TITLE_BOX_SPACE)
            continue
        elif count_spaces == DIS_DEBUG_NOTE_DASHES_COUNT:
            # normalize main note box spaces
            missing_code.append(DEBUG_NOTE_BOX_SPACES)
            continue

        if len(missing_code_line) - len(missing_code_line.lstrip()) == DIS_DEBUG_NOTE_SPACES_COUNT:
            # normalize debug note text justification
            missing_code.append(f"{DEBUG_NOTE_SPACES}{missing_code_line.lstrip()}")
            continue

        if missing_code_line.strip()[0] == ";" and missing_code_line.strip()[-1] == ";" and len(missing_code_line.strip()[1:-1]) == DIS_TITLE_DASHES_COUNT:
            # normalize title text justification
            text = missing_code_line.strip()[1:-1].strip()
            title = f"{DELIMITER_LEFT}{text:<{TITLE_TEXT_WIDTH}}{DELIMITER_RIGHT}"
            missing_code.append(title)
            continue

        missing_code.append(missing_code_line)

    missing_code_string = '\n'.join(missing_code)

    # splitlines removes trailing newlines at the end this fix it:
    if code[-1] == "\n":
        missing_code_string = f"{missing_code_string}\n"

    return missing_code_string