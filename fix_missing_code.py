

from constants import *
import check_strings as cs
import format_output as fo
from missing_code import *
from modal_constants import WIDTH_ADDRESS
from modal_constants import DISASSEMBLER_MODE

MISSING_CODE = {
    # TRS-80 - Level 1 ROM Disassembled.html/TRS-80 - Level 1 ROM Disassembled.html
    '33e2ac3b3c6417fd9307feb68f4c7e2c965ce34b54b46fc8b274b39282eef019':
        {
            '0098H': MC_TRS80_M1_L1_0098,
            '032BH': MC_TRS80_M1_L1_032B,
            '0336H': MC_TRS80_M1_L1_0336,
            '0EBDH': MC_TRS80_M1_L1_0EBD,
        },
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 1.html
    '76337e787a728184b3f5a8af89bedcb8ade1ad79937809d05302f4951f007676': 
        {},
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 2.html
    'ecc98da804913d11f43d7f9f5bc911841020af954a877c728891bd7f1013852b':
        {},
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 3.html
    'a9e56a939c987889be77c22b331974105b7aabc700f8d541d84560653e5f95a8':
        {},
    # Model III ROM Explained - Part 1.html
    '0f2f2135b06b067b3ec6d751ead77d2801902272563ca3ae53bc8a890298089d':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 2.html
    'c4003dbe2e36707400a47c1f28d80ebaca5f7812b34014c3fb3f062c5273e48f':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 3.html
    'c73cf199246f061c047c108e6d1f375dd292f2b243b6d96859f37d94d2b607e6':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 4.html
    'dbabc65bdfb220c4d44a6f6ca8e9bad4ba8416c6885990e275908a7cc935111e':
        {},
    }


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