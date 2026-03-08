import argparse
import os
from pathlib import Path

from constants import *
import helpers as h
import modal_constants as mc


def main():
    parser = argparse.ArgumentParser(description="Extract assembler from specific HTML pages.")
    parser.add_argument("path", nargs='?', default=".", help="Path of file or files.")
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

    # this import will access WIDTH_ADDRESS ansd it is here because it will crash if made before initializing it
    from process_classes import process

    script_dir = Path(__file__).resolve().parent
    path = os.path.join(script_dir, args.path)

    files = []
    if os.path.isdir(path):
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() and Path(entry).suffix in [".html", ".htm"]:
                    files.append(entry.name)

    if os.path.isfile(path):
        files.append(path)

    for file in files:
        hash = h.compute_file_hash(file)
        process(file, hash)


if __name__ == "__main__":
    main()
