import utils
from packer import Packer

class SymTable:
    def __init__(self, section_header, section_data, linked_str_tab_idx):
        self.symbols = []
        self.linked_str_tab_idx = linked_str_tab_idx
        count = int(section_data.get_size() / section_header.get_entry_size())
        for sidx in range(count):
            _start = sidx * section_header.get_entry_size()
            _end = _start + section_header.get_entry_size()
            symbol = Symbol()
            binary = section_data.get_data()
            symbol.unpack(binary[_start:_end])
            self.symbols.append(symbol)

    def get_entries(self):
        return self.symbols

    def get_column_titles(self):
        out = ""
        out += utils.formatter2("%-10s", "[Value]")
        out += utils.formatter2("%-10s", "[Size]")
        out += utils.formatter2("%-20s", "[Bind]")
        out += utils.formatter2("%-20s", "[Info]")
        out += utils.formatter2("%-20s", "[Other]")
        out += utils.formatter2("%-10s", "[Ndx]")
        out += utils.formatter2("%-10s", "[Name]")
        return out

    def get_strtab_idx(self):
        return self.linked_str_tab_idx

class Symbol(Packer):
    ST_NAME_SZ = 0x4
    ST_VALUE_SZ = 0x4
    ST_SIZE_SZ = 0x4
    ST_INFO_SZ = 0x1
    ST_OTHER_SZ = 0x1
    ST_SHNDX_SZ = 0x4

    ST_NAME_64SZ = 0x4
    ST_INFO_64SZ = 0x1
    ST_OTHER_64SZ = 0x1
    ST_SHNDX_64SZ = 0x2
    ST_VALUE_64SZ = 0x8
    ST_SIZE_64SZ = 0x8

    ST_INFO_BIND_M = 0xF0
    ST_INFO_TYPE_M = 0x0F

    ST_BIND_T = {
        0x00: "STB_LOCAL",
        0x10: "STB_GLOBAL",
        0x20: "STB_WEAK",
        0xA0: "STB_LOOS",
        0xC0: "STB_HIOS",
        0xD0: "STB_LOPROC",
        0xF0: "STB_HIPROC"
    }

    ST_OTHER_T = {
        0: "STV_DEFAULT",
        1: "STV_INTERNAL",
        2: "STV_HIDDEN",
        3: "STV_PROTECTED",
        4: "STV_EXPORTED",
        5: "STV_SINGLETON",
        6: "STV_ELIMINATE"
    }

    ST_TYPE_T = {
        0: "STT_NOTYPE",
        1: "STT_OBJECT",
        2: "STT_FUNC",
        3: "STT_SECTION",
        4: "STT_FILE",
        5: "STT_COMMON",
        6: "STT_TLS",
        10: "STT_LOOS",
        12: "STT_HIOS",
        13: "STT_LOPROC",
        14: "STT_SPARC_REGISTER",
        15: "STT_HIPROC"
    }

    ST_SHNDX_T = {
        0x0000: "SHN_UNDEF",
        0xFFF1: "SHN_ABS",
        0xFF00: "SHN_LOPROC",
        0xFF1F: "SHN_HIPROC",
        0xFF20: "HN_LIVEPATCH",
        0xFFF1: "SHN_ABS",
        0xFFF2: "SHN_COMMON",
        0xFFFF: "SHN_HIRESERVE"
    }

    def __init__(self, st_name="", st_value=0, st_size=0, st_info=0, st_other=0, st_shndx=0):
        super().__init__(
            {
                "st_name": st_name,
                "st_value": st_value,
                "st_size": st_size,
                "st_info": st_info,
                "st_other": st_other,
                "st_shndx": st_shndx
            },
            {
                "st_name": st_name,
                "st_info": st_info,
                "st_other": st_other,
                "st_shndx": st_shndx,
                "st_value": st_value,
                "st_size": st_size,
            }
        )

        self.syminfo = {
            "si_boundto": 0,
            "si_flags": 0
        }

    def get_name_idx(self):
        return self.members["st_name"]

    def get_strtab_idx(self):
        return self.members["st_shndx"]

    def set_resolved_name(self, name):
        self.members["st_name"] = name

    def __str__(self):
        out = ""
        out += utils.formatter2("%-010x", self.members["st_value"])
        out += utils.formatter2("%-10s", self.members["st_size"])
        out += utils.formatter2("%-20s", self.members["st_info"] & Symbol.ST_INFO_BIND_M, table=Symbol.ST_BIND_T)
        out += utils.formatter2("%-20s", self.members["st_info"] & Symbol.ST_INFO_TYPE_M, table=Symbol.ST_TYPE_T)
        out += utils.formatter2("%-20s", self.members["st_other"], table=Symbol.ST_OTHER_T)
        out += utils.formatter2("%-10s", self.members["st_shndx"], table=Symbol.ST_SHNDX_T)
        out += utils.formatter2("%-10s", self.members["st_name"])
        return out