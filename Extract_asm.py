import sys
import os
from pathlib import Path
import operator
import functools

from bs4 import BeautifulSoup
from bs4 import element


WIDTH_ADDRESS = 8
WIDTH_INSTRUCTION = 24
WIDTH_COMMENT = 100

DELIMITER_SPLIT_COMMENT = "..."
PRE_DOTS = DELIMITER_SPLIT_COMMENT + " "
POST_DOTS = " " + DELIMITER_SPLIT_COMMENT
DELIMITER_COMMENT = ";"
DELIMITER_LEFT = DELIMITER_COMMENT + " "
DELIMITER_RIGHT = " " + DELIMITER_COMMENT

COL_INDEX_ADDRESS = 0
COL_INDEX_INSTRUCTION = 1
COL_INDEX_COMMENT= 2

# this program is for extracting ASM code from a se of specific files ...
# ... it is notintended to be a generic use one ...
# ... the ifs maze reflect a lot of inconsistencies, exceptions, and errors on the HTML page it parses

def process(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        error_and_exit(f"Error: The file '{file}' was not found.")
    except IOError as e:
        error_and_exit(f"Error reading file '{file}': {e}")

    soup = BeautifulSoup(content, 'html.parser')
    # TODO process assembly-section-title class
    # TODO process debug-note class
    # TODO Process comments with ↓,→,←, and → and other non ASCII chars that macroassembles does not accept

    # code_lines = soup.find_all('div', class_='assembly-row-combined')
    div_classes = 'div.assembly-row-combined, h2.assembly-section-title, p.debug-note'
    code_lines = soup.select(div_classes)

    if code_lines:
        for code_line in code_lines:
            process_classes(code_line)
    else:
        pass

def process_classes(code_line):
    classes = code_line.attrs["class"]

    if "assembly-row-combined" in classes:
        process_assembly_row_combined(code_line)
    elif "assembly-section-title" in classes:
        process_assembly_section_title(code_line)
    elif "debug-note" in classes:
        process_debug_note(code_line)
    else:
        pass

def process_assembly_section_title(code_line):
    dashes_count = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - 2*len(DELIMITER_COMMENT)
    box = f"{DELIMITER_COMMENT}{'-'*(dashes_count)}{DELIMITER_COMMENT}"
    box_space = f"{DELIMITER_COMMENT}{' '*(dashes_count)}{DELIMITER_COMMENT}"

    delimiters_width = len(DELIMITER_LEFT) + len(DELIMITER_RIGHT)
    text_width = WIDTH_ADDRESS + WIDTH_INSTRUCTION + WIDTH_COMMENT - delimiters_width

    # remove symbol of clipboard at the end of title
    code_line.contents[len(code_line.contents)-1].extract()

    text = code_line.get_text()
    text = text.replace("\r", "").replace("\n","")
    lines = get_comment_lines(text, text_width)
    
    print()
    print(box)
    print(box_space)
    for line in lines:
        print(f"{DELIMITER_LEFT}{line:<{text_width}}{DELIMITER_RIGHT}")
    print(box_space)
    print(box)
    print()

def process_debug_note(code_line):
    # TODO this is a template put the text in the middle
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
    lines = get_comment_lines(text, text_width)

    print()
    print(box)
    for line in lines:
        print(f"{' '*spaces_count}{DELIMITER_LEFT}{line:<{text_width}}{DELIMITER_RIGHT}")
    print(box)
    print()

def process_assembly_row_combined(code_line):
    # TODO fix wrong parts as wrongs addresses or repeated parts using a skip list depending on the file
    # TODO process comments as box titles
    # TODO process comments yellow boxes

    # easier to have code_line for debugging and error messages

    # it is needed to know the number of elements prior so I avoid lazy evaluation ...
    # ... at this point there will be about 3 elements tops so it is not a problem
    cols = list(code_line.children)
    cols_count = len(cols)

    if case1general.condition(cols_count):
        cols, cols_count = case1general(cols)

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
    if case1col1.condition(col_address_count):
        case1col1(col_address)
    elif case2col1.condition(col_address_count, col_instruction_count):
        end = case2col1(col_address, col_instruction, col_comment)
        if end: return
    elif case3col1.condition(col_address_count, col_instruction_count):
        case3col1(col_address, col_instruction, col_comment)
    else:
        error_and_exit(f"Unexpected format: '{code_line.decode_contents()}'")

    # column 1 instruction
    if case1col2.condition(col_instruction_count, col_instruction):
        case1col2(col_instruction)
    elif case2col2.condition(col_instruction_count, col_instruction):
        end = case2col2(col_instruction)
        if end: return
    elif case3col2.condition(col_instruction_count):
        case3col2(col_instruction)
    elif case4col2.condition(col_instruction_count, col_instruction):
        end = case4col2(col_address, col_instruction, col_comment)
        if end: return
    elif case5col2.condition(col_instruction_count, col_instruction):
        case5col2(col_instruction)
    elif case6col2.condition(col_instruction_count, col_instruction):
        case6col2(col_instruction)
    elif case7col2.condition(col_instruction_count, col_comment_count):
        end = case7col2(col_address, col_instruction, col_comment)
        if end: return
    else:
        error_and_exit(f"Unexpected format: '{code_line.decode_contents()}'")

    # column 2 comments
    if case1col3.condition(col_comment_count):
        case1col3()
    elif case2col3.condition(col_comment_count):
        case2col3(col_comment)
    elif case3col3.condition(col_comment_count):
        case3col3(col_comment)
    else:
       error_and_exit(f"Unexpected format: '{code_line.decode_contents()}'")
    
def call_count(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls_count += 1
        return func(*args, **kwargs)
    
    wrapper.calls_count = 0
    return wrapper

# attributes in funtions are only initialized the first time tunction is called...
# ... using a decorator that is run at definition I can use them,
def with_condition(condition):
    def decorator(func):
        func.condition = condition
        return func
    return decorator

@call_count
@with_condition(lambda cols_count: cols_count == 4)
def case1general(cols):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>067FH</div>
    #       <div>CP 22H</div>
    #       <div>CP 22H</div>
    #       <div>Compare the value held in Register A against 22H (ASCII: <span class="code">"</span>). Results: If Register A equals ", the Z FLAG is set; otherwise, the NZ FLAG is set.</div>
    #   </div>
    
    # this is an error on the page formatting: 
    # ... you can ignore the second DIV if it repeats the instruction ...
    # ... the repeat was inadvertly put as comment garbling format ...
    # ... remove it
    if cols[1].get_text() != cols[2].get_text():
        error_and_exit(f"Unexpected format: repeatded instruction does not match: '{cols[1].get_text()}', '{cols[2].get_text()}'.")

    cols.pop(2)

    return cols, len(cols)

@call_count
@with_condition(lambda col_address_count: col_address_count == 1)
def case1col1(col_address):
    # examples:
    # 
    #   <div class="assembly-row-combined">
    #       <div>0000H</div>
    #       <div>DI</div>
    #       <div>Disable Interrupts.</div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       <div>0000H</div>
    #       <div>DI</div>
    #       <div>Disable Interrupts.</div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       <div>000AH</div>
    #       <div>CP (HL)</div>
    #       <div>Compare  the next non-space character (held in Register A) against the value held at the top of the 
    #           stack (i..e, in the memory location pointed to by  the value held in Register Pair HL).  Results: 
    #           <ul>
    #               <li>If Register A equals the value held in Register (HL), the Z FLAG is set.</li>
    #               <li>If A &lt; (HL), the CARRY FLAG will be set.</li>
    #               <li>if A &gt;= (HL), the NO CARRY FLAG will be set.</li>
    #           </ul>
    #       </div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       <div>0EB2H</div>
    #       <div>DEFB 40H E7H 4DH</div>
    #   </div>
    
    # normal case: one address
    address = col_address.contents[0]
    if not is_address_valid(address):
        # TODO if address is 015EH set flag to skip next repeat with a return until it reaches 015EH when the flag is reset ...
        # TODO ... there are several errors on the page at 
        # TODO ... 0155H, 0249H, 0287H, 0842H, 08B6H
        # TODO return is here so we can treat all cases and test remove when ready
        return
        error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{is_address_valid.prev_address_dec:X}H'.")

    print(format_address(address), end="")

@call_count
@with_condition(lambda col_address_count, col_instruction_count: col_address_count in [3, 5] and col_address_count == col_instruction_count)
def case2col1(col_address, col_instruction, col_comment):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>0084H<br/>0085H</div>
    #       <div>RLA
    #            <br/>
    #            RLA
    #       </div>
    #       <div>Rotate the bits of Register left (i.e., lower bit moves higher) two bit positions so that A will correspond to 00H (Variable A) to 64H (Variable Z)</div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       <div>0AA2H
    #            <br/>
    #            0AA3H
    #            <br/>
    #            0AA4H
    #       </div>
    #       <div>LD A,H
    #            <br/>
    #            CPL
    #            <br/>
    #            LD H,A
    #       </div>
    #       <div>Invert the bits in Register H.  If H started as 41H, which is 01000001, then the CPL would be 10111110, or 0BEH</div>
    #   </div>
    
    # an alternate format: ..
    # ... several addresses in one tag on column 1 separated by </br>
    # ... several instructions in one tag on column 2 separated by </br>
    # ... so the comment is applied to those group of addresses and instructions

    # comment here has one line only if it has more change to get as case4col2
    if len(col_comment.contents) > 1:
         error_and_exit(f"Comment lines expected: '1', found: '{len(col_comment.contents)}'.")

    col_address_count = len(col_address.contents)
    lines_count = get_lines_from_lines_spaces(col_address_count)
    text_width = WIDTH_COMMENT - len(DELIMITER_LEFT)
    comment = col_comment.contents[0]
    comments = get_comment_lines(comment, text_width, lines_count)

    lines = []
    index_line = 0
    for index in range(0, col_address_count):
        address = col_address.contents[index].get_text(strip=True)
        instruction = col_instruction.contents[index].get_text(strip=True)

        if address == "" and instruction == "":
            # it is a </br> skip it
            continue
 
        if operator.xor(address == "", instruction == ""):
            # address and instruction lists are inconsistent
            error_and_exit(f"Inconsistent addresses: '{col_address.contents[index]}' and instruction: '{col_instruction.contents[index_line]:}'.")

        if not is_address_valid(address):
            # TODO ... there are several errors on the page at 
            # TODO ... 04ECH, 0501H, 066AAH, 08D4H, 0A89H, 0AB1H, 0E4AH
            # TODO return is here so we can treat all cases and test remove when ready
            return
            error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{is_address_valid.prev_address_dec:X}H'.")

        lines.append(f"{format_address(address)}{format_instruction(instruction)}{DELIMITER_LEFT}{comments[index_line]}")
        index_line += 1
        
    for line in lines:
        print(line)

    # there are still not printed comment lines
    if len (comments) > len(lines):
        for index in range(len(lines), len(comments)):
            print(f"{' '*(WIDTH_ADDRESS + WIDTH_INSTRUCTION)}{DELIMITER_LEFT}{comments[index]}")

    return True

@call_count
@with_condition(lambda col_address_count, col_instruction_count: col_address_count == 3 and col_instruction_count == 1)
def case3col1(col_address, col_instruction, col_comment):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>0BFAH<br/>0BFBH</div>
    #       <div>DEC HL</div>
    #       <div>Back up HL (i.e., the pointer to the variable in RAM) two bytes.</div>
    #   </div>

    # a weird single case where at 0BFA the DEC HL instruction is given ...
    # ... and the next address follows with no instruction ...
    # ... comparing with with ROM image the instruction repeats twice, what matches the comment about decremented twice
    addresses = col_address.contents
    address1 = addresses[0].get_text(strip=True)
    address2 = addresses[1].get_text(strip=True)
    address3 = addresses[2].get_text(strip=True)

    f_address1_valid = is_address_valid(address1)
    if not f_address1_valid:
        error_and_exit(f"Inconsistent addresses: current: '{address1}', previous: '{is_address_valid.prev_address_dec:X}H'.")

    f_address3_valid = is_address_valid(address3)
    if not f_address3_valid:
        error_and_exit(f"Inconsistent addresses: current: '{address3}', previous: '{is_address_valid.prev_address_dec:X}H'.")

    if not(is_address_valid.address_dec - is_address_valid.prev_address_dec == 1 and address2 == ""):
        error_and_exit(f"Unexpected format: '{col_address.decode_contents()}'.")

    lines = []
    instruction = col_instruction.contents[0].get_text(strip=True)
    comments = get_comment_lines(col_comment.contents[0], WIDTH_COMMENT - len(DELIMITER_LEFT))
    comment = comments[0]

    if len(comments) > 1 or len(col_comment.contents) > 1:
        error_and_exit(f"Unexpected comment format: '{col_address.decode_contents()}'.")

    lines.append(format_address(address1) + format_instruction(instruction) + f"{DELIMITER_LEFT}{comment}")
    lines.append(format_address(address3) + format_instruction(instruction) + f"{DELIMITER_LEFT}{DELIMITER_SPLIT_COMMENT}")

    for line in lines:
        print(line)

    print()

@call_count
@with_condition(lambda col_instruction_count, col_instruction: col_instruction_count == 1 and is_quoted_string(col_instruction.contents[0].get_text()))
def case1col2(col_instruction):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>01C0H</div>
    #       <div>"BREAK AT"</div>
    #       <div></div>
    #   </div>

    # literal without DEFM
    instruction = col_instruction.get_text(strip=True)
    instruction = f"DEFM {instruction}"
    print(format_instruction(instruction), end="")

@call_count
@with_condition(lambda col_instruction_count, col_instruction: col_instruction_count == 1 and is_quoted_string_with_cr(col_instruction.contents[0].get_text()))
def case2col2(col_instruction):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>01A9H</div>
    #       <div>"HOW?" + 0DH</div>
    #       <div></div>
    #   </div>

    # string literal followed by CR (like "HOW?" + 0DH) used for error messages: make it like DEFB "HOW?", 0DH
    instructions = col_instruction.get_text(strip=True).split("+")
    instruction = f"DEFB {instructions[0].strip()}, {instructions[1].strip()}"
    print(format_instruction(instruction))
    return True

@call_count
@with_condition(lambda col_instruction_count: col_instruction_count == 1)
def case3col2(col_instruction):
    # examples:
    #
    #   <div class="assembly-row-combined">
    #       <div>01A9H</div>
    #       <div>"HOW?" + 0DH</div>
    #       <div></div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       <div>0000H</div>
    #       <div>DI</div>
    #       <div>Disable Interrupts.</div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       <div>000AH</div>
    #       <div>CP (HL)</div>
    #       <div>Compare the next non-space character (held in Register A) against the value held at the top of the 
    #           stack (i..e, in the memory location pointed to by  the value held in Register Pair HL).  Results: 
    #           <ul>
    #               <li>If Register A equals the value held in Register (HL), the Z FLAG is set.</li>
    #               <li>If A &lt; (HL), the CARRY FLAG will be set.</li>
    #               <li>if A &gt;= (HL), the NO CARRY FLAG will be set.</li>
    #           </ul>
    #       </div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       <div>0EB2H</div>
    #       <div>DEFB 40H E7H 4DH</div>
    #   </div>

    # normal case: one instruction
    instruction = col_instruction.contents[0].get_text(strip=True)
    print(format_instruction(instruction), end="")

@call_count
@with_condition(lambda col_instruction_count, col_instruction: col_instruction_count > 1 and col_instruction.contents[0][0:3] == "RST")
def case4col2(col_address, col_instruction, col_comment):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>0044H</div>
    #       <div>RST 08H
    #            <br/>
    #            28H
    #            <br/>
    #            <a class="memory-link" href="#0081H">3AH</a>
    #       </div>
    #       <div>Next we need to check for the array, which means a parenthesis. We do this a  call to RST 08H with 
    #            parameters of "(" and an offset of 3AH.  RST 08H will move to the next non-space character and check 
    #            it against 28H (which is a "(").  If there is no match, jump to the return (of the next instruction, 
    #            i.e. 0047H) + 3AH instructions (which would be 0081H).
    #       </div>
    #   </div>

    # an RST followed by two bytes that are parameters skipped by the called routine manipulating PC
    col_instruction_count = len(col_instruction.contents)

    comment = ""
    for content in col_comment.contents:
        cur_content = content.get_text()
        if cur_content == content:
            comment += cur_content
        else:
            # add spaces around if it is inside a tag
            comment += f" {cur_content} "

    text_width = WIDTH_COMMENT - len(DELIMITER_LEFT)
    lines_count = get_lines_from_lines_spaces(col_instruction_count)
    # comments = get_normalized_comment(comment, col_instruction_count)
    comments = get_comment_lines(comment, text_width, lines_count)

    lines = []
    address_dec, _ = hex2dec(col_address.contents[0][:-1])
    index_line = 0
    for index in range(0, col_instruction_count):
        instruction = col_instruction.contents[index].get_text(strip=True)
        if instruction == "":
            # it is a </br> skipt it
            continue

        if index_line == 0:
            # first line is a normal one: address already printed and, just the instruction ...
            lines.append(format_instruction(instruction) + comments[index_line])
        else:
            # ... next lines need to print the adress and, are data so a DEFB is needed
            instruction = f"DEFB {instruction}"
            lines.append(f"{format_address(f'{address_dec:04X}H')}{format_instruction(instruction)}{DELIMITER_LEFT}{comments[index_line]}")

        address_dec+=1
        index_line +=1

    for line in lines:
        print(line)

    # there are still not printed comment lines
    if len (comments) > len(lines):
        for index in range(len(lines), len(comments)):
            print(f"{' '*(WIDTH_ADDRESS + WIDTH_INSTRUCTION)}{DELIMITER_LEFT}{comments[index]}")
    
    return True

@call_count
@with_condition(lambda col_instruction_count, col_instruction: col_instruction_count > 1 and col_instruction.contents[0][0] == '"')
def case5col2(col_instruction):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>032DH</div>
    #       <div>"<span class="code">&gt;</span>"</div>
    #       <div></div>
    #   </div>

    # two quotation marks enclosing a single character like <, >, =
    instruction = col_instruction.get_text(strip=True)
    instruction = f"DEFM {instruction}"
    print(format_instruction(instruction), end="")

@call_count
@with_condition(lambda col_instruction_count, col_instruction: col_instruction_count > 1 and is_hex(col_instruction.contents[0][-3:-1]))
def case6col2(col_instruction):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>047AH</div>
    #       <div>LD A,20H
    #            <br/>
    #            LD A," "
    #       </div>
    #       <div>Let Register A equal 20H (ASCII: <span class="code">SPACE</span>).</div>
    #   </div>
    #

    # the instruction is repeated below with no address and with an two byte hexadecimal immediate 
    # ... in ascii or binary form alone or with the instruction ...
    # ... print only the first instruction
    instruction = col_instruction.contents[0].get_text(strip=True)
    print(format_instruction(instruction), end="")

@call_count
@with_condition(lambda col_instruction_count, col_comment_count: col_instruction_count > 1 and col_comment_count == 1)
def case7col2(col_address, col_instruction, col_comment):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>01ECH</div>
    #       <div>LD A,H
    #            <br/>
    #            OR L
    #       </div>
    #       <div>Since the Z-80 cannot test Register Pair HL against zero, the common trick is Register L. 
    #            Only if both Register H and Register L were zero can the Z FLAG be set.
    #       </div>
    #   </div>

    # a instruction is followed by another with the address only in the first one ...
    # ... they are grouped with only one comment because they execute a single operation
    
    # just one comment as it is in the condition of the case
    col_instruction_count = len(col_instruction.contents)
    comment = col_comment.contents[0]
    comments = get_comment_lines(comment, WIDTH_COMMENT - len(DELIMITER_LEFT))

    lines = []
    address_dec, _ = hex2dec(col_address.contents[0][:-1])
    index_line = 0
    for index in range(0, col_instruction_count):
        instruction = col_instruction.contents[index].get_text(strip=True)
        if instruction == "":
            # it is a </br> skipt it
            continue

        if index_line == 0:
            # first line is a normal one: address already printed and, just the instruction ...
            lines.append(format_instruction(instruction) + comments[index_line])
        else:
            # ... next lines need to print the adress and, are data so a DEFB is needed
            lines.append(format_address(f"{address_dec:04X}H") + format_instruction(instruction) + comments[index_line])

        address_dec+=1
        index_line +=1

    for line in lines:
        print(line)
    
    return True

@call_count
@with_condition(lambda col_comment_count: col_comment_count == 0)
def case1col3():
    # exemplo:
    #
    #   <div class="assembly-row-combined">
    #       <div>01C0H</div>
    #       <div>"BREAK AT"</div>
    #       <div></div>
    #   </div>
    #

    # there is no comment
    print()

@call_count
@with_condition(lambda col_comment_count: col_comment_count == 1)
def case2col3(col_comment):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>0000H</div>
    #       <div>DI</div>
    #       <div>Disable Interrupts.</div>
    #   </div>

    # normal case one comment
    comments = get_comment_lines(col_comment.contents[0], WIDTH_COMMENT - len(DELIMITER_LEFT))
    for index, comment in enumerate(comments):
        if index == 0:
            print(f"{DELIMITER_LEFT}{comment}")
        else:
            print(f"{' '*(WIDTH_ADDRESS+WIDTH_INSTRUCTION)}{DELIMITER_LEFT}{comment}")

        if len(comments) != 1 and index == len(comments) - 1:
            print()

@call_count
@with_condition(lambda col_comment_count: col_comment_count > 1)
def case3col3(col_comment):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>000AH</div>
    #       <div>CP (HL)</div>
    #       <div>Compare  the next non-space character (held in Register A) against the value held at the top of the stack (i..e, 
    #            in the memory location pointed to by the value held in Register Pair HL).  
    #            Results: 
    #            <ul>
    #               <li>If Register A equals the value held in Register (HL), the Z FLAG is set.</li>
    #               <li>If A &lt; (HL), the CARRY FLAG will be set.</li>
    #               <li>if A &gt;= (HL), the NO CARRY FLAG will be set.</li>
    #           </ul>
    #       </div>
    #   </div>
    #
    #   <div class="assembly-row-combined">
    #       div>0B8AH</div>
    #       <div>
    #           <a class="memory-link" href="#0BA5H">
    #           CALL 0BA5H
    #           </a>
    #       </div>
    #       <div>GOSUB to 0BA5H to check for a 
    #            <kbd>
    #            SHIFT
    #            </kbd>
    #            , set the FLAGS, and put Register B into Register A.
    #       </div>
    #   </div>

    # ... one case:
    # ... the comment has more than a line  already formatted: ...
    # ...    first line after the instruction ...
    # ...    other lines continuing the comment without instruction before ...
    # ... other case ...
    # ...    some foprmatting like kbd that spreads it in lines

    # add lines wiithout spliting trivial tags just removing them
    temp_lines = []
    for content in col_comment.contents:
        if type(content) is element.NavigableString:
            if len(temp_lines) == 0:
                temp_lines.append(content.get_text(strip=True))
            else:
                temp_lines[-1] += f" {content.get_text(strip=True)} "

        elif type(content) is element.Tag and content.name == "ul":
            for index, comment in enumerate(content.contents):
                comment_text = comment.get_text()
                if comment_text != "":
                    temp_lines.append(comment_text)

        elif type(content) is element.Tag and content.name in ["span", "b", "a", "br", "kbd"]:
            # trivial tags are not split
            # TODO if this is the forst one this will break as temp_lines[-1] does not exist as temp_lines is an empty list
            temp_lines[-1] += f" {content.get_text()} "
        elif type(content) is element.Tag:
            error_and_exit(f"Unexpected tag: '{content.name}'")
        else:
            error_and_exit(f"Unexpected format: '{col_comment.decode_contents()}'")

    # split long lines
    split_lines = []
    line_width =  WIDTH_COMMENT - len(DELIMITER_LEFT)
    for line in temp_lines:
        partial_split_lines = get_split_comment(line, line_width)
        for split_line in partial_split_lines:
            split_lines.append(split_line)

    lines = add_split_comment_delimiters(split_lines)
    
    for index, line in enumerate(lines):
        if index == 0:
            print(f"{DELIMITER_LEFT}{line}")
        else:
            print(f"{' '*(WIDTH_ADDRESS+WIDTH_INSTRUCTION)}{DELIMITER_LEFT}{line}")
    
    print()

def error_and_exit(message):
        print(message, file=sys.stderr)
        sys.exit(1)

def format_address(address):
    return f"{address:<{WIDTH_ADDRESS}}"

def format_instruction(instruction):
    return f"{instruction:<{WIDTH_INSTRUCTION}}"

def get_split_comment(comment, line_width, lines_count=0):
    comment = comment.replace("\r", "").replace("\n","").replace("  "," ")

    comment_size = len(comment)
    if comment_size <= line_width and not lines_count > 1:
        lines = [comment]
        # while lines_count > len(lines):
        #     lines.append("")

        return lines
    
    # if the comment is divided in lines make space for the dots
    line_width = line_width - len(PRE_DOTS) - len(POST_DOTS)

    # find first space in comment from WIDTH_COMMENT from end to start
    lines = []
    prev_cut_point = 0
    remaining_comment = comment
    while  len(remaining_comment) > 0:
        if len(remaining_comment) <= line_width:
            lines.append(remaining_comment.strip())
            break

        cur_line = remaining_comment[prev_cut_point:line_width]
        cur_reversed_line = cur_line[::-1]
        cut_point = len(cur_line) - cur_reversed_line.find(" ")

        line = remaining_comment[prev_cut_point:cut_point]
        lines.append(line.strip())
        remaining_comment = remaining_comment[cut_point:]

    while lines_count > len(lines):
        lines.append("")

    return lines

def add_split_comment_delimiters(lines):
    out_lines = []
    for i, line in enumerate(lines):
        if i == 0 and not i == len(lines) - 1: prefix, suffix = "", POST_DOTS # first not last
        if 0 < i < len(lines) - 1: prefix, suffix = PRE_DOTS, POST_DOTS # not first not last
        if not i == 0 and i == len(lines) - 1: prefix, suffix = PRE_DOTS, "" # not first last
        if i == 0 and i == len(lines) - 1: prefix, suffix = "", "" # first and last (just one line)

        out_lines.append(prefix + line.strip() + suffix)

    return out_lines

def get_lines_from_lines_spaces(lines_spaces_count):
    # multiple lines have </br> between instructions in the list that are discarded ...
    # ... so normalize to take just the comment lines
    lines_count = (lines_spaces_count // 2) + 1
    return lines_count

def get_comment_lines(comment, line_width, lines_count=0):
    lines = get_split_comment(comment, line_width, lines_count)
    comment_lines = add_split_comment_delimiters(lines)
    return comment_lines

def hex2dec(s):
    if not s:  # int() will not work on empty strings
        return None, False
    try:
        i = int(s, 16)
        return i, True
    except ValueError:
        return None, False

def is_hex(s):
    _, f = hex2dec(s)
    return f
    
def is_address_valid(address):
    # checks if: ...
    # ... address is a valid hexadecimal number folowed by H and ...
    # ... addresses always crescent
    if not hasattr(is_address_valid, "prev_address_dec"):
        is_address_valid.prev_address = "-1H"

    address_dec, f_hex_adddress = hex2dec(address[:-1])
    prev_address_dec, f_hex_prev_adddress = hex2dec(is_address_valid.prev_address[:-1])

    is_address_valid.address_dec = address_dec
    is_address_valid.prev_address_dec = prev_address_dec
    is_address_valid.prev_address = address
    return f_hex_adddress and f_hex_prev_adddress and (0 <= address_dec <= 65535 and address_dec > prev_address_dec)

def is_quoted_string(s):
    return s[0] == '"' and s[-1] == '"'

def is_quoted_string_with_cr(s):
    return s.replace(" ", "")[-5:] == '"+0DH'

def main():
    path = "."
    nparams = len(sys.argv)
    if nparams > 1:
        path = sys.argv[1]
    if nparams > 2:
        print("Too many parameters, only the first one will be used.")

    script_dir = Path(__file__).resolve().parent
    path = os.path.join(script_dir, path)

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
