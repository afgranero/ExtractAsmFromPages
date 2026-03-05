from constants import *
import page_cases as pc


def fix_instruction(instruction):
    if pc.fix_missing_defb.condition(instruction):
        instruction = pc.fix_missing_defb(instruction)
    elif pc.fix_defb_instead_of_defw.condition(instruction):
        instruction = pc.fix_defb_instead_of_defw(instruction)
    return instruction


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