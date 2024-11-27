import utils
from packer import Packer

class SectionData:
    '''SectionData
    '''
    def __init__(self, data):
        self.data = data

    def get_size(self):
        '''Get Size
        '''
        return len(self.data)

    def get_data(self):
        '''Get Data
        '''
        return self.data

class SectionHeader(Packer):
    '''Section Header
    '''
    SH_NAME_OFF_SZ = 4
    SH_TYPE_SZ = 4
    SH_FLAGS_SZ = 4
    SH_ADDR_SZ = 4
    SH_OFFSET_SZ = 4
    SH_SIZE_SZ = 4
    SH_LINK_SZ = 4
    SH_INFO_SZ = 4
    SH_ADDRALIGN_SZ = 4
    SH_ENTSIZE_SZ = 4

    SH_NAME_OFF_64SZ = 4
    SH_TYPE_64SZ = 4
    SH_FLAGS_64SZ = 8
    SH_ADDR_64SZ = 8
    SH_OFFSET_64SZ = 8
    SH_SIZE_64SZ = 8
    SH_LINK_64SZ = 4
    SH_INFO_64SZ = 4
    SH_ADDRALIGN_64SZ = 8
    SH_ENTSIZE_64SZ = 8

    SH_TYPE_T = {0x00: "SHT_NULL (Unused)",
                 0x01: "SHT_PROGBITS (Program data)",
                 0x02: "SHT_SYMTAB (Symbol table)",
                 0x03: "SHT_STRTAB (String table)",
                 0x04: "SHT_RELA (Relocation entries with addends)",
                 0x05: "SHT_HASH (Symbol hash table)",
                 0x06: "SHT_DYNAMIC (Dynamic linking inmformation)",
                 0x07: "SHT_NOTE (Notes)",
                 0x08: "SHT_NOBITS (bss)",
                 0x09: "SHT_REL (Relocation entries, no addends)",
                 0x0A: "SHT_SHLIB (Reserved)",
                 0x0B: "SHT_DYNSYM (Dynamic linker symbol table)",
                 0x0E: "SHT_INIT_ARRAY (Array of constructors)",
                 0x0F: "SHT_FINI_ARRAY (Array of destructors)",
                 0x10: "SHT_PREINIT_ARRAY (Array of pre-constructors)",
                 0x11: "SHT_GROUP (Section group)",
                 0x12: "SHT_SYMTAB_SHDX (Extended section indices)",
                 0x13: "SHT_NUM (Number of defined types)",
                 0x60000000: "Start OS-specific"}

    _FLAGS_FULL = {0x01: "SHF_WRITE (Writable)",
                   0x02: "SHF_ALLOC (Occupies memory during execution)",
                   0x04: "SHF_EXECINSTR (Executable)",
                   0x10: "SHF_MERGE (Might be merged)",
                   0x20: "SHF_STRINGS (Null-terminated strings)",
                   0x40: "SHF_INFO_LINK (\'sh_info\' contains SHT index)",
                   0x80: "SHF_LINK_ORDER (Preserved order after combining)",
                   0x100: "SHF_OS_NONCONFORMING (Non-standard OS specific handling required)",
                   0x200: "SHF_GROUP (Section is member of a group)",
                   0x400: "SHF_TLS (Section hold thread-local data)",
                   0x0FF00000: "SHF_MASKOS (OS-specific)",
                   0xF0000000: "SHF_MASKPROC (Processor-specific)",
                   0x800: "SHF_COMPRESSED (Compressed)",
                   0x4000000: "SHF_ORDERED (Special ordering requirement (Solaris))",
                   0x8000000: "SHF_EXCLUDE (Section is excluded unless referenced or allocated (Solaris))"}

    SH_FLAGS_T = {0x01: "SHF_WRITE",
                  0x02: "SHF_ALLOC",
                  0x04: "SHF_EXECINSTR",
                  0x10: "SHF_MERGE",
                  0x20: "SHF_STRINGS",
                  0x40: "SHF_INFO_LINK",
                  0x80: "SHF_LINK_ORDER",
                  0x100: "SHF_OS_NONCONFORMING",
                  0x200: "SHF_GROUP",
                  0x400: "SHF_TLS",
                  0x0FF00000: "SHF_MASKOS",
                  0xF0000000: "SHF_MASKPROC",
                  0x800: "SHF_COMPRESSED",
                  0x4000000: "SHF_ORDERED",
                  0x8000000: "SHF_EXCLUDE"}
    TYPE_SHT_NULL = 0x00
    TYPE_SHT_PROGBITS = 0x01
    TYPE_SHT_SYMTAB = 0x02
    TYPE_SHT_STRTAB = 0x03
    TYPE_SHT_NOBITS = 0x08
    TYPE_SHT_DYNSYM = 0x0B
    TYPE_SHT_DYNAMIC = 0x06
    FLAGS_SHF_ALLOC = 0x02
    FLAGS_SHF_EXECINSTR = 0x04

    def __init__(self, sh_name_off=0, sh_type=0, sh_flags=0, sh_size=0, sh_offset=0, sh_addr=0):
        self.name = ""
        super().__init__(
            {
                "sh_name_off": sh_name_off,
                "sh_type": sh_type,
                "sh_flags": sh_flags,
                "sh_addr": sh_addr,
                "sh_offset": sh_offset,
                "sh_size": sh_size,
                "sh_link": 0,
                "sh_info": 0,
                "sh_addralign": 0,
                "sh_entsize": 0
            },
            {
                "sh_name_off": sh_name_off,
                "sh_type": sh_type,
                "sh_flags": sh_flags,
                "sh_addr": sh_addr,
                "sh_offset": sh_offset,
                "sh_size": sh_size,
                "sh_link": 0,
                "sh_info": 0,
                "sh_addralign": 0,
                "sh_entsize": 0
            }
        )
        self.section_data = None

    def get_size(self):
        return self.members["sh_size"]

    def get_entry_size(self):
        return self.members["sh_entsize"]

    def get_offset(self):
        return self.members["sh_offset"]

    def get_type(self):
        return self.members["sh_type"]

    def get_align(self):
        return self.members["sh_addralign"]

    def get_addr(self):
        return self.members["sh_addr"]

    def get_link(self):
        return self.members["sh_link"]
    
    def is_allocatable(self):
        return self.members["sh_flags"] & SectionHeader.FLAGS_SHF_ALLOC

    def set_offset(self, offset):
        self.members["sh_offset"] = offset

    def get_name_off(self):
        return self.members["sh_name_off"]

    def set_size(self, size):
        self.members["sh_size"] = size

    def resolve_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_section_data(self, section_data):
        self.section_data = section_data

    def get_section_data(self):
        return self.section_data

    def get_column_titles():
        out = ""
        out += utils.formatter2("%-10s", "[Offset]")
        out += utils.formatter2("%-20s", "[File offset]")
        out += utils.formatter2("%-20s", "[File size]")
        out += utils.formatter2("%-20s", "[Physical address]")
        out += utils.formatter2("%-10s", "[Link]")
        out += utils.formatter2("%-10s", "[Info]")
        out += utils.formatter2("%-20s", "[Entry Size]")
        out += utils.formatter2("%-20s", "[Align]")
        out += utils.formatter2("%-30s", "[Type]")
        out += utils.formatter2("%-30s", "[Flags]")
        return out

    def __str__(self):
        out = ""
        out += utils.formatter2("%-10s", self.members["sh_name_off"])
        out += utils.formatter2("%-20x", self.members["sh_offset"])
        out += utils.formatter2("%-20x", self.members["sh_size"])
        out += utils.formatter2("%-20x", self.members["sh_addr"])
        out += utils.formatter2("%-10x", self.members["sh_link"])
        out += utils.formatter2("%-10x", self.members["sh_info"])
        out += utils.formatter2("%-20x", self.members["sh_entsize"])
        out += utils.formatter2("%-20x", self.members["sh_addralign"])
        out += utils.formatter2("%-30s", self.members["sh_type"], table=SectionHeader.SH_TYPE_T)
        out += utils.formatter2("%-30s", self.members["sh_flags"], table=SectionHeader.SH_FLAGS_T, mask=True)
        return out
