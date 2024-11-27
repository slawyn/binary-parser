import sys
import argparse
from parsers.pe.pe import PeParser
from parsers.elf.elf import ElfParser

from utils import log, load_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')

    parser.add_argument('-i', '--input')
    parser.add_argument('-p', '--print', action='store_true')
    parser.add_argument('-oh', '--ohex')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    try:
        buffer = load_file(args.input)
        elf_type = buffer[0:4] == b"\x7fELF"
        pe_type = buffer[0:2] == b"MZ"
        if elf_type:
            _parser = ElfParser(buffer)
        elif pe_type:
            _parser = PeParser(buffer)
        else:
            raise Exception("ERROR: File type not recognized")
        # Analyze
        if args.print:
            print(_parser)

        # Output
        if args.output:
            _parser.write_data_to_file(file_out=args.output)

    except Exception as e:
        log(e)
