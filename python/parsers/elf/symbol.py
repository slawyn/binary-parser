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
        0xFFF2: "SHN_COMMON",
        0xFFFF: "SHN_HIRESERVE"
    }

    def __init__(self):
        super().__init__(
            {
                "st_name": 4,
                "st_value": 4,
                "st_size": 4,
                "st_info": 1,
                "st_other": 1,
                "st_shndx": 4,
            },
            {
                "st_name": 4,
                "st_info": 1,
                "st_other": 1,
                "st_shndx": 2,
                "st_value": 8,
                "st_size": 8,
            }
        )

        self.syminfo = {
            "si_boundto": 0,
            "si_flags": 0
        }

    def get_name_idx(self):
        return self.get_value("st_name")

    def get_strtab_idx(self):
        return self.get_value("st_shndx")

    def set_resolved_name(self, name):
        self.members["st_name"] = name

    def __str__(self):
        out = ""
        out += utils.formatter2("%-010x", self.get_value("st_value"))
        out += utils.formatter2("%-10s", self.get_value("st_size"))
        out += utils.formatter2("%-20s", self.get_value("st_info") & Symbol.ST_INFO_BIND_M, table=Symbol.ST_BIND_T)
        out += utils.formatter2("%-20s", self.get_value("st_info") & Symbol.ST_INFO_TYPE_M, table=Symbol.ST_TYPE_T)
        out += utils.formatter2("%-20s", self.get_value("st_other"), table=Symbol.ST_OTHER_T)
        out += utils.formatter2("%-10s", self.get_value("st_shndx"), table=Symbol.ST_SHNDX_T)
        out += utils.formatter2("%-10s", self.members["st_name"])
        return out
