import argparse
import os
from pathlib import Path

from constants import *
from fix_constants import FIX_LIST, MISSING_CODE
import helpers as h
import modal_constants as mc


def main():
    parser = argparse.ArgumentParser(description="Extract assembler from specific HTML pages.")
    parser.add_argument("path", nargs='?', default=".", help="Path of input file.")
    parser.add_argument("output_path", nargs='?', default="", help="Path of output file.")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-d", "--disassembler", dest="disassembler_mode", action="store_true",  help="Outputs a disassembler format.")
    group.add_argument("-c", "--assembler",    dest="disassembler_mode", action="store_false", help="Outputs a compilable assembler format.")
    parser.set_defaults(disassembler_mode=True)
    
    args = parser.parse_args()

    mc.set("DISASSEMBLER_MODE", args.disassembler_mode)
    if args.disassembler_mode:
        mc.set("WIDTH_ADDRESS", WIDTH_ADDRESS_DISASSEMBLY_MODE)
    else:
        mc.set("WIDTH_ADDRESS", WIDTH_ADDRESS_COMPILABLE_MODE)

    # TODO make a mode foe z80asm

    # this import will access WIDTH_ADDRESS and it is here because it will crash if made before initializing it
    from process_classes import process


    script_dir = Path(__file__).resolve().parent
    path = os.path.join(script_dir, args.path)

    if args.output_path != "":
        output_path = os.path.join(script_dir, args.output_path)
        output_path_parent = os.path.dirname(output_path)

        if os.path.exists(output_path_parent):
            h.output_to_file_and_stdio(output_path)
        else:
            h.error_and_exit(f"Output file creation directory does not exist: '{output_path_parent}'.")

    if not os.path.exists(path):
        h.error_and_exit(f"Input file or directory does not exist: '{path}'.")

    files = []
    if os.path.isdir(path):
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() and Path(entry).suffix in [".html", ".htm"]:
                    files.append(entry.name)

    if os.path.isfile(path):
        hash = h.compute_file_hash(path)
        # TODO maybe I should have only one dictionary owith file hashes as keys ...
        # TODO ... so there is no way they become inconsistent
        if hash not in FIX_LIST and hash not in MISSING_CODE:
            h.error_and_exit(f"Input file is not one os the specific files expected: '{path}'.")

        files.append(path)

    for file in files:
        hash = h.compute_file_hash(file)
        process(file, hash)


if __name__ == "__main__":
    main()
