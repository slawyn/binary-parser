import sys

from parsers.pe import PeParser
from parsers.elf import ElfParser

from utils import log, load_file


if __name__ == "__main__":
    if len(sys.argv) >= 1:
        in_filename = sys.argv[1]

        try:
            buffer = load_file(in_filename)
            if buffer[0:4] == b"\x7fELF":
                parser = ElfParser(buffer)
                parser.print_all()
            elif buffer[0:2] == b"MZ":
                parser = PeParser(buffer)
                parser.print_all()

        except Exception as e:
            log(e)
