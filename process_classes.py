from bs4 import BeautifulSoup

from constants import *
import fix_addresses as fa
import fix_missing_code as fmc
import format_output as fo
from modal_constants import WIDTH_ADDRESS
import helpers as h
import process_cases as pc
import split_comments as sc


# this program is for extracting ASM code from a se of specific files ...
# ... it is not intended to be a generic use one ...
# ... the ifs maze reflect a lot of inconsistencies, exceptions, and errors on the HTML page it parses

def process_assembly_section_title(code_line, hash):
    # remove symbol of clipboard at the end of title
    code_line.contents[len(code_line.contents)-1].extract()

    text = code_line.get_text()
    text = text.replace("\r", "").replace("\n","").replace("  ", " ")

    # save to avoid repetition on process_main_notes
    process_assembly_section_title.title = text

    address_candidate = text[0:5]
    action, _ = fa.fix_address(address_candidate, hash, "title")
    if action == fa.SKIP:
        return True

    dashes_count = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
    box = f"{DELIMITER_COMMENT}{'-'*(dashes_count)}{DELIMITER_COMMENT}"
    box_space = f"{DELIMITER_COMMENT}{' '*(dashes_count)}{DELIMITER_COMMENT}"

    delimiters_width = len(DELIMITER_LEFT) + len(DELIMITER_RIGHT)
    text_width = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - delimiters_width

    lines = sc.get_comment_lines(text, text_width)

    print()
    print(box)
    print(box_space)
    for line in lines:
        print(f"{DELIMITER_LEFT}{line:<{text_width}}{DELIMITER_RIGHT}")
    print(box_space)
    print(box)
    print()


def process_main_notes(code_line, hash):
    text = code_line.get_text()
    text = text.replace("\r", "").replace("\n","").replace("  ", " ")

    action, _ = fa.fix_address("", hash, "title")
    if action == fa.SKIP:
        return True

    # avoid repeat title in main_note even if they differ just by "" around a char
    # TODO in some files the note can appear before a title and  process_assembly_section_title.title can not exist
    if hasattr(process_assembly_section_title, "title") and process_assembly_section_title.title.replace('"','') == text.replace('"',''):
        return

    dashes_count = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
    box = f"{DELIMITER_COMMENT}{'-'*(dashes_count)}{DELIMITER_COMMENT}"
    box_space = f"{DELIMITER_COMMENT}{' '*(dashes_count)}{DELIMITER_COMMENT}"

    delimiters_width = len(DELIMITER_LEFT) + len(DELIMITER_RIGHT)
    text_width = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - delimiters_width

    lines = sc.get_comment_lines(text, text_width)

    print(box)
    for line in lines:
        print(f"{DELIMITER_LEFT}{line:<{text_width}}{DELIMITER_RIGHT}")
    print(box)
    print()


def process_debug_note(code_line, hash):
    dashes_count = WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
    spaces_count = WIDTH_ADDRESS
    spaces = f"{' '*spaces_count}"
    box = f"{spaces}{DELIMITER_COMMENT}{'-'*(dashes_count)}{DELIMITER_COMMENT}"
    box_space = f"{spaces}{DELIMITER_COMMENT}{' '*(dashes_count)}{DELIMITER_COMMENT}"

    delimiters_width = len(DELIMITER_LEFT) + len(DELIMITER_RIGHT)
    text_width = WIDTH_INSTRUCTION + WIDTH_COMMENT - delimiters_width

    text = f"{code_line.get_text():<{text_width}}"
    text = code_line.get_text()
    text = text.replace("\r", "").replace("\n","")

    action, _ = fa.fix_address("", hash, "title")
    if action == fa.SKIP:
        return True

    lines = sc.get_comment_lines(text, text_width)

    print()
    print(box)
    for line in lines:
        print(f"{' '*spaces_count}{DELIMITER_LEFT}{line:<{text_width}}{DELIMITER_RIGHT}")
    print(box)
    print()


def process_assembly_row_combined(code_line, hash):
    # easier to have code_line for debugging and error messages

    # it is needed to know the number of elements prior so I avoid lazy evaluation ...
    # ... at this point there will be about 3 elements tops so it is not a problem
    cols = list(code_line.children)
    cols_count = len(cols)

    if pc.general_case1.condition(cols_count):
        cols, cols_count = pc.general_case1(cols)

    col_address = cols[COL_INDEX_ADDRESS]
    col_address_count = len(col_address.contents)

    col_instruction = cols[COL_INDEX_INSTRUCTION]
    col_instruction_count = len(col_instruction.contents)

    if cols_count == 3:
        # there is a case where there are no comments: so cols does not have 3 elements
        col_comment = cols[COL_INDEX_COMMENT]
        col_comment_count = len(col_comment.contents)
    else:
        col_comment_count = 0

    # column 0 address
    if pc.address_case1.condition(col_address_count):
        end = pc.address_case1(col_address, hash)
        if end: return
    elif pc.address_case2.condition(col_address_count, col_instruction_count):
        end = pc.address_case2(col_address, col_instruction, col_comment, hash)
        if end: return
    elif pc.address_case3.condition(col_address_count, col_instruction_count):
        end = pc.address_case3(col_address, col_instruction, col_comment)
        if end: return
    else:
        h.error_and_exit(f"Unexpected format: '{code_line.decode_contents()}'")

    # column 1 instruction
    if pc.instruction_case0.condition(col_instruction_count, col_instruction):
        end = pc.instruction_case0(col_address, col_instruction, col_comment, hash)
        if end: return
    elif pc.instruction_case1.condition(col_instruction_count):
        pc.instruction_case1(col_instruction)
    elif pc.instruction_case2.condition(col_instruction_count, col_instruction):
        end = pc.instruction_case2(col_address, col_instruction, col_comment, hash)
        if end: return
    elif pc.instruction_case3.condition(col_instruction_count, col_instruction):
        pc.instruction_case3(col_instruction)
    elif pc.instruction_case4.condition(col_instruction_count, col_instruction):
        pc.instruction_case4(col_instruction)
    elif pc.instruction_case5.condition(col_instruction_count, col_comment_count):
        end = pc.instruction_case5(col_address, col_instruction, col_comment)
        if end: return
    else:
        h.error_and_exit(f"Unexpected format: '{code_line.decode_contents()}'")

    # column 2 comments
    if pc.comment_case1.condition(col_comment_count):
        pc.comment_case1()
    elif pc.comment_case2.condition(col_comment_count):
        pc.comment_case2(col_comment)
    elif pc.comment_case3.condition(col_comment_count):
        pc.comment_case3(col_comment)
    else:
      h.error_and_exit(f"Unexpected format: '{code_line.decode_contents()}'")


def process_classes(code_line, hash):
    if "class" in code_line.attrs:
        classes = code_line.attrs["class"]
    else:
        classes = []

    if "assembly-row-combined" in classes:
        process_assembly_row_combined(code_line, hash)
    elif "assembly-section-title" in classes:
        process_assembly_section_title(code_line, hash)
    elif "debug-note" in classes:
        process_debug_note(code_line, hash)
    elif len(code_line.attrs) == 0:
        process_main_notes(code_line, hash)
    else:
        h.error_and_exit(f"Unexpected format: '{code_line.decode_contents()}'")


def process(file, hash):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        h.error_and_exit(f"Error: The file '{file}' was not found.")
    except IOError as e:
        h.error_and_exit(f"Error reading file '{file}': {e}")

    soup = BeautifulSoup(content, 'html.parser')
    # TODO Process comments with ↓,→,←, and → and other non ASCII chars that macroassemblers does not accept

    div_classes = 'div.assembly-row-combined, h2.assembly-section-title, p.debug-note, p:not([class]):not([style])'
    code_lines = soup.select(div_classes)

    if code_lines:
        for code_line in code_lines:
            if hasattr(fa.fix_address, "next"):
                new_address = fa.fix_address.next
                mising_code = fmc.fix_missing_code(new_address, hash)
                print(mising_code, end="")
                delattr(fa.fix_address, "next")

            process_classes(code_line, hash)
    else:
        pass