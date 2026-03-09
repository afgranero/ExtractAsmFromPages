import operator

from bs4 import element

import check_strings as cs
from constants import *
from decorators import *
import fix_addresses as fa
import format_output as fo
import helpers as h
from modal_constants import WIDTH_ADDRESS
import split_comments as sc



@call_count
@with_condition(lambda cols_count: cols_count == 4)
def general_case1(cols):
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
        h.error_and_exit(f"Unexpected format: repeatded instruction does not match: '{cols[1].get_text()}', '{cols[2].get_text()}'.")

    cols.pop(2)

    return cols, len(cols)


@call_count
@with_condition(lambda col_address_count: col_address_count == 1)
def address_case1(col_address, hash):
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

    action, new_address, extra = fa.fix_address(address, hash)
    if action == fa.SKIP:
        return True
    elif action == fa.SUBSTITUTE:
        address = new_address
    elif action == fa.INSERT_NEXT:
        fa.fix_address.next = (new_address, extra)

    if not cs.is_address_valid(address):
        h.error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{cs.is_address_valid.prev_address_dec:X}H'.")

    print(fo.format_address(address), end="")
    return False


@call_count
@with_condition(lambda col_address_count, col_instruction_count: col_address_count in [3, 5] and col_address_count == col_instruction_count)
def address_case2(col_address, col_instruction, col_comment, hash):
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
         h.error_and_exit(f"Comment lines expected: '1', found: '{len(col_comment.contents)}'.")

    col_address_count = len(col_address.contents)
    lines_count = sc.get_lines_from_lines_spaces(col_address_count)
    text_width = WIDTH_COMMENT - len(DELIMITER_LEFT)
    comment = col_comment.contents[0]
    comments = sc.get_comment_lines(comment, text_width, lines_count)

    lines = []
    index_line = 0
    for index in range(0, col_address_count):
        address = col_address.contents[index].get_text(strip=True)
        action, new_address, extra = fa.fix_address(address, hash)
        if action == fa.SKIP:
            return True
        elif action == fa.SUBSTITUTE:
            address = new_address
        elif action == fa.INSERT_NEXT:
            fa.fix_address.next = (new_address, extra)

        instruction = col_instruction.contents[index].get_text(strip=True)

        if address == "" and instruction == "":
            # it is a </br> skip it
            continue

        if operator.xor(address == "", instruction == ""):
            # address and instruction lists are inconsistent
            h.error_and_exit(f"Inconsistent addresses: '{col_address.contents[index]}' and instruction: '{col_instruction.contents[index_line]:}'.")

        if not cs.is_address_valid(address):
            h.error_and_exit(f"Inconsistent addresses: current: '{address}', previous: '{cs.is_address_valid.prev_address_dec:X}H'.")

        lines.append(f"{fo.format_address(address)}{fo.format_instruction(instruction)}{DELIMITER_LEFT}{comments[index_line]}")
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
def address_case3(col_address, col_instruction, col_comment):
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

    f_address1_valid = cs.is_address_valid(address1)
    if not f_address1_valid:
        h.error_and_exit(f"Inconsistent addresses: current: '{address1}', previous: '{cs.is_address_valid.prev_address_dec:X}H'.")

    f_address3_valid = cs.is_address_valid(address3)
    if not f_address3_valid:
        h.error_and_exit(f"Inconsistent addresses: current: '{address3}', previous: '{cs.is_address_valid.prev_address_dec:X}H'.")

    if not(cs.is_address_valid.address_dec - cs.is_address_valid.prev_address_dec == 1 and address2 == ""):
        h.error_and_exit(f"Unexpected format: '{col_address.decode_contents()}'.")

    lines = []
    instruction = col_instruction.contents[0].get_text(strip=True)
    comments = sc.get_comment_lines(col_comment.contents[0], WIDTH_COMMENT - len(DELIMITER_LEFT))
    comment = comments[0]

    if len(comments) > 1 or len(col_comment.contents) > 1:
        h.error_and_exit(f"Unexpected comment format: '{col_address.decode_contents()}'.")

    lines.append(fo.format_address(address1) + fo.format_instruction(instruction) + f"{DELIMITER_LEFT}{comment}")
    lines.append(fo.format_address(address3) + fo.format_instruction(instruction) + f"{DELIMITER_LEFT}{DELIMITER_SPLIT_COMMENT}")

    for line in lines:
        print(line)

    print()


@call_count
@with_condition(lambda col_instruction_count: col_instruction_count == 1)
def instruction_case1(col_instruction):
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
    print(fo.format_instruction(instruction), end="")


@call_count
@with_condition(lambda col_instruction_count, col_instruction: col_instruction_count > 1 and col_instruction.contents[0][0:3] == "RST")
def instruction_case2(col_address, col_instruction, col_comment):
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
    lines_count = sc.get_lines_from_lines_spaces(col_instruction_count)
    # comments = get_normalized_comment(comment, col_instruction_count)
    comments = sc.get_comment_lines(comment, text_width, lines_count)

    lines = []
    address_dec, _ = cs.hex2dec(col_address.contents[0][:-1])
    index_line = 0
    for index in range(0, col_instruction_count):
        instruction = col_instruction.contents[index].get_text(strip=True)
        if instruction == "":
            # it is a </br> skipt it
            continue

        if index_line == 0:
            # first line is a normal one: address already printed and, just the instruction ...
            lines.append(f"{fo.format_instruction(instruction)}{DELIMITER_LEFT}{comments[index_line]}")
        else:
            # ... next lines need to print the adress and, are data so a DEFB is needed
            lines.append(f"{fo.format_address(f'{address_dec:04X}H')}{fo.format_instruction(instruction)}{DELIMITER_LEFT}{comments[index_line]}")

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
def instruction_case3(col_instruction):
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
    print(fo.format_instruction(instruction), end="")


@call_count
@with_condition(lambda col_instruction_count, col_instruction: col_instruction_count > 1 and cs.is_hex(col_instruction.contents[0][-3:-1]))
def instruction_case4(col_instruction):
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
    print(fo.format_instruction(instruction), end="")


@call_count
@with_condition(lambda col_instruction_count, col_comment_count: col_instruction_count > 1 and col_comment_count == 1)
def instruction_case5(col_address, col_instruction, col_comment):
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
    comments = sc.get_comment_lines(comment, WIDTH_COMMENT - len(DELIMITER_LEFT))

    lines = []
    address_dec, _ = cs.hex2dec(col_address.contents[0][:-1])
    index_line = 0
    for index in range(0, col_instruction_count):
        instruction = col_instruction.contents[index].get_text(strip=True)
        if instruction == "":
            # it is a </br> skipt it
            continue

        if index_line == 0:
            # first line is a normal one: address already printed and, just the instruction ...
            lines.append(f"{fo.format_instruction(instruction)}{DELIMITER_LEFT}{comments[index_line]}")
        else:
            # ... next lines need to print the adress and, are data so a DEFB is needed
            lines.append(f"{fo.format_address(f'{address_dec:04X}H')}{fo.format_instruction(instruction)}{DELIMITER_LEFT}{comments[index_line]}")

        address_dec+=1
        index_line +=1

    for line in lines:
        print(line)

    return True


@call_count
@with_condition(lambda col_comment_count: col_comment_count == 0)
def comment_case1():
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
def comment_case2(col_comment):
    # example:
    #
    #   <div class="assembly-row-combined">
    #       <div>0000H</div>
    #       <div>DI</div>
    #       <div>Disable Interrupts.</div>
    #   </div>

    # normal case one comment
    comments = sc.get_comment_lines(col_comment.contents[0], WIDTH_COMMENT - len(DELIMITER_LEFT))
    for index, comment in enumerate(comments):
        if index == 0:
            print(f"{DELIMITER_LEFT}{comment}")
        else:
            print(f"{' '*(WIDTH_ADDRESS+WIDTH_INSTRUCTION)}{DELIMITER_LEFT}{comment}")

        if len(comments) != 1 and index == len(comments) - 1:
            print()


@call_count
@with_condition(lambda col_comment_count: col_comment_count > 1)
def comment_case3(col_comment):
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
            if len(temp_lines) == 0:
                h.error_and_exit(f"Unexpected format: '{col_comment.decode_contents()}'")

            # trivial tags are not split
            temp_lines[-1] += f" {content.get_text()} "
        elif type(content) is element.Tag:
            h.error_and_exit(f"Unexpected tag: '{content.name}'")
        else:
            h.error_and_exit(f"Unexpected format: '{col_comment.decode_contents()}'")

    # split long lines
    split_lines = []
    line_width =  WIDTH_COMMENT - len(DELIMITER_LEFT)
    for line in temp_lines:
        partial_split_lines = sc.get_split_comment(line, line_width)
        for split_line in partial_split_lines:
            split_lines.append(split_line)

    lines = sc.add_split_comment_delimiters(split_lines)

    for index, line in enumerate(lines):
        if index == 0:
            print(f"{DELIMITER_LEFT}{line}")
        else:
            print(f"{' '*(WIDTH_ADDRESS+WIDTH_INSTRUCTION)}{DELIMITER_LEFT}{line}")

    print()
