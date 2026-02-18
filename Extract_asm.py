import sys
import os
from pathlib import Path
import operator

from bs4 import BeautifulSoup


WIDTH_ADDRESS = 12
WIDTH_INSTRUCTION = 16
WIDTH_COMMENT = 100
PRE_DOTS = "... "
POST_DOTS = " ..."
COMMENT_SEPARATOR = "; "
COL_INDEX_ADDRESS = 0
COL_INDEX_INSTRUCTION = 1
COL_INDEX_COMMENT= 2

# this program is for extracting ASM code from a se of specific files ...
# ... it is notintended to be a generic use one ...
# ... the ifs maze reflect a lot of inconsistencies, exceptions, and errors on the HTML page it parses

def error_and_exit(message):
        print(message, file=sys.stderr)
        sys.exit(1)

def format_address(address):
    return f"{address:<{WIDTH_ADDRESS}}"

def format_instruction(instruction):
    return f"{instruction:<{WIDTH_INSTRUCTION}}"

def get_normalized_comment(comment, col_inner_count):
    comment = comment.replace("\r", "").replace("\n","")
    if col_inner_count == 1:
        return COMMENT_SEPARATOR + comment
    
    lines_count = (col_inner_count // 2) + 1
    # calculate where to divide line
    cut_point = int(len(comment) / lines_count) - 1
    # divide line adding ... on the end of the first and ... at the start of the others
    lines = []
    prev_real_cut_point = 0
    for i in range(1, lines_count+1):
        real_cut_point = comment.find(" ", i * cut_point)

        if i == 1: prefix, suffix = "", POST_DOTS
        if i > 1 and i < lines_count: prefix, suffix = PRE_DOTS, POST_DOTS
        if i == lines_count: prefix, suffix = PRE_DOTS, ""

        line = comment[prev_real_cut_point:real_cut_point]
        lines.append(COMMENT_SEPARATOR + prefix + line + suffix)

        prev_real_cut_point = real_cut_point
    else:
        lines[i-1] = lines[i-1] + comment[prev_real_cut_point:]
    return lines


def is_hex(s):
    if not s:  # int() will not work on empty strings
        return False
    try:
        i = int(s, 16)
        return True, i
    except ValueError:
        return False, None
    
def is_address_consistent(address_dec, prev_address_dec):   
    return 0 <= address_dec <= 65535 and address_dec > prev_address_dec

def process_cols(code_line):
    # easier to have code_line for debugging

    # it is needed to know the number of elements prior so I avoid lazy evaluation ...
    # ... at this point there will be about 3 elements tops so it is not a problem
    cols = list(code_line.children)
    cols_count = len(cols)

    if cols_count == 4:
        # this is an error on the page formatting: 
        # ... you can ignore the second DIV if it repeats the instruction ...
        # ... the repeat was inadvertly put as comment garbling format ...
        # ... remove it
        if cols[1].get_text() != cols[2].get_text():
            error_and_exit(f"Unexpected format: repeatded instruction does not match: '{cols[1].get_text()}', '{cols[2].get_text()}'.")

        cols.pop(2)
        cols_count = len(cols)

    col_address = cols[COL_INDEX_ADDRESS]
    col_instruction = cols[COL_INDEX_INSTRUCTION]
    if cols_count == 3:
        # there is a case where there are no comments
        # TODO see if it needs a refactoring to put it in other scope
        col_comment = cols[COL_INDEX_COMMENT]
        col_comment_inner_count = len (col_comment.contents)

    col_address_inner_count = len(col_address.contents)
    col_instruction_inner_count = len(col_instruction.contents)
  

    address = ""
    address_dec = -1
    prev_address_dec = -1

    # column 0 is address
    if col_address_inner_count == 1:
        prev_address_dec = address_dec
        address = col_address.contents[0]
        f_hex, address_dec = is_hex(address[:-1])
        if f_hex and is_address_consistent(address_dec, prev_address_dec):
            print(format_address(address), end="")
        else:
            error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{prev_address_dec:X}'.")
    elif col_address_inner_count % 2 != 0 and col_instruction_inner_count % 2 != 0 and col_address_inner_count == col_instruction_inner_count:
        # an alternate format: ..
        # ... several addresses in one tag on column 1
        # ... several instructions in one tag on column 2
        # ... so the comment is applied to those group of addresses and instructions
        comment = col_comment.contents[0]
        comments = get_normalized_comment(comment, col_address_inner_count)
        lines = []
        k = 0
        for j in range(0, col_address_inner_count, 2):
            address = col_address.contents[j].get_text(strip=True)
            instruction = col_instruction.contents[j].get_text(strip=True)
            if operator.xor(address == "", instruction == ""):
                # address and instruction lists are inconsistent
                error_and_exit(f"Inconsistent address: '{col_address.contents[j]}' and instruction: '{col_instruction.contents[j]}'.")
            
            if address == "" and instruction == "":
                # it is a </br> skipt it
                continue

            f_hex, address_dec = is_hex(address[:-1])
            if f_hex and is_address_consistent(address_dec, prev_address_dec):
                lines.append(format_address(address) + format_instruction(instruction) + comments[k])
                k += 1
            else:
                error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{prev_address_dec:X}'.")
        
        for line in lines:
            print(line)
    elif col_address_inner_count == 3:
        # a weird single case where at 0BFA the DEC HL instruction is given ...
        # ... and an empty address follows with no instruction ...
        # ... comparing with with ROM image the instruction repeats twice, what matches the comment about decremented twice
        addresses = col_address.contents
        address1 = addresses[0].get_text(strip=True)
        address2 = addresses[1].get_text(strip=True)
        address3 = addresses[2].get_text(strip=True)
        _, address_dec1 = is_hex(address1[:-1])
        _, address_dec3 = is_hex(address3[:-1])
        if not(address_dec1 + 1 == address_dec3 and address2 == ""):
            error_and_exit(f"Unexpected format: sequential addresses in two lines not found: '{col_address.decode_contents()}'.")

        lines = []
        instruction = col_instruction.contents[0].get_text(strip=True)
        comment = get_normalized_comment(col_comment.contents[0], 1)
        lines.append(format_address(address1) + format_instruction(instruction) + comment)
        lines.append(format_address(address1) + format_instruction(instruction))

        for line in lines:
            print(line)

    else:
        error_and_exit(f"Unexpected format: '{col_address.decode_contents()}'")






    # column 1 is instruction  
    if col_instruction_inner_count == 1:
        if cols_count == 3:
            # normal case: address instruction; comment
            instruction = col_instruction.contents[0].get_text(strip=True)
            comments = col_comment.contents
            if col_comment_inner_count == 0:
                # there is no comment
                comment = ""
            elif col_comment_inner_count == 1:
                # normal case one comment
                comment = comments[0]
            elif col_comment_inner_count > 1: 
                # the comment has more than a line  already formatted: ...
                # ... first line after the instruction ...
                # ... other lines continuing the comment without instruction before
                # TODO implement
                # TODO print print first line complete and just comments on single lines aline
                # TODO put after next print outside the if so treaats the comments only

                comment = "" # placefolder for now
                            
            # TODO here the second parameter of get_normalized_comment 
            # TODO ... received get_normalized_comment but I think it was wrong ...
            # TODO ...it treated the cases with 0 and 1 comment only not several
            print(format_instruction(instruction) + get_normalized_comment(comment, 1))
        elif cols_count == 2:
            # usually just addresses followed by data definitions with no comments: ...
            # ... print with CR ...
            # ... skip to the next
            instruction = col_instruction.contents[0].get_text(strip=True)
            print(format_instruction(instruction))
    elif col_instruction_inner_count > 1:
        # TODO the instruction: print it
        # two cases : ...
        # ... two quotation marks enclosing a single character
        # TODO implement
        pass
        # ... an RST followed by two bytes that are parameters skipped by the called routine manipulating PC
        # TODO implement
        pass


def process(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        error_and_exit(f"Error: The file '{file}' was not found.")
    except IOError as e:
        error_and_exit(f"Error reading file '{file}': {e}")

    soup = BeautifulSoup(content, 'html.parser')
    code_lines = soup.find_all('div', class_='assembly-row-combined')

    if code_lines:
        for code_line in code_lines:
            if code_line.name == "div":
                process_cols(code_line)
            else:
                error_and_exit(f"Unexpected content found: '{code_line.decode_contents()}'")
    else:
        error_and_exit("'assembly-row-combined' class not found.")

def main():
    path = "."
    nparams = len(sys.argv)
    if nparams > 1:
        path = sys.argv[1]
    if nparams > 2:
        print("Too many parameters, only the first one will be used.")

    # script_dir = Path(__file__).resolve().parent
    # path = os.path.join(script_dir, path)


    # 
    files = []
    if os.path.isdir(path):
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() and Path(entry).suffix in [".html", ".htm"]:
                    files.append(entry.name)

    if os.path.isfile(path):
        files.append(path)

    for file in files:
        process(file)


if __name__ == "__main__":
    main()
