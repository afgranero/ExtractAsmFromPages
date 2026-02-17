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
    cols = code_line.children
    # it is needed to know the number of elements prior so I avoid lazy evaluation ...
    # ... at this point there will be about 3 elements tops so it is not a problem
    cols_list = list(cols)
    cols_count = len(cols_list)

    if cols_count == 4:
        # this is an error on the page formatting: 
        # ... you can ignore the second DIV if it repeats the instruction ...
        # ... the repeat was inadvertly put as comment garbling format ...
        # ... remove it
        if cols_list[1].get_text() == cols_list[2].get_text():
            cols_list.pop(2)
        else:
            error_and_exit(f"Unexpected format: repeatded instruction does not match: '{cols_list[1].get_text()}', '{cols_list[2].get_text()}'.")

    address = ""
    address_dec = -1
    prev_address_dec = -1
    for i, col in enumerate(cols_list):
        col_inner_count = len(col.contents)
        if i == 0:
            # column 0 is address
            next_col_inner_count = len(cols_list[i+1].contents)
            if col_inner_count == 1:
                prev_address_dec = address_dec
                address = col.contents[0]
                f_hex, address_dec = is_hex(address[:-1])
                if f_hex and is_address_consistent(address_dec, prev_address_dec):
                    print(format_address(address), end="")
                else:
                    error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{prev_address_dec:X}'.")
            elif col_inner_count % 2 != 0 and next_col_inner_count % 2 != 0 and col_inner_count == next_col_inner_count:
                # an alternate format: ..
                # ... several instructions in one tag
                # ... so the comment is applied to those group of instructions
                comment = cols_list[i+2].contents[0]
                comments = get_normalized_comment(comment, col_inner_count)
                lines = []
                k = 0
                for j in range(0, col_inner_count, 2):
                    address = col.contents[j].get_text(strip=True)
                    instruction = cols_list[i+1].contents[j].get_text(strip=True)
                    if address == "" and instruction == "":
                        # it is a </br> skipt it
                        continue
                    elif  operator.xor(address == "", instruction == ""):
                        # address and instruction lists are inconsistent
                         error_and_exit(f"Inconsistent address: '{col.contents[j]}' and instruction: '{cols_list[i+1].contents[j]}'.")
                    f_hex, address_dec = is_hex(address[:-1])
                    if f_hex and is_address_consistent(address_dec, prev_address_dec):
                        lines.append(format_address(address) + format_instruction(instruction) + comments[k])
                        k += 1
                    else:
                        error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{prev_address_dec:X}'.")
                
                for line in lines:
                    print(line)

                break
            elif col_inner_count == 3:
                # a weird single case where at 0BFA the DEC HL instruction is given ...
                # ... and an empty address follows with no instruction ...
                # ... comparing with with ROM image the instruction repeats twice, what matches the comment about decremented twice
                addresses = col.contents
                address1 = addresses[0].get_text(strip=True)
                address2 = addresses[1].get_text(strip=True)
                address3 = addresses[2].get_text(strip=True)
                _, address_dec1 = is_hex(address1[:-1])
                _, address_dec3 = is_hex(address3[:-1])
                if address_dec1 + 1 == address_dec3 and address2 == "":
                    lines = []
                    instruction = cols_list[i+1].contents[0].get_text(strip=True)
                    comment = get_normalized_comment(cols_list[i+2].contents[0], 1)
                    lines.append(format_address(address1) + format_instruction(instruction) + comment)
                    lines.append(format_address(address1) + format_instruction(instruction))

                    for line in lines:
                        print(line)

                    break
                else:
                    error_and_exit(f"Unexpected format: sequential addresses in two lines not found: '{col.decode_contents()}'.")

            else:
                 error_and_exit(f"Unexpected format: '{col.decode_contents()}'")

        elif i == 1:
            # column 1 is instruction    
            if col_inner_count == 1:
                if cols_count == 3:
                    # normal case: address instruction; comment
                    instruction = col.contents[0].get_text(strip=True)
                    comments = cols_list[i+1].contents
                    comments_count = len (comments)
                    if comments_count == 0:
                        # there is no comment
                        comment = ""
                    elif comments_count == 1:
                        # normal case one comment
                        comment = comments[0]
                    elif comments_count > 1: 
                        # the comment has more than a line  already formatted: ...
                        # ... first line after the instruction ...
                        # ... other lines continuing the comment without instruction before
                        # TODO implement
                        # TODO print print first line complete and just comments on single lines aline
                        # TODO put after next print outside the if so treaats the comments only

                        comment = "" # placefolder for now
                        break
                    
                    print(format_instruction(instruction) + get_normalized_comment(comment, col_inner_count))
                    break
                elif cols_count == 2:
                    # usually just addresses followed by data definitions with no comments: ...
                    # ... print with CR ...
                    # ... skip to the next
                    instruction = cols_list[i].contents[0].get_text(strip=True)
                    print(format_instruction(instruction))
                    break
            elif col_inner_count > 1:
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
