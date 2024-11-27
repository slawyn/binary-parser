import utils
from packer import Packer

class DynamicEntry(Packer):
    D_TAG_SZ = 4
    D_VAL_SZ = 2
    D_PTR_SZ = 4
    D_OFF_SZ = 4

    D_TAG_64SZ = 8
    D_VAL_64SZ = 2
    D_PTR_64SZ = 4

    D_TAG_T = {
        0: 'DT_NULL',
        1: 'DT_NEEDED',
        2: 'DT_PLTRELSZ',
        4: 'DT_HASH',
        5: 'DT_STRTAB',
        6: 'DT_SYMTAB',
    }

    def __init__(self, d_tag=0, d_val=0, d_ptr=0, d_off=0):
        super().__init__(
            {
                "d_tag": d_tag,
                "d_val": d_val,
                "d_ptr": d_ptr,
                "d_off": d_off
            },
            {
                "d_tag": d_tag,
                "d_val": d_val,
                "d_ptr": d_ptr
            }
        )

    def __str__(self):
        out = ""
        out += utils.formatter2("%-20s", self.members["d_tag"],  table=DynamicEntry.D_TAG_T)
        out += utils.formatter2("%-10x", self.members["d_val"])
        out += utils.formatter2("%-10x", self.members["d_ptr"])
        out += utils.formatter2("%-20s", self.members.get("d_off", "NONE"))
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