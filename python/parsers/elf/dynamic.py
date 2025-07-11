import utils
from packer import Packer


class DynamicEntry(Packer):
    D_TAG_T = {
        0: 'DT_NULL',
        1: 'DT_NEEDED',
        2: 'DT_PLTRELSZ',
        4: 'DT_HASH',
        5: 'DT_STRTAB',
        6: 'DT_SYMTAB',
    }

    def __init__(self):
        super().__init__(
            {
                "d_tag": 4,
                "d_val": 2,
                "d_ptr": 4,
                "d_off": 4
            },
            {
                "d_tag": 8,
                "d_val": 2,
                "d_ptr": 4
            }
        )

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20s", self.get_value("d_tag"), table=DynamicEntry.D_TAG_T)
        out += utils.formatter2("%-10x", self.get_value("d_val"))
        out += utils.formatter2("%-10x", self.get_value("d_ptr"))
        out += utils.formatter2("%-20s", self.get_value("d_off") if self.key_exists("d_off") else "NONE")
        return out


class Dynamic:
    def __init__(self, section_header, section_data):
        self.entries = []
        count = int(section_data.get_size() / section_header.get_entry_size())
        for sidx in range(count):
            _start = sidx * section_header.get_entry_size()
            _end = _start + section_header.get_entry_size()
            entry = DynamicEntry()
            binary = section_data.get_data()
            entry.unpack(binary[_start:_end])
            self.entries.append(entry)

    def get_column_titles(self):
        out = ""
        out += utils.formatter2("%-20s", "[Tag]")
        out += utils.formatter2("%-10s", "[Value]")
        out += utils.formatter2("%-10s", "[Pointer]")
        out += utils.formatter2("%-20s", "[Offset]")
        return out

    def get_entries(self):
        return self.entries
